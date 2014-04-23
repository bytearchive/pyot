#ifndef __STATIC_ROUTNG_MAP_H__
#define __STATIC_ROUTNG_MAP_H__

/*                                  0 0 0 0 0 0 0 0 0 1 1 1 1 1 1             */
/*                                  1 2 3 4 5 6 7 8 9 0 1 2 3 4 5             */
static uint8_t nbr_map[15][15] = { {0,1,1,0,0,0,0,0,0,0,0,0,0,0,0},  /* 1 */  \
                                   {1,0,0,1,1,0,0,0,0,0,0,0,0,0,0},  /* 2 */  \
                                   {1,0,0,0,0,1,1,0,0,0,0,0,0,0,0},  /* 3 */  \
                                   {0,1,0,0,0,0,0,1,1,0,0,0,0,0,0},  /* 4 */  \
                                   {0,1,0,0,0,0,0,0,0,1,1,0,0,0,0},  /* 5 */  \
                                   {0,0,1,0,0,0,0,0,0,0,0,1,1,0,0},  /* 6 */  \
                                   {0,0,1,0,0,0,0,0,0,0,0,0,0,1,1},  /* 7 */  \
                                   {0,0,0,1,0,0,0,0,0,0,0,0,0,0,0},  /* 8 */  \
                                   {0,0,0,1,0,0,0,0,0,0,0,0,0,0,0},  /* 9 */  \
                                   {0,0,0,0,1,0,0,0,0,0,0,0,0,0,0},  /* 10 */ \
                                   {0,0,0,0,1,0,0,0,0,0,0,0,0,0,0},  /* 11 */ \
                                   {0,0,0,0,0,1,0,0,0,0,0,0,0,0,0},  /* 12 */ \
                                   {0,0,0,0,0,1,0,0,0,0,0,0,0,0,0},  /* 13 */ \
                                   {0,0,0,0,0,0,1,0,0,0,0,0,0,0,0},  /* 14 */ \
                                   {0,0,0,0,0,0,1,0,0,0,0,0,0,0,0}}; /* 15 */

/*                                        0 0 0 0 0 0 0 0 0 1 1 1 1 1 1       */
/*                                      E 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5       */
static uint8_t routing_map[15][16] = { {0,0,2,3,2,2,3,3,2,2,2,2,3,3,3,3},  /* 1 */  \
                                       {1,1,0,1,4,5,1,1,4,4,5,5,1,1,1,1},  /* 2 */  \
                                       {1,1,1,0,1,1,6,7,1,1,1,1,6,6,7,7},  /* 3 */  \
                                       {2,2,2,2,0,2,2,2,8,9,2,2,2,2,2,2},  /* 4 */  \
                                       {2,2,2,2,2,0,2,2,2,2,10,11,2,2,2,2},  /* 5 */  \
                                       {3,3,3,3,3,3,0,3,3,3,3,3,12,13,3,3},  /* 6 */  \
                                       {3,3,3,3,3,3,3,0,3,3,3,3,3,3,14,15},  /* 7 */  \
                                       {4,4,4,4,4,4,4,4,0,4,4,4,4,4,4,4},  /* 8 */  \
                                       {4,4,4,4,4,4,4,4,4,0,4,4,4,4,4,4},  /* 9 */  \
                                       {5,5,5,5,5,5,5,5,5,5,0,5,5,5,5,5},  /* 10 */ \
                                       {5,5,5,5,5,5,5,5,5,5,5,0,5,5,5,5},  /* 11 */ \
                                       {6,6,6,6,6,6,6,6,6,6,6,6,0,6,6,6},  /* 12 */ \
                                       {6,6,6,6,6,6,6,6,6,6,6,6,6,0,6,6},  /* 13 */
                                       {7,7,7,7,7,7,7,7,7,7,7,7,7,7,0,7},  /* 14 */
                                       {7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,0}}; /* 15 */


#endif /* __STATIC_ROUTNG_MAP_H__ */
