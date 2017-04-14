#ifndef BITMAP_H
#define BITMAP_H

#include "pixel.h"

typedef struct BMP
{
    char *header;
    int fileSize, width, height;
    char *payload;
    char *fileName;
    Pixel *pixelArray;
}BMP;

BMP *getBMPClone(BMP *toClone);

BMP *newBMP(char *name, int strings, char **data);

void writeBMP(BMP *bmp);

#endif // BITMAP_H
