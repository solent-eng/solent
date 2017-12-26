#include <stdlib.h>
#include <stdint.h>

#include <tchar.h>
#include <Windows.h>


/* --------------------------------------------------------
  windows magic
-------------------------------------------------------- */
/* from https://www.codeguru.com/cpp/w-p/dll/tips/article.php/c3635/Tip-Detecting-a-HMODULEHINSTANCE-Handle-Within-the-Module-Youre-Running-In.htm */

#if _MSC_VER >= 1300    // for VC 7.0
  // from ATL 7.0 sources
  #ifndef _delayimp_h
  extern "C" IMAGE_DOS_HEADER __ImageBase;
  #endif
#endif

/* This allows us to get the HModule, which we are going
to need if we are launching windows. This has been an obstacle
because we are inside a dll, rather than writing a standalone
Windows app. */
HMODULE get_current_module()
{
#if _MSC_VER < 1300    // earlier than .NET compiler (VC 6.0)
  // Here's a trick that will get you the handle of the module
  // you're running in without any a-priori knowledge:
  // http://www.dotnet247.com/247reference/msgs/13/65259.aspx
 
  MEMORY_BASIC_INFORMATION mbi;
  static int dummy;
  VirtualQuery( &dummy, &mbi, sizeof(mbi) );
 
  return reinterpret_cast<HMODULE>(mbi.AllocationBase);
 
#else    // VC 7.0
  // from ATL 7.0 sources
 
  return reinterpret_cast<HMODULE>(&__ImageBase);
#endif
}


/* --------------------------------------------------------
  config
-------------------------------------------------------- */
#define MAX_COLS 230
#define MAX_ROWS 70

#define RING_BUFFER_SIZE 3

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

    uint32_t ring[RING_BUFFER_SIZE];
    int r_idx; // next read
    int w_idx; // next write
} Console;


/* --------------------------------------------------------
  global
-------------------------------------------------------- */
Console* CONSOLE;

MSG messages; /* Here messages to the application are saved */

HBRUSH HBRUSH_BLACK = CreateSolidBrush(0x00000000) ;

uint32_t NO_EVENT = 0;


/* --------------------------------------------------------
  ringbuffer interaction
-------------------------------------------------------- */
void buffer_kevent(uint8_t c) {
    int w_next;
    uint32_t* event ;
    uint8_t* u8 ;

    // Work out what the next write point would be if we did
    // buffer more data.
    w_next = CONSOLE->w_idx + 1;
    if (w_next == RING_BUFFER_SIZE) {
        w_next = 0;
    }

    // Cover the case that we have run out of buffer space.
    if (w_next == CONSOLE->r_idx) {
        exit(1);
        return ;
    }

    // Get the event from the ring-buffer that we will write to,
    event = &(CONSOLE->ring[CONSOLE->w_idx]);
    // Rotate the write pointer ready for next time.
    CONSOLE->w_idx = w_next;

    // Cram the kevent into our uint32_t
    //
    // byte 0: Input-type
    u8 = (uint8_t*) event;
    *u8 = INPUT_TYPE_KEVENT;
    // byte 1: Keystroke-value
    u8++;
    *u8 = c;
    // byte 2: Unused by this event-type
    u8++;
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

int init_window() {
    HWND hWnd; /* This is the handle for our window */
    HMODULE hModule;
    HINSTANCE hInstance;
    int nCmdShow;
    WNDCLASSEX wincl;        /* Data structure for the windowclass */

    hModule = get_current_module();
    hInstance = GetModuleHandle(NULL);

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
    /* Register the window class, and if it fails quit the program */
    if (!RegisterClassEx (&wincl)) {
        return -1;
    }
    
    hWnd = CreateWindowEx (
           0,                   /* Extended possibilites for variation */
           szClassName,         /* Classname */
           _T("Title Text"),    /* Title Text */
           WS_OVERLAPPEDWINDOW, /* default window */
           CW_USEDEFAULT,       /* Windows decides the position */
           CW_USEDEFAULT,       /* where the window ends up on the screen */
           544,                 /* The programs width */
           375,                 /* and height in pixels */
           HWND_DESKTOP,        /* The window is a child-window to desktop */
           NULL,                /* No menu */
           hInstance,           /* Program Instance handler */
           NULL                 /* No Window Creation data */
           );

    nCmdShow = SW_SHOW;
    ShowWindow(hWnd, nCmdShow);

    return 0;
}

/* This function is called by the Windows function DispatchMessage()  */
LRESULT CALLBACK WindowProcedure(HWND hwnd, UINT message, WPARAM wParam, LPARAM lParam)
{
    static int  cx_char, cx_caps, char_width, col_count, row_count ;
    static HFONT hFont;
    
    HDC         hdc;
    int         i, col, row ;
    PAINTSTRUCT ps ;
    TCHAR       szBuffer [10] ;
    TCHAR       ch ;
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

        // xxx
        col_count = 10;
        row_count = 4;

        GetTextMetrics (hdc, &tm) ;
        cx_char = tm.tmAveCharWidth ;
        cx_caps = (tm.tmPitchAndFamily & 1 ? 3 : 2) * cx_char / 2 ;
        char_width = tm.tmHeight + tm.tmExternalLeading ;

        ReleaseDC (hwnd, hdc) ;
        return 0 ;

    case WM_PAINT:
        hdc = BeginPaint (hwnd, &ps) ;

        // Text will be drawn with a black background
        SetBkColor(hdc, RGB(0, 0, 0)) ;
        // Set font
        SelectObject(hdc, hFont);

        SetTextColor(hdc, RGB(255, 25, 2)) ;
        lpString = _T("@ Here is some text") ;
        for (row = 0; row < row_count ; row++) {
            TextOut (hdc, 0, char_width * row,
                     lpString, lstrlen(lpString)) ;
        }

        EndPaint(hwnd, &ps) ;
        return 0 ;

    case WM_KEYDOWN:
        switch (wParam) {
        default:
            ch = (TCHAR) wParam;
            buffer_kevent(
                (unsigned char) ch) ;
        }
        return 0 ;

    case WM_DESTROY:
        CONSOLE->keep_running = 0 ;
        PostQuitMessage(0) ;
        return 0 ;

    default:                      /* for messages that we don't deal with */
        return DefWindowProc (hwnd, message, wParam, lParam);
    }
}


/* --------------------------------------------------------
  api
-------------------------------------------------------- */
extern "C" void create_screen(int width, int height) {
    int i, j, res;
    Row* row;
    Cell* cell;

    CONSOLE = (Console*) malloc(sizeof(Console));

    CONSOLE->keep_running = 1;

    for (i=0; i<MAX_ROWS; i++) {
        row = &(CONSOLE->row[i]);
        for (j=0; j<MAX_COLS; j++) {
            cell = &(row->col[j]);
            cell->c = ' ';
            cell->o = 0;
        }
    }

    CONSOLE->r_idx = 0;
    CONSOLE->w_idx = 0;

    init_window();
}

#define WINDOW_EVENTS_PER_CALL 10

/* Returns 0 when the process has closed. */
extern "C" int process_windows_events() {
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

extern "C" void get_next_event(uint32_t* event)
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

extern "C" void set(int drop, int rest, int c, int o)
{
    Row* row;
    Cell* cell;
    
    row = &(CONSOLE->row[drop]);
    cell = &(row->col[rest]);
    cell->c = c;
    cell->o = o;
}

extern "C" void redraw()
{
}

extern "C" void close()
{
}

