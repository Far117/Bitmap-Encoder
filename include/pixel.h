#ifndef PIXEL_H
#define PIXEL_H

typedef struct Pixel
{
    char color[3];
}Pixel;

Pixel *createPixelArray(char *data, int *pixels);

int findClosestPixelPosition(Pixel target, Pixel *pixelArray, int lowerBound, int pixels);

Pixel *getPixelArrayClone(Pixel *toClone, int pixels);

Pixel newPixel(char r, char g, char b);

double pixelSimilarity(Pixel first, Pixel second);

void swapPixels(Pixel *pixelArray, int first, int second);

#endif // PIXEL_H
