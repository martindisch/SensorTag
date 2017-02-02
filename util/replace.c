#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/**
 * Reads CSV data from stdin that is of the form
 *
 * 2017/01/18 15:32:37,-6.09,64.39
 * 2017/01/18 15:33:38,-6.12,64.58
 * ...
 *
 * and in lines where the humidity value (the last one) is 100.00
 * because of faulty measurements, replaces it with the last valid
 * humidity value. The new CSV data is then printed to stdout.
 *
 * Use as follows:
 * ./replace < original.csv > replaced.csv
 *
 */
int main() {
    int size = 300;
    char **lines = calloc(size, sizeof(char *));
    int line = 0, element = 0, character = 0;
    int c;
    lines[0] = calloc(20, sizeof(char));
    while ((c = getchar()) != EOF) {
        switch (c) {
        case ',':
            lines[3*line + element][character] = '\0';
            element++;
            character = 0;
            lines[3*line + element] = calloc(20, sizeof(char));
            break;
        case '\n':
            lines[3*line + element][character] = '\0';
            line++;
            element = 0;
            character = 0;
            if (size == 3*line) {
                size *= 2;
                char **newp = realloc(lines, size * sizeof(char *));
                if (newp) lines = newp;
                else printf("Error reallocating memory\n");
            }
            lines[3*line + element] = calloc(20, sizeof(char));
            break;
        default:
            lines[3*line + element][character++] = c;
            break;
        }
    }
    
    int l;
    char lastHum[20];
    strcpy(lastHum, "50.00");
    for (l = 0; l < line; l++) {
        if (strcmp(lines[3*l + 2], "100.00") == 0) strcpy(lines[3*l + 2], lastHum);
        else strcpy(lastHum, lines[3*l + 2]);
        printf("%s,%s,%s\n", lines[3*l], lines[3*l + 1], lines[3*l + 2]);
        free(lines[3*l]);
        free(lines[3*l + 1]);
        free(lines[3*l + 2]);
    }
    free(lines[3*line + element]);
    free(lines);
    return 0;
}
