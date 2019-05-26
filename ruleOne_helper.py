import os
import time
import csv
import fnmatch
import requests
import numpy as np
from pathlib import Path

#------------------------------------------------------------------
# Calculate the growth rate based on the number of years, initial
# and future results.
# Note:
# If the initial or future results are above the thousand, then a
# comma is inserted to delimit the thousand and needs to be removed.
def getGrowthRate(nper, pv, fv):
    if isinstance(pv, str):
        pv = float(pv.replace(',',''))

    if isinstance(fv, str):
        fv = float(fv.replace(',',''))

    return np.rate(nper-1, 0, -pv, fv)

#------------------------------------------------------------------
def getFutureEPS(growthRateEPS, presentEPS):
    return np.fv(growthRateEPS, 10, 0, -presentEPS)

#------------------------------------------------------------------
def getFutureStockPrice(futureEPS, futurePE):
    return futureEPS * futurePE

#------------------------------------------------------------------
def getStickerPrice(growthRateEPS, presentEPS, futurePE):
    futureEPS = getFutureEPS(growthRateEPS, presentEPS)
    futureStockPrice = getFutureStockPrice(futureEPS, futurePE)
    return np.pv(0.15, 10, 0, -futureStockPrice)

#------------------------------------------------------------------
def getMosPrice(stickerPrice):
    return stickerPrice/2

class ruleOneInvesting:
    # Path for the financial data folder.
    FINANCIAL_DATA_PATH = "."
    
    # Global variables
    financialZoneDir = []
    financialZoneDict = {}
    
    def __init__(self):
        pass
    
    #------------------------------------------------------------------
    def ruleOneCheck(self, stockPath):
        revenues_list  = []
        earnings_list  = []
        bookvalue_list = []
        roic_list      = []
        operating_list = []

        print("stockPath: ", stockPath)

        with open(stockPath) as csvFile:
            csvReader = csv.reader(csvFile, delimiter=',')

        found_earn      = False
        found_rev       = False
        found_book      = False
        found_roic      = False
        found_operating = False

        for row in csvReader:
            if ( ('Revenue ' in row) and (' Mil' in row) ):
                    revenues_list = row[1:]
                    print("revenues_list", revenues_list)
                    found_rev = True
            if ('Earnings Per Share ' in row):
                    earnings_list = row[1:]
                    print("earnings_list", earnings_list)
                    found_earn = True
            if ('Book Value Per Share * ' in row):
                    bookvalue_list = row[1:]
                    print("bookvalue_list", bookvalue_list)
                    found_book = True
            if ('Return on Invested Capital %' in row):
                    roic_list = row[1:]
                    print("roic_list", roic_list)
                    found_roic = True
            if ( ('Operating Cash Flow ' in row) and (' Mil' in row) ):
                    operating_list = row[1:]
                    print("operating_list", operating_list)
                    found_operating = True                        

            if (found_rev and found_earn and found_book and found_operating and found_roic):
                    print("All Values Retrieved")
                    break

    #------------------------------------------------------------------
    def doFinanceAnalysis(self):
        # Fill in the list of financial zone directories.
        self.financialZoneDir = self.listDir(self.FINANCIAL_DATA_PATH)

        # Iterate thru each financial zone directory.
        for fdir in self.financialZoneDir:
            # List all the csv files in the directory.
            self.financialZoneDict[fdir] = self.listFiles(fdir, '*.csv')

        #print("Dictonary: ", self.financialZoneDict)

        # For each stock exchange csv file, create a new folder (if it does not already exist).
        for key in self.financialZoneDict:
            geoZone = key
            stockExchanges = self.financialZoneDict[key]

            # Check if the list of stock exchange is not empty.
            if stockExchanges:
                # List of stock exchange is not empty
                #print("geoZone: ", geoZone)
                print("stockExchanges: ", stockExchanges)
                # Iterate thru the list and create the folders holding the financial
                # data for the stock exchange.
                for stockEx in stockExchanges:
                    # Clear counter 
                    # Retrieve the file name without the extension
                    # to create a folder with the same name.
                    #folderName = os.path.splitext(os.path.basename(csv))[0]
                    stockExfolderName = self.getBaseName(stockEx)
                    #print("stockExfolderName: ", stockExfolderName)

                    # Get the stock name.
                    stockName, discardName = stockExfolderName.split("_", 1)
                    #print("stockName: ", stockName)

                    # Create the folder name.
                    self.createFolder(geoZone, stockExfolderName)

                    # Set the folder full path.
                    #dataDest = getFullPath("\\" + geoZone + "\\" + stockExfolderName)
                    dataDest = self.getFullPath(geoZone + "\\" + stockExfolderName)
                    #print("dataDest: ", dataDest)

                    #print("stockEx: ", stockEx)
                    #print("getFullPath(stockEx): ", getFullPath(geoZone + "\\" + stockEx))

                    # Get the list of stock symbols for the current stock exchange name.
                    stockList = self.getStockListFromStockExchange(self.getFullPath(geoZone + "\\" + stockEx))

                    # Clear counter keeping track of number of files that came back empty.
                    zeroCounter = 0

                    # Get the financial data for all the stock symbols.
                    for stockSymbol in stockList:
                        # Build up the stock file name.
                        fileName = stockName + "_" + stockSymbol + ".csv"

                        # Set the stock path.
                        stockPath = os.path.join(dataDest, fileName)

                        # Get the financial data from pre-records or download it.
                        if(self.getFinancialData(stockPath, stockName, stockSymbol) == True):
                            zeroCounter = zeroCounter + 1
                        else:
                            # Analyze the financial data.
                            pass
                            #ruleOneCheck(stockPath)

                    print("zeroCounter: ", zeroCounter)

        print("DONE RETRIEVING FINANCIAL DATA.")

    #------------------------------------------------------------------

#invest = ruleOneInvesting()
#invest.doFinanceAnalysis()
