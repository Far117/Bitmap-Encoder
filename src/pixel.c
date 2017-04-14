#include "pixel.h"

Pixel *createPixelArray(char *data, int *pixels)
{
    int i, length = strlen(data);
    *pixels = (length / 3) + (length % 3);
    Pixel *pixelArray = calloc(*pixels, sizeof(Pixel));

    printf("Initializing pixels...\n");
    for (i = 0; i < length; i++)
    {
        //loadingBar(0, length, i, "Initializing pixels...");
        pixelArray[i / 3].color[i % 3] = data[i];
    }

    return pixelArray;
}

int findClosestPixelPosition(Pixel target, Pixel *pixelArray, int lowerBound, int pixels)
{
    int i;
    double closestValue = 1000, currentSimilarity = 0;
    int closestPosition;

    for (i = lowerBound + 1; i < pixels; i++)
    {
        currentSimilarity = pixelSimilarity(target, pixelArray[i]);

        if (currentSimilarity < closestValue)
        {
            closestValue = currentSimilarity;
            closestPosition = i;
        }
    }

    return closestPosition;
}

Pixel *getPixelArrayClone(Pixel *toClone, int pixels)
{
    int i, j;
    Pixel *clone = malloc(pixels * sizeof(Pixel));

    for (i = 0; i < pixels; i++)
    {
        for (j = 0; j < 3; j++)
            clone[i].color[j] = toClone[i].color[j];
    }

    return clone;
}

Pixel newPixel(char r, char g, char b)
{
    Pixel pix;

    pix.color[0] = r;
    pix.color[1] = g;
    pix.color[2] = b;

    return pix;
}

double pixelSimilarity(Pixel first, Pixel second)
{
    double similarity = 0;
    int i;

    for (i = 0; i < 3; i++)
    {
        similarity += abs(first.color[i] - second.color[i]);
    }

    return similarity;
}

void swapPixels(Pixel *pixelArray, int first, int second)
{
    char tmpColors[3] = {pixelArray[first].color[0],
                            pixelArray[first].color[1],
                            pixelArray[first].color[2]};
    int i;

    for (i = 0; i < 3; i++)
    {
        pixelArray[first].color[i] = pixelArray[second].color[i];
        pixelArray[second].color[i] = tmpColors[i];

        printf("Swapped %c%c%c with %c%c%c\n", pixelArray[second].color[0],
                                                pixelArray[second].color[1],
                                                pixelArray[second].color[2],
                                                tmpColors[0],
                                                tmpColors[1],
                                                tmpColors[2]);
        system("pause");
    }

    return;
}
