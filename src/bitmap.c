#include <stdio.h>

#include "bitmap.h"
#include "constants.h"

BMP *getBMPClone(BMP *toClone)
{
    BMP *clone = calloc(1, sizeof(BMP));
    int i;

    clone->fileName = calloc(strlen(toClone->fileName) + 1, 1);
    clone->header = calloc(HEADER_SIZE + 1, 1);
    clone->payload = calloc(toClone->fileSize - HEADER_SIZE + 1, 1);

    strcpy(clone->fileName, toClone->fileName);
    for (i = 0; i < HEADER_SIZE; i++)
        clone->header[i] = toClone->header[i];
    for (i = 0; i < toClone->fileSize - HEADER_SIZE; i++)
        clone->payload[i] = toClone->payload[i];

    clone->pixelArray = getPixelArrayClone(toClone->pixelArray, strlen(toClone->payload) / 3);

    clone->fileSize = toClone->fileSize;
    clone->height = toClone->height;
    clone->width = toClone->width;

    return clone;
}

BMP *newBMP(char *name, int strings, char **data)
{
    BMP *bmp = calloc(1, sizeof(BMP));
    char defaultHeader[] = {HEADER};
    int i,j, numberOfPixels, runningPosition = 0;

    bmp->fileName = calloc(strlen(name) + 1, sizeof(char));
    strcpy(bmp->fileName, name);

    bmp->header = calloc(HEADER_SIZE, sizeof(char));
    for (i = 0; i < HEADER_SIZE; i++)
        bmp->header[i] = defaultHeader[i];

    for (i = strings - 1; i >= 2; i--)
    {
        bmp->fileSize += strlen(data[i]);
    }

    // Spaces
    bmp->fileSize += strings - 3;
    char *dataString = calloc(bmp->fileSize, sizeof(char));

    for (i = 2; i < strings; i++)
    {
        strcat(dataString, data[i]);
        if (i + 1 < strings)
            strcat(dataString, " ");
    }

    bmp->pixelArray = createPixelArray(dataString, &numberOfPixels);

    getLargestFactors(&bmp->width, &bmp->height, numberOfPixels);

    bmp->payload = calloc(numberOfPixels * 3, sizeof(char));

    printf("Preparing pixel array...\n");
    for (i = 0; i < numberOfPixels; i++)
    {
        //printf("%i\n", runningPosition);
        for (j = 0; j < 3; j++)
        {
            //loadingBar(0, numberOfPixels * 3, runningPosition, "Preparing pixel array...");
            bmp->payload[runningPosition++] = bmp->pixelArray[i].color[j];
        }

        /*
        if ((i + 1) % 2 == 0)
        {
            //printf("%i +2\n", runningPosition);
            bmp->payload[runningPosition++] = 0;
            bmp->payload[runningPosition++] = 0;
        }
        */
    }
    bmp->payload = realloc(bmp->payload, runningPosition + runningPosition / 3);
    bmp->fileSize = runningPosition + HEADER_SIZE + runningPosition / 3;
    //printf("FS: %i\n", runningPosition);

    //printf("%s\n", bmp->payload);
    return bmp;
}

void writeBMP(BMP *bmp)
{
    FILE *output = NULL;

    output = fopen(bmp->fileName, "wb");

    if (output)
    {
        fwrite(bmp->header, sizeof(char), HEADER_SIZE, output);
        int tmp = SEEK_CUR;

        fseek(output, 2, SEEK_SET);
        fwrite(&bmp->fileSize, sizeof(int), 1, output);

        fseek(output, 18, SEEK_SET);
        fwrite(&bmp->width, sizeof(int), 1, output);

        fseek(output, 22, SEEK_SET);
        fwrite(&bmp->height, sizeof(int), 1, output);

        fseek(output, HEADER_SIZE, SEEK_SET);

        fwrite(bmp->payload, sizeof(char), bmp->fileSize - HEADER_SIZE, output);

        fclose(output);
    }
    else
    {
        printf("Error writing to %s\n", bmp->fileName);
    }

    return;
}
