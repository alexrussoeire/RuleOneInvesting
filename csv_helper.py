import csv

#------------------------------------------------------------------
# CSV related helper functions.
#------------------------------------------------------------------

#------------------------------------------------------------------
# Save a list to file
def saveListToFile(file, List):
    with open(file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')

        for element in List:
            writer.writerow([element])

#------------------------------------------------------------------
# Get list from file
def getListFromFile(file):
    List = []

    with open(file) as csvFile:
        csvReader = csv.reader(csvFile, delimiter=',')

        for row in csvReader:
            List.append(row)

    return List
