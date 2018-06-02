#include "winplace.h"

// xxx
#include <stdio.h>

// buffer pixels present in the font file
const int WINPLACE_BUFFER_DROP = 4;
const int WINPLACE_BUFFER_REST = 4;
// width and height of each character in both the font file and our output
const int WINPLACE_CDROP = 14;
const int WINPLACE_CREST = 8;
// gaps between characters in the font file
const int WINPLACE_SRC_DROP_GAP = 0;
const int WINPLACE_SRC_REST_GAP = 1;
// gaps between characters in our output
const int WINPLACE_DST_DROP_GAP = 2;
const int WINPLACE_DST_REST_GAP = 3;

int winplace_determine_screen_pixel_drop(int char_rows) {
    int peri, extra;

    // xxx
    printf("winplace_determine_screen_pixel_drop char_rows:%d\n", char_rows);

    peri = char_rows + 2;
    extra = 25; // compensate for title bar
    return ((peri*WINPLACE_CDROP) + (peri*WINPLACE_DST_DROP_GAP) + extra);
}
int winplace_determine_screen_pixel_rest(int char_cols) {
    int peri, extra;

    // xxx
    printf("winplace_determine_screen_pixel_rest char_cols:%d\n", char_cols);

    peri = char_cols + 2;
    extra = 0;
    return ((peri*WINPLACE_CREST) + (peri*WINPLACE_DST_REST_GAP) + extra);
}

// This contains our palette
HBITMAP BMP;
// This is a working bitmap
HBITMAP SIGIL;
// This is a working area we use for the sigil
HDC HDC_BMP, HDC_SIGIL;

void winplace_init(char* path) {
    BMP = (HBITMAP) LoadImage(
        0,
        path,
        IMAGE_BITMAP,
        0,
        0,
        LR_LOADFROMFILE | LR_DEFAULTSIZE);
    SIGIL = CreateBitmap(
        WINPLACE_CREST,
        WINPLACE_CDROP,
        1,
        1,
        NULL);
}

/* Do this with the same frequency as BeginPaint. */
void winplace_paint_begin(HDC hdcSrc) {
    HDC_BMP = CreateCompatibleDC(hdcSrc);
    SelectObject(HDC_BMP, BMP);

    HDC_SIGIL = CreateCompatibleDC(hdcSrc);
    SelectObject(HDC_SIGIL, SIGIL);
}

void winplace_paint_end() {
	DeleteDC(HDC_BMP);
    DeleteObject(HDC_SIGIL);
}

void winplace_paint_c(HDC hdcDest, uint16_t drop, uint16_t rest, unsigned char c, unsigned int colR, unsigned int colG, unsigned int colB) {
    unsigned int paletteDrop, paletteRest;
    unsigned int srcDrop, srcRest;
    unsigned int dstDrop, dstRest;
    unsigned int pixelRest, pixelDrop;
    //
    // work out the drop and rest offsets of (unsigned char) c within our
    // font bitmap.
    paletteDrop = c / 32;
    paletteRest = c % 32;
    //
    // work out our dimensions
    srcDrop = WINPLACE_BUFFER_DROP + (paletteDrop*WINPLACE_CDROP) + (paletteDrop*WINPLACE_SRC_DROP_GAP);
    srcRest = WINPLACE_BUFFER_REST + (paletteRest*WINPLACE_CREST) + (paletteRest*WINPLACE_SRC_REST_GAP);
    dstDrop = (drop*WINPLACE_CDROP) + (drop*WINPLACE_DST_DROP_GAP);
    dstRest = (rest*WINPLACE_CREST) + (rest*WINPLACE_DST_REST_GAP);
    //
    // copy one character from BMP (font bitmap) into SIGIL (one character)
    BitBlt(
        HDC_SIGIL,      // hdc dest
        0,              // dst rest
        0,              // dst drop
        WINPLACE_CREST, // width
        WINPLACE_CDROP, // height
        HDC_BMP,        // hdc src
        srcRest,        // src rest
        srcDrop,        // src drop
        SRCCOPY);       // raster operation code
    //
    // set sigil colour
    colR = colR % 255;
    colG = colG % 255;
    colB = colB % 255;
    SetTextColor(hdcDest, RGB(colR, colG, colB));
    SetBkColor(hdcDest, RGB(0, 0, 0));
    //
    // place the coloured sigil into the destination
    BitBlt(
        hdcDest,        // hdc dest
        dstRest,        // dst rest
        dstDrop,        // dst drop
        WINPLACE_CREST, // width
        WINPLACE_CDROP, // height
        HDC_SIGIL,      // hdc src
        0,              // src rest
        0,              // src drop
        SRCCOPY);       // raster operation code
}

