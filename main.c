#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>

#include "tinydir.h"
#include "bitmap.h"
#include "pixel.h"
#include "constants.h"

typedef struct FileList
{
    char **file;
    int numberOfFiles;
}FileList;

void loadingBar(int min, int max, int current, char *message)
{
    int i, spaces = 10;
    static int ticksToPrint = -1;

    if (ticksToPrint != (int)((double)(current + 1) / abs(max - min) * 10))
    {
        CLS;

        ticksToPrint = (int)((double)(current + 1) / abs(max - min) * 10);
        printf("%s\n", message);
        printf("[");

        for (i = 0; i < ticksToPrint; i++)
        {
            printf("=");
            spaces--;
        }

        for (i = 0; i < spaces; i++)
        {
            printf(" ");
        }

        printf("]\n");
    }
}

FileList *getListOfFiles()
{
    tinydir_dir dir;
    FileList *files = calloc(1, sizeof(FileList));
    int i;

    tinydir_open(&dir, "input");


    files->file = calloc(MAX_FILES, sizeof(char*));
    for (i = 0; i < MAX_FILES; i++)
    {
        files->file[i] = calloc(MAX_NAME_SIZE, 1);
    }

    while (dir.has_next)
    {
        tinydir_file file;
        tinydir_readfile(&dir, &file);
        printf("Found: %s\n", file.name);

        strcpy(files->file[files->numberOfFiles], "input/");
        strcat(files->file[files->numberOfFiles], file.name);
        files->numberOfFiles++;

        tinydir_next(&dir);
    }

    printf("\n===============\n\n");

    tinydir_close(&dir);

    return files;
}

void getLargestFactors(int *f1, int *f2, int number)
{
    int best1 = 0, best2 = 0, smallestDifference = -1;

    printf("Finding bitmap dimensions...\n");
    for (*f1 = 1; *f1 <= number; *f1 += 1)
    {
        for (*f2 = 1; *f2 <= number; *f2 += 1)
        {
            //loadingBar(0, (number + 1) * (number + 1), (*f1 * number) + *f2, "Finding bitmap dimensions...");


            // No need to continue
            if (*f1 * *f2 > number)
                break;

            if (*f1 * *f2 == number)
            {
                if (smallestDifference == -1)
                {
                    best1 = *f1;
                    best2 = *f2;
                    smallestDifference = abs(best1 - best2);
                }
                else if (abs(*f1 - *f2) < smallestDifference)
                {
                    best1 = *f1;
                    best2 = *f2;
                    smallestDifference = abs(best1 - best2);
                }
            }

        }
    }

    *f1 = best1;
    *f2 = best2;

    return;
}

char *loadInputFile(char *fileName)
{
    FILE *input = NULL;
    char *fileContents = NULL;
    int fileSize;

    input = fopen(fileName, "rb");

    if (input)
    {
        fseek(input, 0, SEEK_END);
        fileSize = ftell(input);
        fseek(input, 0, SEEK_SET);

        fileContents = calloc(fileSize + 1, sizeof(char));
        fread(fileContents, sizeof(char), fileSize, input);
        fclose(input);
    }
    else
    {
        printf("Error loading input!\n\n");
    }

    return fileContents;
}

void rebuildPayloadFromPixelArray(BMP *bmp)
{
    int i, length = bmp->height * bmp->width * 3;

    for (i = 0; i < length; i++)
    {
        loadingBar(0, length, i, "Rebuilding payload...");
        bmp->payload[i] = bmp->pixelArray[i / 3].color[i % 3];
    }

    return;
}

BMP *createSpectrograph(BMP *original)
{
    BMP *spectrograph = getBMPClone(original);
    int i,
        //pixels = strlen(spectrograph->payload) / 3;
        pixels = original->width * original->height;

    swapPixels(spectrograph->pixelArray, 0,
                findClosestPixelPosition(newPixel(255, 0, 0), spectrograph->pixelArray, 0, pixels));

    for (i = 1; i < pixels; i++)
    {
        loadingBar(0, pixels, i, "Creating spectrograph...");
        swapPixels(spectrograph->pixelArray, i,
                   findClosestPixelPosition(spectrograph->pixelArray[i - 1], spectrograph->pixelArray, i, pixels));
    }

    spectrograph->fileName = realloc(spectrograph->fileName, 100);

    if (!spectrograph->fileName)
        printf("Error\n");

    char *tmp = calloc(strlen(spectrograph->fileName) + 1, 1);
    strcpy(tmp, spectrograph->fileName);
    strcpy(spectrograph->fileName, "SPEC ");
    strcat(spectrograph->fileName, tmp);
    free(tmp);

    return spectrograph;
}

void analyzeBMP(BMP *original)
{
    BMP *spectrograph = createSpectrograph(original);
    rebuildPayloadFromPixelArray(spectrograph);

    writeBMP(spectrograph);

    return;
}

int main(int argc, char **argv)
{
    time_t  startTime = time(NULL),
            currentLoopTime = 0,
            runningTime = 0;
    if (argc < 2)
    {
        printf("Usage:\n\n");
        printf("bmpEncoder [output file] [string-to-encode]\n");
        printf("bmpEncoder [input file]\n");
        printf("Examples:\nbmpEncoder output.bmp Hello, everyone!\n");
        printf("bmpEncoder someRandomBook.txt\n\n");
    }
    else if (argc == 2)
    {
        if (!strcmp(argv[1], "INPUT"))
        {
            FileList *files = getListOfFiles();

            for (files->numberOfFiles; files->numberOfFiles > 2; files->numberOfFiles--)
            {
                currentLoopTime = time(NULL);
                printf("Processing %s...\n", files->file[files->numberOfFiles - 1]);
                char *file = loadInputFile(files->file[files->numberOfFiles - 1]);

                // I'm sorry for this
                char **argvSim = malloc(sizeof(char*) * 3);
                argvSim[2] = file;

                BMP *bmp = newBMP(strcat(files->file[files->numberOfFiles - 1], ".bmp"), 3, argvSim);
                writeBMP(bmp);

                char command[255];
                memset(command, 0, 255);
                strcpy(command, "makeSpectrograph.py ");
                strcat(command, bmp->fileName);
                strcat(command, " /l diagonal");
                system(command);

                currentLoopTime = time(NULL);
                printf("Done in %is\n\n", currentLoopTime - runningTime - startTime);
                runningTime += currentLoopTime - runningTime - startTime;
            }
        }
        else
        {
            char *file = loadInputFile(argv[1]);
            // I'm sorry for this
            char **argvSim = malloc(sizeof(char*) * 3);
            argvSim[2] = file;

            BMP *bmp = newBMP(strcat(argv[1], ".bmp"), 3, argvSim);
            writeBMP(bmp);

            char command[255];
            memset(command, 0, 255);
            strcpy(command, "makeSpectrograph.py ");
            strcat(command, bmp->fileName);
            system(command);
            //analyzeBMP(bmp);
        }

    }
    else
    {
        BMP *bmp = newBMP(argv[1], argc, argv);
        writeBMP(bmp);

        char command[255];
        memset(command, 0, 255);
        strcpy(command, "makeSpectrograph.py ");
        strcat(command, bmp->fileName);
        system(command);
        //analyzeBMP(bmp);
    }

    printf("Total time: %is\n", time(NULL) - startTime);

    system("pause");
    return 0;
}
