from PIL import Image
import os
import sys
from math import sqrt

'''
    TODO:
    Figure out how many bytes to add to each image
    Figure out how to interspace holes
    Fill holes
    Save all images
'''

def getLargestSize(bitmaps):
    largest = 0
    for b in bitmaps:
        if (b.size[0] * b.size[1] > largest):
            largest = b.size[0] * b.size[1]
            
    return largest

def openBitmaps(fileList):
    bitmaps = []
    for f in fileList:
        bitmaps.append(Image.open(f))
    
    return bitmaps

def getPixelList(bitmaps):
    pixelList = []
    for b in bitmaps:
        pixelList.append(b.load())
        
    return pixelList

def getFileList(dir):
    files = []
    for (dirpath, dirnames, filenames) in os.walk(dir):
        files.extend(filenames)
        break
    for i in range(len(files)):
        files[i] = dir + "/" + files[i]
        
    return files

def findSquareContainer(num):
    square = 1
    while (square ** 2 < num):
        square += 1
    
    return square ** 2

directory = str(sys.argv[1])
fileList = getFileList(directory)
bitmaps = openBitmaps(fileList)
pixelList = getPixelList(bitmaps)
largestBitmap = getLargestSize(bitmaps)
squareSize = sqrt(findSquareContainer(largestBitmap))

print("The largest bitmap has " + str(largestBitmap) + " pixels, or " + str(largestBitmap * 3) + "B")
print("The smallest image size that can hold this is " + str(squareSize) + "x" + str(squareSize))
print("This image weighs in at " + str(squareSize ** 2) + " pixels, or " + str((squareSize ** 2) * 3) + "B")