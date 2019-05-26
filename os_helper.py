import os
import fnmatch
from pathlib import Path

#------------------------------------------------------------------
# Path related helper functions.
#------------------------------------------------------------------

#------------------------------------------------------------------
# Get full path
def getFullPath(name):
    return (str(Path().absolute()) + "\\" + name)

#------------------------------------------------------------------
# Set full path
def setFullPath(folderPath, fileName):
    return (os.path.join(folderPath, fileName))

#------------------------------------------------------------------
# Get the file name without the extension.
def getFileBaseName(fileName):
    return (os.path.splitext(os.path.basename(fileName))[0])



#------------------------------------------------------------------
# Folder related helper functions.
#------------------------------------------------------------------

#------------------------------------------------------------------
# List directory names not starting with '.' based on path.
def listDir(dirPath, filter):
    dir_list = []
    for entry in os.scandir(dirPath):
        if not entry.name.startswith(filter) and entry.is_dir():
            dir_list.append(entry.name)

    return dir_list

#------------------------------------------------------------------
# Create folder
def createFolder(dirPath):
    if not os.path.exists(dirPath):
        os.makedirs(dirPath)

#------------------------------------------------------------------
# Create sub folder
def createSubFolder(rootDir, newDir):
    newDir = rootDir + "\\" + newDir

    if not os.path.exists(newDir):
        os.makedirs(newDir)
        print("createSubFolder:", newDir)

    return newDir

#------------------------------------------------------------------
# List files in directory
def getFileList(dirPath, filter):
    fileList = fnmatch.filter(os.listdir(dirPath), filter)
    #print("fileList: ", fileList)
    return fileList

#------------------------------------------------------------------
# Get full path
def getFolderPath(filePath):
    return (os.path.dirname(filePath))

#------------------------------------------------------------------
# File related helper functions.
#------------------------------------------------------------------

#------------------------------------------------------------------
# Check if the file already exist.
def checkFileExists(filePath):
    return os.path.exists(filePath)

#------------------------------------------------------------------
def getFileSize(filePath):
    return os.stat(filePath).st_size

#------------------------------------------------------------------
def removeFile(filePath):
    if checkFileExists(filePath):
        os.remove(filePath)
