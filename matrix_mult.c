#include <stdio.h>
#include "config_params.h"


#if (L1_DCACHE_SIZE <= 8192)
  #define BASE_TILE 4
#elif (L1_DCACHE_SIZE <= 16384)
  #define BASE_TILE 8
#elif (L1_DCACHE_SIZE <= 32768)
  #define BASE_TILE 16
#else
  #define BASE_TILE 32
#endif

#if (TOTAL_CORES <= 1)
  #define TILE_SIZE (BASE_TILE)
#elif (TOTAL_CORES == 2)
  #define TILE_SIZE (BASE_TILE * 2)
#elif (TOTAL_CORES >= 4)
  #define TILE_SIZE (BASE_TILE * 4)
#else
  #define TILE_SIZE (BASE_TILE)
#endif

#if (TOTAL_CORES == 1)
  #define UNROLL_FACTOR 1
#elif (TOTAL_CORES == 2)
  #define UNROLL_FACTOR 2
#elif (TOTAL_CORES == 4)
  #define UNROLL_FACTOR 4
#else
  #define UNROLL_FACTOR 2
#endif


static float A[MATRIX_SIZE][MATRIX_SIZE];
static float B[MATRIX_SIZE][MATRIX_SIZE];
static float C[MATRIX_SIZE][MATRIX_SIZE];

static inline uint64_t read_mcycle(void) {
    uint64_t cycle;
    
    asm volatile ("rdcycle %0" : "=r"(cycle));
    return cycle;
}

int main(void) {
    printf("[Matrix Multiply] M=%d, Cores=%d, L1=%d, TILE=%d, UNROLL=%d\n",
           MATRIX_SIZE, TOTAL_CORES, L1_DCACHE_SIZE, TILE_SIZE, UNROLL_FACTOR);

    uint64_t start = read_mcycle();

    // Initialize
    for (int i = 0; i < MATRIX_SIZE; i++) {
        for (int j = 0; j < MATRIX_SIZE; j++) {
            A[i][j] = 1.0f;
            B[i][j] = 2.0f;
        }
    }

    // Tiled outer loops
    for (int iBase = 0; iBase < MATRIX_SIZE; iBase += TILE_SIZE) {
        for (int jBase = 0; jBase < MATRIX_SIZE; jBase += TILE_SIZE) {

            int iMax = (iBase + TILE_SIZE > MATRIX_SIZE) ? MATRIX_SIZE : iBase + TILE_SIZE;
            int jMax = (jBase + TILE_SIZE > MATRIX_SIZE) ? MATRIX_SIZE : jBase + TILE_SIZE;

            for (int i = iBase; i < iMax; i++) {
                for (int j = jBase; j < jMax; j++) {
                    float sum = 0.0f;

                    // Unrolled k loop
                    for (int k = 0; k < MATRIX_SIZE; k += UNROLL_FACTOR) {
                        // Expand partial sum logic
                        for (int uf = 0; uf < UNROLL_FACTOR; uf++) {
                            int kk = k + uf;
                            if (kk < MATRIX_SIZE) {
                                sum += A[i][kk] * B[kk][j];
                            }
                        }
                    }
                    C[i][j] = sum;
                }
            }
        }
    }

    uint64_t end = read_mcycle();

    // Print partial results
    printf("C[0][0] = %d\n", (int)C[0][0]);
    printf("C[%d][%d] = %d\n", MATRIX_SIZE - 1, MATRIX_SIZE - 1,
                             (int)C[MATRIX_SIZE - 1][MATRIX_SIZE - 1]);
    printf("Cycle count = %llu\n", (long long unsigned) (end - start));
    return 0;
}

