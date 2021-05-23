#include <stdlib.h>
#include <stdint.h>
#include <stdio.h>

#include <tchar.h>
#include <Windows.h>

#include "winplace.h"


#ifdef __cplusplus
extern "C" {
#endif

/* --------------------------------------------------------
  config
-------------------------------------------------------- */
#define MAX_COLS 230
#define MAX_ROWS 70

#define RING_BUFFER_SIZE 10

/* We do not put the nothing input type into the input ring-buffer, but we do
 * return 0 from the API when there is no new input to consider. Hence, it is
 * defined here so that nobody will be tempted to use 0 for another
 * purpose.
 */
#define INPUT_TYPE_NO_EVENT 0
#define INPUT_TYPE_KEVENT 1
#define INPUT_TYPE_MEVENT_BUTTON 2


/* --------------------------------------------------------
  screen structures
-------------------------------------------------------- */
typedef struct Cell_st {
    // 7-bit ascii. Yes, the second half of the range is wasted memory.
    uint8_t c;
    // colour
    uint8_t o;
    uint8_t _spare_a;
    uint8_t _spare_b;
} Cell;

typedef struct Row_st {
    Cell col[MAX_COLS];
} Row;

typedef struct Console_st {
    int keep_running;

    Row row[MAX_ROWS];

    // ring buffer for input
    uint64_t ring[RING_BUFFER_SIZE];
    int r_idx; // next read
    int w_idx; // next write
} Console;

typedef struct KsMetaStatus_st {
    uint8_t shift : 1;
    uint8_t ctrl : 1;
} KsMetaStatus;

typedef struct MsMetaStatus_st {
    uint8_t mb0 : 1;
    uint8_t mb1 : 1;
    uint8_t mb2 : 1;
} MsMetaStatus;


/* --------------------------------------------------------
  global
-------------------------------------------------------- */
Console* CONSOLE;

MSG messages; /* Here messages to the application are saved */

uint64_t NO_EVENT = 0;

uint8_t KS_BITFIELD_BYTE = 0;
KsMetaStatus* KS_META_STATUS = (KsMetaStatus*) &KS_BITFIELD_BYTE;

uint8_t MS_BITFIELD_BYTE = 0;
MsMetaStatus* MS_META_STATUS = (MsMetaStatus*) &MS_BITFIELD_BYTE;

int ROW_COUNT = 4;
int COL_COUNT = 10;
int N_DROP;
int N_REST;
Row* ROW;
Cell* CELL;


/* --------------------------------------------------------
  logging
-------------------------------------------------------- */
typedef void (*cc_log_t) (char*);

cc_log_t CF_LOG = NULL;

static char WORKING_S[400];

void log(char* msg) {
    if (CF_LOG == NULL) {
        return;
    }
    CF_LOG(msg);
}


/* --------------------------------------------------------
  ringbuffer interaction
-------------------------------------------------------- */
void buffer_kevent(uint8_t c) {
    int w_next;
    uint64_t* event ;
    uint8_t* u8 ;

    // Work out what the next write point would be if we did
    // buffer more data.
    w_next = CONSOLE->w_idx + 1;
    if (w_next == RING_BUFFER_SIZE) {
        w_next = 0;
    }

    // Cover the case that we have run out of buffer space.
    if (w_next == CONSOLE->r_idx) {
        return ;
    }

    // Get the event from the ring-buffer that we will write to,
    event = &(CONSOLE->ring[CONSOLE->w_idx]);
    // Rotate the write pointer ready for next time.
    CONSOLE->w_idx = w_next;

    // Cram the kevent into our uint64_t
    //
    // byte 0: Input-type
    u8 = (uint8_t*) event;
    *u8 = INPUT_TYPE_KEVENT;
    // byte 1: Bitfield indicating status of ctrl, shift, etc
    u8++;
    *u8 = KS_BITFIELD_BYTE;
    // byte 2: Keystroke-value
    u8++;
    *u8 = c;
    // byte 3: Unused by this event-type
    u8++;
}


/* --------------------------------------------------------
  window creation
-------------------------------------------------------- */
/*  Declare Windows procedure  */
LRESULT CALLBACK WindowProcedure (HWND, UINT, WPARAM, LPARAM);

/*  Make the class name into a global variable  */
TCHAR szClassName[ ] = _T("windows_form_grid_console");

HWND OUR_HWND;

int init_window() {
    HWND hWnd; /* This is the handle for our window */
    HMODULE hModule;
    HINSTANCE hInstance;
    int nCmdShow;
    WNDCLASSEX wincl;        /* Data structure for the windowclass */
    int height_in_pixels;
    int width_in_pixels;

    hInstance = GetModuleHandle(NULL);
    hModule = hInstance;

    HBRUSH HBRUSH_BLACK = CreateSolidBrush(0x00000000) ;

    /* The Window structure */
    wincl.hInstance = hInstance;
    wincl.lpszClassName = szClassName;
    wincl.lpfnWndProc = WindowProcedure;  /* This function is called by windows */
    wincl.style = CS_DBLCLKS;             /* Catch double-clicks */
    wincl.cbSize = sizeof(WNDCLASSEX);
    /* Use default icon and mouse-pointer */
    wincl.hIcon = LoadIcon(NULL, IDI_APPLICATION);
    wincl.hIconSm = LoadIcon(NULL, IDI_APPLICATION);
    wincl.hCursor = LoadCursor(NULL, IDC_ARROW);
    wincl.lpszMenuName = NULL;                 /* No menu */
    wincl.cbClsExtra = 0;                      /* No extra bytes after the window class */
    wincl.cbWndExtra = 0;                      /* structure or the window instance */
    /* Use Windows's default colour as the background of the window */
    //wincl.hbrBackground = (HBRUSH) COLOR_BACKGROUND;
    wincl.hbrBackground = HBRUSH_BLACK ;

    // xxx adapt path to relpath
    HICON hIcon = (HICON) LoadImage(
        0,
        (char*) "C:\\saga\\007.solent\\solent\\wres\\ext\\windows_form_grid_console\\sail_SFT_icon.ico",
        IMAGE_ICON,
        48,
        48,
        LR_LOADFROMFILE | LR_DEFAULTSIZE | LR_DEFAULTCOLOR);
    if (NULL == hIcon) {
        printf("Icon is null\n"); // xxx
    }
    else {
        printf("Setting icon\n"); // xxx
        wincl.hIcon = hIcon;
        wincl.hIconSm = hIcon;
    }

    /* Register the window class, and if it fails quit the program */
    if (!RegisterClassEx (&wincl)) {
        return -1;
    }
    
    // xxx set program width and height dynamically.
    height_in_pixels = winplace_determine_screen_pixel_drop(ROW_COUNT);
    width_in_pixels = winplace_determine_screen_pixel_rest(COL_COUNT);
    hWnd = CreateWindowEx (
           0,                   // dwExStyle, Extended possibilites for variation
           szClassName,         // lpClassName
           _T("Title Text"),    // lpWindowName, Title Text
           WS_OVERLAPPEDWINDOW, // dwStyle, default window
           CW_USEDEFAULT,       // x, Windows decides the position
           CW_USEDEFAULT,       // y, where the window ends up on the screen
           width_in_pixels,     // nWidth, in pixels
           height_in_pixels,    // nHeight, in pixels
           HWND_DESKTOP,        // The window is a child-window to desktop
           NULL,                // No menu
           hInstance,           // Program Instance handler
           NULL                 // No Window Creation data
           );

    OUR_HWND = hWnd;

    nCmdShow = SW_SHOW;
    ShowWindow(hWnd, nCmdShow);

    return 0;
}

void repaint_window()
{
    HDC hdc;
    PAINTSTRUCT ps;

    hdc = BeginPaint(OUR_HWND, &ps);
    winplace_paint_begin(hdc);
    {
        unsigned char c;
        int i, level;

        for (N_DROP=0; N_DROP<ROW_COUNT; N_DROP++) {
            ROW = &(CONSOLE->row[N_DROP]);
            for (N_REST=0; N_REST<COL_COUNT; N_REST++) {
                CELL = &(ROW->col[N_REST]);
                c = CELL->c;
                //printf("c %3d %3d|%c|\n", N_DROP, N_REST, c); // xxx
                winplace_paint_c(
                    hdc,
                    N_DROP,
                    N_REST,
                    c,
                    64,
                    128,
                    192);
            }
        }
    }
    DeleteDC(hdc);
    winplace_paint_end();
    EndPaint(OUR_HWND, &ps);
}

/* This function is called by the Windows function DispatchMessage()  */
LRESULT CALLBACK WindowProcedure(HWND hwnd, UINT message, WPARAM wParam, LPARAM lParam)
{
    static int  cx_char, cx_caps, char_width;
    static HFONT hFont;
    
    HDC         hdc;
    int         i;
    PAINTSTRUCT ps ;
    TCHAR       szBuffer [10] ;
    TCHAR       ch ;
    TCHAR*      tchar ;
    TEXTMETRIC  tm ;
    LPCTSTR     lpString ;

    switch (message)
    {
    case WM_CREATE:
        hdc = GetDC (hwnd) ;

        //hFont = (HFONT) GetStockObject(ANSI_FIXED_FONT); 
        hFont = CreateFont(
            34,                     // nHeight
            20,                     // nWidth
            0,                      // nEscapement
            0,                      // nOrientation
            700,                    // fnWeight
            FALSE,                  // fdwItalic
            FALSE,                  // fdwUnderline
            FALSE,                  // fwdStrikeout
            DEFAULT_CHARSET,        // fdwCharset
            OUT_OUTLINE_PRECIS,     // fdwOutputPrecision
            CLIP_DEFAULT_PRECIS,    // fdwClipPrecision
            ANTIALIASED_QUALITY,    // fdwQuality
            VARIABLE_PITCH,         // fdwPitchAndFamily
            TEXT("Courier New"));   // lpszFace
        SelectObject(hdc, hFont);

        GetTextMetrics (hdc, &tm) ;
        cx_char = tm.tmAveCharWidth ;
        cx_caps = (tm.tmPitchAndFamily & 1 ? 3 : 2) * cx_char / 2 ;
        char_width = tm.tmHeight + tm.tmExternalLeading ;

        ReleaseDC (hwnd, hdc) ;
        return 0 ;

    case WM_PAINT:
        repaint_window();
        return 0 ;

    case WM_KEYDOWN:
        ch = (TCHAR) wParam;
        switch (ch) {
        case 16: // shift
            KS_META_STATUS->shift = 1;
            break;
        case 17: // ctrl
            KS_META_STATUS->ctrl = 1;
            break;
        default:
            buffer_kevent(
                (unsigned char) ch) ;
        }
        return 0 ;

    case WM_KEYUP:
        ch = (TCHAR) wParam;
        switch (ch) {
        case 16: // shift
            KS_META_STATUS->shift = 0;
            break;
        case 17: // ctrl
            KS_META_STATUS->ctrl = 0;
            break;
        default:
            // Do nothing. This is WM_KEYUP.
            break;
        }
        return 0 ;

    case WM_DESTROY:
        CONSOLE->keep_running = 0 ;
        PostQuitMessage(0) ;
        return 0 ;

    default: /* for messages that we don't deal with */
        return DefWindowProc (hwnd, message, wParam, lParam);
    }
}


/* --------------------------------------------------------
  api
-------------------------------------------------------- */
#define DLLX __declspec(dllexport)

DLLX void set_cc_log(cc_log_t cc_log) {
    CF_LOG = cc_log;
}

DLLX void create_screen(int char_cols, int char_rows) {
    sprintf(WORKING_S, "create_screen %d %d", char_cols, char_rows);
    log(WORKING_S);

    if (char_rows > MAX_ROWS) {
        log("Error! Width exceeds MAX_COLS");
        return;
    }
    if (char_cols > MAX_COLS) {
        log("Error! Width exceeds MAX_COLS");
        return;
    }

    ROW_COUNT = char_rows;
    COL_COUNT = char_cols;

    // xxx need to find a better way to do this
    const char* path_codepath =
        "c:\\saga\\017.bitmap.display\\img\\Codepage-850.mono.bmp";
    winplace_init((char*) path_codepath);

    CONSOLE = (Console*) malloc(sizeof(Console));

    CONSOLE->keep_running = 1;

    // hammer the cells to be empty
    for (N_DROP=0; N_DROP<ROW_COUNT; N_DROP++) {
        ROW = &(CONSOLE->row[N_DROP]);
        for (N_REST=0; N_REST<COL_COUNT; N_REST++) {
            CELL = &(ROW->col[N_REST]);
            CELL->c = ' ';
            CELL->o = 0;
        }
    }
    CONSOLE->row[N_DROP-1].col[N_REST-1].c = '+';

    CONSOLE->r_idx = 0;
    CONSOLE->w_idx = 0;

    init_window();
}

#define WINDOW_EVENTS_PER_CALL 10

/* You need to call this regularly so that Windows keeps processing events.
 * This returns 0 when the process has closed. */
DLLX int process_windows_events() {
    int i, res;

    if (!CONSOLE->keep_running) {
        return 0;
    }

    /* Run the message loop. It will run until GetMessage() returns 0 */
    for (i=0; i<WINDOW_EVENTS_PER_CALL; i++) {
        res = PeekMessage(
            &(messages),            // lpMsg
            NULL,                   // hWnd
            0,                      // wMsgFilterMin
            0,                      // wMsgFilterMax
            PM_REMOVE);             // wRemoveMsg
        if (res == 0) {
            /* We did not receive a new message. */
            break;
        }
        /* Translate virtual-key messages into character messages */
        TranslateMessage(&(messages));
        /* Send message to WindowProcedure */
        DispatchMessage(&(messages));
    }

    return CONSOLE->keep_running;
}

/*
 * This will put a uint64_t value into *event. Here is a rough
 * guide to interpreting these four bytes,
 *
 * Byte 0, this will tell you whether or not there is activity,
 * and the type of activity. See the INPUT_TYPE_* defines above. 
 *
 * Byte 1,
 *  when INPUT_TYPE_NO_EVENT:       irrelevant
 *  when INPUT_TYPE_KEVENT:         current value of KS_BITFIELD_BYTE
 *  when INPUT_TYPE_MEVENT_BUTTON:  current value of MS_BITFIELD_BYTE
 *
 * Byte 2,
 *  when INPUT_TYPE_NO_EVENT:       irrelevant
 *  when INPUT_TYPE_KEVENT:         windows keystroke code
 *  when INPUT_TYPE_MEVENT_BUTTON:  xxx tbd
 *
 * Byte 3-7,
 *  xxx tbd
 *
 */
DLLX void get_next_event(uint64_t* event)
{
    if (CONSOLE->r_idx == CONSOLE->w_idx) {
        *event = NO_EVENT;
    }
    else {
        *event = CONSOLE->ring[CONSOLE->r_idx];
        // move the read pointer to the next cell
        CONSOLE->r_idx++;
        if (CONSOLE->r_idx == RING_BUFFER_SIZE) {
            CONSOLE->r_idx = 0;
        }
    }
}

DLLX void set(int drop, int rest, int c, int o)
{
    Row* row;
    Cell* cell;

    row = &(CONSOLE->row[drop]);
    cell = &(row->col[rest]);
    cell->c = c;
    cell->o = o;
}

DLLX void redraw()
{
    RedrawWindow(OUR_HWND, NULL, NULL, RDW_INVALIDATE);
    repaint_window();
}

DLLX void close()
{
}


#ifdef __cplusplus
}
#endif
