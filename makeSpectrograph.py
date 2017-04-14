from PIL import Image
import os
import sys
import time
import operator
import math

'''
Usage: makeSpectrograph.py [input] [options]

Options [default in brackets]:
/a :    Algorithm type.    [line]/stack
/l :    Layout.            [bar]/diagonal
/s :    Colorspace.        [lab]/xyz/rgb
/c :    Seed color.        [white]/red/green/blue/black/gray
'''

def loadingBar(lowerBounds, upperBounds, current, message):
    
    if (loadingBar.ticksToPrint != int(float(current + 1) / abs(upperBounds - lowerBounds) * 10)):
        os.system('cls' if os.name == 'nt' else 'clear')

        spaces = 10
        loadingBar.ticksToPrint = int(float(current + 1) / abs(upperBounds - lowerBounds) * 10)
        print(message + "\n[", end = '')

        for i in range(loadingBar.ticksToPrint):
            print("=", end = '')
            spaces -= 1
        for i in range(spaces):
            print(" ", end = '')
        print("]")

    return
    
def DPToXY(dp, bounds):
    xy = [0, 0]
    

def RGBToXYX(pixel):
    rgb = [0.0, 0.0, 0.0]
    xyz = [0.0, 0.0, 0.0]
    
    for i in range(3):
        rgb[i] = pixel[i] / 255
        
        if (rgb[i] > 0.04045):
            rgb[i] = ((rgb[i] + 0.055) / 1.055) ** 2.4
        else:
            rgb[i] = rgb[i] / 12.92
        
        rgb[i] *= 100
        
    xyz[0] = rgb[0] * 0.4124 + rgb[1] * 0.3576 + rgb[2] * 0.1805
    xyz[1] = rgb[0] * 0.2126 + rgb[1] * 0.7152 + rgb[2] * 0.0722
    xyz[2] = rgb[0] * 0.0193 + rgb[1] * 0.1192 + rgb[2] * 0.9505
    
    return xyz

def XYZToLAB(xyz):
    lab = [0.0, 0.0, 0.0]
    
    for i in range(3):
        xyz[i] /= 100
        
        if (xyz[i] > 0.008856):
            xyz[i] = xyz[i] ** (1/3)
        else:
            xyz[i] = (7.787 * xyz[i]) + (16 / 116)

    lab[0] = (116 * xyz[1]) - 16
    lab[1] = 500 * (xyz[0] - xyz[1])
    lab[2] = 200 * ( xyz[1] - xyz[2])
    
    return lab

def getSimilarity(pix1, pix2, colorspace):
    '''
    similarity = 0
    
    for i in range(0, 3):
        similarity += abs(pix1[i] - pix2[i])

    #print("Similarity: " + str(similarity))
    return similarity
    '''
    set1 = pix1
    set2 = pix2
    if (colorspace == "xyz" or colorspace == "lab"):
        #print("Converted to xyz")
        set1 = RGBToXYX(set1)
        set2 = RGBToXYX(set2)
    if (colorspace == "lab"):
        #print("converted to lab")
        set1 = XYZToLAB(set1)
        set2 = XYZToLAB(set2)
    
    return math.sqrt(((set1[0] - set2[0]) ** 2) + ((set1[1] - set2[1]) ** 2) + ((set1[2] - set2[2]) ** 2))

def findClosestPixel(img, pixelArray, target, targetPosition):
    bestMatch = [0, 0]
    bestScore = 1000
    currentScore = 0

    for x in range(targetPosition[0] + 1, img.size[0]):
        for y in range(targetPosition[1] +1, img.size[1]):
            
            currentScore = getSimilarity(target, pixelArray[x,y])
                                         
            if (currentScore < bestScore):
                print(str(bestScore))
                bestScore = currentScore
                bestMatch[0] = x
                bestMatch[1] = y

    return bestMatch

def shakeList(img, pixelArray, options):
    
    print("Scanning pixels...")
    
    layout = options[1]
    algorithm = options[0]
    seedColor = options[3]
    
    x = 0
    y = 0
    scores = []
    stackLayers = []
    
    if (algorithm == "line"):
    
        for x in range(img.size[0]):
            for y in range(img.size[1]):
                scores.append([pixelArray[x, y], getSimilarity(seedColor, pixelArray[x, y], options[2])])
                
    elif (algorithm == "stack"):
        for y in range(img.size[1]):
            for x in range(img.size[0]):
                if (y == 0):
                    scores.append([pixelArray[x, y], getSimilarity(seedColor, pixelArray[x, y], options[2])])
                else:
                    scores.append([pixelArray[x, y], getSimilarity(stackLayers[y - 1][0][0], pixelArray[x, y], options[2])])
            
            stackLayers.append(sorted(scores, key = operator.itemgetter(1)))
            scores = []
    
    sortedValues = sorted(scores, key = operator.itemgetter(1))
    #print(",".join(map(str, sortedValues)))
    
    if (layout == "bar"):
        if (algorithm == "line"):
            for x in range(img.size[0]):
                for y in range(img.size[1]):
                    #print(str(x) + " " + str(y) + " : " + str(x * img.size[1] + y))
                    pixelArray[x, y] = sortedValues[x * img.size[1] + y][0]
                    
        elif (algorithm == "stack"):
            for y in range(img.size[1]):
                for x in range(img.size[0]):
                    pixelArray[x, y] = stackLayers[y][x][0]
                    
    elif (layout == "diagonal"):
    
        i = 0
        j = 0
        dx = 0
        dy = 0
        counter = 0
        for d in range((img.size[0] - 1) + (img.size[1]) - 1):
            i = dx
            j = dy
            while (i >= 0 and j < img.size[1]):
                pixelArray[i, j] = sortedValues[counter][0]
                counter += 1
                i -= 1
                j += 1
            
            if (dx < img.size[0] - 1):
                dx += 1
            elif (dy < img.size[1] - 1):
                dy += 1
   
    return

def swapPixels(pixelArray, pixPos1, pixPos2):
    pixel = pixelArray[pixPos1[0], pixPos1[1]]
    #pixelArray[pixPos1[0], pixPos1[1]], pixelArray[pixPos2[0], pixPos2[1]] = pixelArray[pixPos2[0], pixPos2[1]], pixelArray[pixPos1[0], pixPos1[1]]
    pixelArray[pixPos1[0], pixPos1[1]] = pixelArray[pixPos2[0], pixPos2[1]]
    pixelArray[pixPos2[0], pixPos2[1]] = pixel
    
    #print("Swapped " + " ".join(map(str, pixPos1)) + " with " + " ".join(map(str, pixPos2)))
    
    return

def parseInput(argv):
    options = ["line", "diagonal", "lab", [255, 255, 255]]
    colors = {"white":[255,255,255], "red":[255,0,0], "green":[0,255,0], "blue":[0,0,255], "black":[0,0,0], "gray":[128,128,128]}
    
    for i in range(len(argv)):

        if (argv[i].lower() == "/a"):
            options[0] = argv[i + 1].lower()
        elif (argv[i].lower() == "/l"):
            options[1] = argv[i + 1].lower()
        elif (argv[i].lower() == "/s"):
            options[2] = argv[i + 1].lower()
        elif (argv[i].lower() == "/c"):
            options[3] = colors[argv[i + 1].lower()]
    
    return options

def getTags(options):
    tag = ""
    potentialTags = {"lab":"[ShakeLAB]", "xyz":"[ShakeXYZ]", "rgb":"[ShakeRGB]", "line":"[Line]", "bar":"[Bar]", "stack":"[Stack]", "diagonal":"[Diagonal]", (255,255,255):"[White]", (255,0,0):"[Red]", (0,255,0):"[Green]", (0,0,255):"[Blue]", (0,0,0):"[Black]", (128,128,128):"[Gray]"}
    
    for i in range(4):
        if (i < 3):
            tag = tag + potentialTags[options[i]]
        else:
            tag = tag + potentialTags[tuple(options[i])]
    
    tag = tag + " "
    return tag
    
    

loadingBar.ticksToPrint = -1
img = Image.open(str(sys.argv[1]))

options = parseInput(sys.argv)

startTime = time.time()
shakeList(img, img.load(), options)
test2End = time.time() - startTime

#print(str(test2End) + "s elapsed")

if "input" in str(sys.argv[1]):
    img.save(str(sys.argv[1][0:6]) + getTags(options) + str(sys.argv[1][6:]), 'bmp')
else:
    img.save(getTags(options) + str(sys.argv[1][6:]), 'bmp')