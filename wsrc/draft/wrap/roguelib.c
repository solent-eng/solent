//
// This is obsolete, but was the original code that I used to get ctypes
// working. Leaving it here for moment in case I want to reference anything
// into clib.c. Should be removed in near future.
//

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <sys/ioctl.h>

// --------------------------------------------------------
//  doc
// --------------------------------------------------------
//
// = screen_positions
//
//   0   5   10 drop
//   5          |
//   10         V
// rest ------->
//
//
// = entity positions
//
//      -s      south
//   -e  <  e   |
//       s      V
// east ------->
//
//
// --------------------------------------------------------
//  defines
// --------------------------------------------------------
//
// see doc: screen_positions
//
#define SCREEN_DROP 24
#define SCREEN_REST 78
#define HALF_DROP (SCREEN_DROP / 2)
#define HALF_REST (SCREEN_REST / 2)


// --------------------------------------------------------
//  ehandlers
// --------------------------------------------------------
void abort1(char* a) {
    printf("\n\nfatal|%s|\n\n", a);
    exit(1);
}
void abort2(char* a, int code) {
    printf("\n\nfatal|%s|%d|\n\n", a, code);
    exit(code);
}
void abort3(char* a, char* b, int code) {
    printf("\n\nfatal|%s|%s|%d|\n\n", a, b, code);
    exit(code);
}


// --------------------------------------------------------
//  structures
// --------------------------------------------------------
struct ent {
  int is_sentinel; // up staircase
  struct ent* next;

  int rel_s;
  int rel_e;
  char c;
};

struct ent* o_ent() {
    struct ent* o = malloc(sizeof(struct ent));
    o->is_sentinel = 1;
    o->next = o;

    o->rel_s = 0;
    o->rel_e = 0;
    o->c = '<';

    return o;
}

struct ent* n_ent(struct ent* o, int rel_s, int rel_e, char c) {
    struct ent* w = o->next;

    o->next = malloc(sizeof(struct ent));
    o->next->is_sentinel = 0;
    o->next->next = w;

    o->next->rel_s = rel_s;
    o->next->rel_e = rel_e;
    o->next->c = c;

    return o->next;
}

// xxx put tdd around this
void x_ent(struct ent* o, struct ent* x) {
    struct ent* w;

    if (o == x) { abort1("attempt to shring ent sentinel"); }
    w = o;
    while (w->next != x && w->next != o) w = w->next;
    if (w->next == o) { abort1("entity x not in ring."); }

    w->next = w->next->next;
    free(x);
}

struct level {
  int is_sentinel; // garden
  struct level* next;

  struct ent* ent;
};

struct level* o_level() {
    struct level* o = malloc(sizeof(struct level));
    o->next = o;
    o->ent = o_ent();
    return o;
}

struct level* n_level(struct level* o) {
    struct level* w;
    w = o->next;
    o->next = malloc(sizeof(struct level));
    o->next->is_sentinel = 0;
    o->next->next = w;
    o->ent = o_ent();
}

// xxx put tdd around this
void x_level(struct level* o, struct level* x) {
    struct level* w;
    
    if (o == x) { abort1("x_level called on sentinel."); }
    w = o;
    while (w->next != x && w->next != o) w = w->next;
    if (w->next == o) { abort1("entity x is not in ring."); }

    w->next = w->next->next;
    free(x);
}

struct avatar {
  int is_sentinel; // gm
  struct avatar* next;

  char* blank;
  char* screen;

  struct level* level;
  struct ent* player;
};

struct avatar* o_avatar(int drop, int rest, struct level* level, struct ent* ent) {
    struct avatar* c = malloc(sizeof(struct avatar));
    c->is_sentinel = 1;
    c->level = level;
    c->player = ent;

    c->blank = malloc( (drop * (rest+1)) * sizeof(char) ); {
        int i, offset;
        char* line;
        
        line = malloc(sizeof(char) * (rest+1));
        for (i=0; i<(rest); i++) {
            line[i] = '.';
        }
        line[rest] = '\n';

        for (i=0; i<drop; i++) {
            offset = i * (rest+1);
            strncpy( (c->blank) + offset
                   , line
                   , rest+1
                   );
        }
		c->blank[SCREEN_DROP * (SCREEN_REST+1)] = (char) '\0';

        free(line);
    }
	c->screen = malloc(SCREEN_DROP * (SCREEN_REST+1));

    return c;
}
void x_avatar(struct avatar* c) {
    free(c);
}


// --------------------------------------------------------
//  operations
// --------------------------------------------------------
char* render(struct avatar* avatar) {
    int i;
    struct ent* nw = malloc(sizeof(struct ent));
    struct ent* se = malloc(sizeof(struct ent));
    
    // these are the bounds of what we are going to display
    nw->rel_s = (avatar->player->rel_s - HALF_DROP);
    nw->rel_e = (avatar->player->rel_e - HALF_REST);
    se->rel_s = (nw->rel_s + SCREEN_DROP);
    se->rel_e = (nw->rel_e + SCREEN_REST);

    strcpy(avatar->screen, avatar->blank);

    while (1) {
        // xxx
    }

    free(nw);
    free(se);

    return avatar->screen;
}

void player_n(struct avatar* avatar) {
    avatar->player->rel_s--;
}
void player_s(struct avatar* avatar) {
    avatar->player->rel_s++;
}
void player_e(struct avatar* avatar) {
    avatar->player->rel_e++;
}
void player_w(struct avatar* avatar) {
    avatar->player->rel_e--;
}





