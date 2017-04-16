from PIL import Image
import os
import sys
from math import sqrt
from math import floor

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

def getSquaredImages(numberOfImages, size):
    squaredImages = []
    for i in range(numberOfImages):
        squaredImages.append(Image.new("RGB", (size, size)))
    
    return squaredImages
    
def incrementXY(ylim, currentPosition):
    if (currentPosition[1] + 1 >= ylim):
        currentPosition[1] = 0
        currentPosition[0] += 1
    else:
        currentPosition[1] += 1
        
    return

# DP is a system like XY coordinates, except traversing a matrix diagonally
# [D0P0][D1P0][D2P0]
# [D1P1][D2P1][D3P0]
# [D2P2][D3P1][D4P0]
def incrementDP(bounds, currentPosition):
    # Increment P by 1
    if (currentPosition[0] > 0 and currentPosition[1] < bounds[1] - 1):
        currentPosition[0] -= 1
        currentPosition[1] += 1
    # Increment D by 1
    else: #(currentPosition[0] <= 0 or currentPosition[1] >= bounds[1] - 1):
        # Traverse to P = 0 of arbitrary D
        while (currentPosition[0] < bounds[0] - 1 and currentPosition[1] >= 0):
            currentPosition[0] += 1
            currentPosition[1] -= 1
        # Next D is to the right
        if (currentPosition[1] == 0 and currentPosition[0] < bounds[0] - 1):
            currentPosition[0] += 1
        # Next D is below
        else:
            currentPosition[1] += 1
    
    return

# Pixel list, list of bounds[x, y], and position of the pixel to interpolate
def interpolate(pix, bounds, pos):
    # Interpolated pixel
    i = [0,0,0]
    values = 0
    if (pos[0] > 0): i[0] += pix[pos[0] - 1, pos[1]][0]; i[1] += pix[pos[0] - 1, pos[1]][1]; i[2] += pix[pos[0] - 1, pos[1]][2]; values += 1
    if (pos[0] < bounds[0] - 1): i[0] += pix[pos[0] + 1, pos[1]][0]; i[1] += pix[pos[0] + 1, pos[1]][1]; i[2] += pix[pos[0] + 1, pos[1]][2]; values += 1
    
    if (pos[1] > 0): i[0] += pix[pos[0], pos[1] - 1][0]; i[1] += pix[pos[0], pos[1] - 1][1]; i[2] += pix[pos[0], pos[1] - 1][2]; values += 1
    if (pos[1] < bounds[1] - 1): i[0] += pix[pos[0], pos[1] + 1][0]; i[1] += pix[pos[0], pos[1] + 1][1]; i[2] += pix[pos[0], pos[1] + 1][2]; values += 1
    
    for j in range(3):
        i[j] = int(i[j] / values)
    
    return tuple(i)
    
def expand(original, output):
    originalSize = original.size[0] * original.size[1]
    originalPixels = original.load()
    outputSize = output.size[0] * output.size[1]
    outputPixels = output.load()
    
    bytesNeeded = outputSize - originalSize
    try:
        spreadSize = outputSize / bytesNeeded
    except:
        print("Divide by zero error?")
        #input("Press enter to continue...")
        return
    
    print("{} {} {} {}".format(originalSize, outputSize, bytesNeeded, spreadSize))
    currentTick = 0
    origPos = [0, 0]
 
    if (floor(spreadSize) >= 2):
        for x in range(output.size[0]):
            for y in range(output.size[1]):
                if (currentTick % floor(spreadSize) == 0):
                    #outputPixels[x,y] = (0,0,0)
                    outputPixels[x,y] = interpolate(originalPixels, (original.size[0], original.size[1]), (origPos[0], origPos[1]))
                    currentTick += 1
                    #print("Added plack pixel!")
                else:
                    #print(str(origPos[0]) + " " + str(origPos[1]))
                    outputPixels[x,y] = originalPixels[origPos[0], origPos[1]]
                    #incrementXY(original.size[1], origPos)
                    incrementDP([original.size[0], original.size[1]], origPos)
                    currentTick += 1
    else:
        print("Warning, image is too small to accurately interpolate!")
        #input("Press enter to exit...")
    
    return
                

directory = str(sys.argv[1])
fileList = getFileList(directory)
bitmaps = openBitmaps(fileList)
pixelList = getPixelList(bitmaps)
largestBitmap = getLargestSize(bitmaps)
squareSize = sqrt(findSquareContainer(largestBitmap))
outputBMPs = getSquaredImages(len(bitmaps), int(squareSize))

for i in range(len(outputBMPs)):
    expand(bitmaps[i], outputBMPs[i])
    outputBMPs[i].save(fileList[i][0:11] + "[Interpolated]" + fileList[i][11:], 'bmp')
'''
print("The largest bitmap has " + str(largestBitmap) + " pixels, or " + str(largestBitmap * 3) + "B")
print("The smallest image size that can hold this is " + str(squareSize) + "x" + str(squareSize))
print("This image weighs in at " + str(squareSize ** 2) + " pixels, or " + str((squareSize ** 2) * 3) + "B")'''