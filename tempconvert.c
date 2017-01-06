#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

void tempConvert(uint16_t rawObjTemp, uint16_t rawAmbTemp,
                 float *tObj, float *tAmb) {
    const float SCALE_LSB = 0.03125;
    float t;
    
    t = rawObjTemp >> 2;
    *tObj = t * SCALE_LSB;
    
    t = rawAmbTemp >> 2;
    *tAmb = t* SCALE_LSB;
}

int main(int argc, char *argv[]) {
    if (argc != 5) {
        printf("Incorrect arguments. Expected something like 'e0 08 48 0c'.\n");
        return EXIT_FAILURE;
    }
    
    char buf[5];
    strcpy(buf, argv[2]);
    strcat(buf, argv[1]);
    uint16_t rawObjTemp = strtol(buf, NULL, 16);
    
    strcpy(buf, argv[4]);
    strcat(buf, argv[3]);
    uint16_t rawAmbTemp = strtol(buf, NULL, 16);
    
    float obj, amb;
    tempConvert(rawObjTemp, rawAmbTemp, &obj, &amb);
    printf("Object: %.1f\nAmbient: %.1f\n", obj, amb);
    
    return EXIT_SUCCESS;
}
