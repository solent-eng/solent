#include <windows.h>
#include <stdint.h>

#ifndef WINPLACE_H
#define WINPLACE_H
int winplace_determine_screen_pixel_drop(int char_rows);
int winplace_determine_screen_pixel_rest(int char_cols);
void winplace_init(char* path);
void winplace_paint_begin(HDC hdcSrc);
void winplace_paint_end();
void winplace_paint_c(HDC hdcDest, uint16_t drop, uint16_t rest, unsigned char c, unsigned int colR, unsigned int colG, unsigned int colB);
#endif /* WINPLACE_H */

