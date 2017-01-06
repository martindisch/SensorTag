#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

void humConvert(uint16_t rawTemp, uint16_t rawHum,
                 float *tTemp, float *tHum) {
    *tTemp = ((double) rawTemp / 65536) * 165 - 40;
    *tHum = ((double) rawHum / 65536)*100;
}

int main(int argc, char *argv[]) {
    if (argc != 5) {
        printf("Incorrect arguments. Expected something like 'e0 08 48 0c'.\n");
        return EXIT_FAILURE;
    }
    
    char buf[5];
    strcpy(buf, argv[2]);
    strcat(buf, argv[1]);
    uint16_t rawTemp = strtol(buf, NULL, 16);
    
    strcpy(buf, argv[4]);
    strcat(buf, argv[3]);
    uint16_t rawHum = strtol(buf, NULL, 16);
    
    float temp, hum;
    humConvert(rawTemp, rawHum, &temp, &hum);
    printf("Temperature: %.2f\nHumidity: %.2f\n", temp, hum);
    
    return EXIT_SUCCESS;
}
