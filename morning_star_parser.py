import csv
import requests
import numpy as np
import pandas as pd
import os_helper as osh
import csv_helper as csvh

#------------------------------------------------------------------
# 
def saveFinancialData(rawStockPath, stockName, stockSymbol):
    startUrl = "http://financials.morningstar.com/finan/ajax/exportKR2CSV.html?&callback=?&t="
    midUrl = ":"
    endUrl = "&region=usa&culture=en-US&cur=&order=asc"

    # Build up the URL to download the financial data from.
    url = str(startUrl) + str(stockName) + midUrl + str(stockSymbol) + str(endUrl)

    #print("URL: ", url)
       
    # Build up the referer to download the financial data.
    startRef = "http://financials.morningstar.com/balance-sheet/bs.html?t="
    endRef = "&region=usa&culture=en-US"
    ref = str(startRef) + str(stockSymbol) + str(endRef)
    #print("referer", ref)
    
    #response = requests.get(url)
    response = requests.get(url, headers={'referer': ref})
    with open(rawStockPath, 'wb') as f:
        f.write(response.content)

#------------------------------------------------------------------
# 
def trimFinancialData(rawStockPath, trimStockPath, stockName, stockSymbol):
    month_list        = []
    revenues_list     = []
    earnings_list     = []
    bookvalue_list    = []
    roic_list         = []
    freeCashFlow_list = []

    with open(rawStockPath) as csvFile:
        csvReader = csv.reader(csvFile, delimiter=',')

        for row in csvReader:
            # Only process non-void lines.
            if (len(row)):
                # Save the name of the key ratio.
                label = row[0]

                if ( ('Revenue ' in label) and (' Mil' in label) ):
                        revenues_list = row[1:]
                        revenues_list.insert(0, "SALES")
                        #print("revenues_list", revenues_list)
                if ('Earnings Per Share ' in label):
                        earnings_list = row[1:]
                        earnings_list.insert(0, "EPS")
                        #print("earnings_list", earnings_list)
                if ('Book Value Per Share * ' in label):
                        bookvalue_list = row[1:]
                        bookvalue_list.insert(0, "BVPS")
                        #print("bookvalue_list", bookvalue_list)
                if ('Return on Invested Capital %' in label):
                        roic_list = row[1:]
                        roic_list.insert(0, "ROIC")
                        #print("roic_list", roic_list)
                if ( ('Free Cash Flow ' in label) and (' Mil' in label) ):
                        freeCashFlow_list = row[1:]
                        freeCashFlow_list.insert(0, "FCF")
                        #print("freeCashFlow_list", freeCashFlow_list)
                # Using the line "Cash Flow Ratios" to extract the year labels.
                if ('Cash Flow Ratios' in label):
                    new_month_list = []
                    month_list = row[1:]
                    for month in month_list[:-1]:
                        new_month_list.append(int(month[0:4]))
                    new_month_list.append(new_month_list[-1] + 1)
                    month_list = new_month_list
                    month_list.insert(0, "KEY RATIO")
                    #print("month_list", month_list)
                    month_list = [str(i) for i in month_list]
                    #print("month_list", month_list)

    frameList = [roic_list, revenues_list, earnings_list, bookvalue_list, freeCashFlow_list]
    df = pd.DataFrame(frameList, index = [0,1,2,3,4], columns = month_list)
    #print(df)

    df.to_csv(trimStockPath)

#------------------------------------------------------------------
# Get the list of stock in the selected stock exchange.
def getStockListFromStockExchange(stockListPath):
    stockList = []

    with open(stockListPath) as csvFile:
        csvReader = csv.reader(csvFile, delimiter=',')
        lineCount = 0
        for row in csvReader:
            stockName = row[0]

            if ("^" not in stockName) and ("." not in stockName):
                stockList.append(stockName)
            else:
                pass
                #print("Stock ^ name:", stockName)

    #print("StockList: ", stockList)
    return stockList

#------------------------------------------------------------------
def getFinancialData(rawStockPath, stockName, stockSymbol):
    # Flag keeping track if a file was created but with size zero.
    sizeZero = False

    # Check if the raw financial data already exist.
    if not osh.checkFileExists(rawStockPath):
        #print("Financial File Does Not Exist.")
        # Financial file does not exist, download it.
        saveFinancialData(rawStockPath, stockName, stockSymbol)
        #print("Financial data does not exist.")

    # Delete the file if the file is empty.
    if (osh.getFileSize(rawStockPath) == 0):
        #print("Financial File Size is Zero.")
        # Delete empty files.
        osh.removeFile(rawStockPath)
        sizeZero = True

    return sizeZero

#------------------------------------------------------------------
def ruleOnefilter(rawStockPath, trimStockPath, stockName, stockSymbol):
    # Flag keeping track if a file with missing data.
#    missingData = False

    # Check if the trimmed financial data already exist.
    if not osh.checkFileExists(trimStockPath):
        # Trim the financial data.
        trimFinancialData(rawStockPath, trimStockPath, stockName, stockSymbol)

'''
    # Delete the file if the file is empty.
    if (osh.getFileSize(trimStockPath) == 0):
        #print("Financial File Size is Zero.")
        # Delete empty files.
        osh.removeFile(trimStockPath)
        missingData = True
'''

#------------------------------------------------------------------
# Morning Star Parser Class
class morningStarParser:
  
    # Global variables
    financialZoneDir = []
    financialZoneDict = {}
    
    def __init__(self):
        pass

    #------------------------------------------------------------------
    def doFinanceAnalysis(self, stockListPath):

        # Clear counter keeping track of number of files that came back empty.
        zeroCounter = 0

        recordFoundStockList = []
        notFoundStockList    = []

        #print("stockListPath: ", stockListPath)

        baseFolderPath = osh.getFolderPath(stockListPath)
        #print("baseFolderPath: ", baseFolderPath)

        # Set the file name and path holding the list of symbols not found.
        stockNotFoundPath = osh.setFullPath(baseFolderPath, osh.getFileBaseName(stockListPath) + "_NOT_FOUND" + ".csv")

        # Declare both raw and sorted folder name
        rawFolderPath = osh.createSubFolder(baseFolderPath, "Raw_Data")
        trimFolderPath = osh.createSubFolder(baseFolderPath, "Trim_Data")

        # Get the list of stock symbols for the current stock exchange name.
        stockList = getStockListFromStockExchange(stockListPath)
        #print("stockList: ", stockList)

        stockExfolderName = osh.getFileBaseName(stockListPath)
        #print("stockExfolderName: ", stockExfolderName)

        # Get the stock name.
        stockName, stockSymbol = stockExfolderName.split("_", 1)
        #print("stockName:   ", stockName)
        #print("stockSymbol: ", stockSymbol)

        # Create the destination folder (if it does not already exist).
        osh.createFolder(rawFolderPath)

        # Get the financial data for all the stock symbols.
        for stockSymbol in stockList:
            print("stockSymbol: ", stockSymbol)

            # Build up the stock file name.
            fileName = stockName + "_" + stockSymbol + ".csv"
            #print("fileName: ", fileName)

            # Set the raw stock path.
            rawStockPath = osh.setFullPath(rawFolderPath, fileName)
            #print("rawStockPath: ", rawStockPath)

            # Get the financial data from pre-records or download it.
            if(getFinancialData(rawStockPath, stockName, stockSymbol) == True):
                notFoundStockList.append(stockSymbol)
                zeroCounter = zeroCounter + 1
            else:
                recordFoundStockList.append(stockSymbol)
                # Filter out the relevant financial data used for the rule #1 investing.

                # Set the trimmed stock path.
                trimStockPath = osh.setFullPath(trimFolderPath, fileName)
                #print("trimStockPath: ", trimStockPath)

                ruleOnefilter(rawStockPath, trimStockPath, stockName, stockSymbol)

        #print("recordFoundStockList", recordFoundStockList)
        #print("notFoundStockList", notFoundStockList)

        # Save the list of stock that could not be found.
        csvh.saveListToFile(stockNotFoundPath, notFoundStockList)

        # Overwrite the stock list after removing stock symbol that could not
        # be found.
        csvh.saveListToFile(stockListPath, recordFoundStockList)

        print("DONE RETRIEVING FINANCIAL DATA.")

