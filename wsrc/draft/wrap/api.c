#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <sys/ioctl.h>

static const int ARR_SIZE = 100;

char* hello(char * what)
{
    int offset = 0;
    int len = 0;
    char* mem = (char*) malloc( sizeof(char) * ARR_SIZE );

    offset = len;
    strncpy(
        (char*) mem+offset,
        "Hello, ",
        ARR_SIZE-len);
    len = strlen(mem);

    offset = len;
    strncpy(
        (char*) mem+offset,
        what,
        ARR_SIZE-len);
    len = strlen(mem);

    offset = len;
    strncpy(
        (char*) mem+offset,
        "!\n",
        ARR_SIZE-len);
    len = strlen(mem);

    return mem;
}

