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

static float input[MATRIX_SIZE][MATRIX_SIZE];
static float kernel[KERNEL_SIZE][KERNEL_SIZE];
static float output[MATRIX_SIZE][MATRIX_SIZE];

static inline uint64_t read_mcycle(void) {
    uint64_t cycle;
    
    asm volatile ("rdcycle %0" : "=r"(cycle));
    return cycle;
}

int main(void) {
    printf("[Convolution] M=%d, K=%d, Cores=%d, L1=%d, TILE=%d, UNROLL=%d\n",
           MATRIX_SIZE, KERNEL_SIZE, TOTAL_CORES, L1_DCACHE_SIZE,
           TILE_SIZE, UNROLL_FACTOR);

    uint64_t start = read_mcycle();

    // Initialize
    for (int i = 0; i < MATRIX_SIZE; i++) {
        for (int j = 0; j < MATRIX_SIZE; j++) {
            input[i][j] = (float)(i + j);
            output[i][j] = 0.0f;
        }
    }
    for (int i = 0; i < KERNEL_SIZE; i++) {
        for (int j = 0; j < KERNEL_SIZE; j++) {
            kernel[i][j] = 1.0f;
        }
    }

    // Tiled convolution (over i, j) only if (iBase + TILE_SIZE <= M - K + 1)
    for (int iBase = 0; iBase < MATRIX_SIZE - KERNEL_SIZE + 1; iBase += TILE_SIZE) {
        for (int jBase = 0; jBase < MATRIX_SIZE - KERNEL_SIZE + 1; jBase += TILE_SIZE) {
            int iMax = (iBase + TILE_SIZE > MATRIX_SIZE - KERNEL_SIZE + 1)
                      ? (MATRIX_SIZE - KERNEL_SIZE + 1) : (iBase + TILE_SIZE);
            int jMax = (jBase + TILE_SIZE > MATRIX_SIZE - KERNEL_SIZE + 1)
                      ? (MATRIX_SIZE - KERNEL_SIZE + 1) : (jBase + TILE_SIZE);

            for (int i = iBase; i < iMax; i++) {
                for (int j = jBase; j < jMax; j++) {
                    float sum = 0.0f;
                    // unrolled kernel loops
                    for (int ki = 0; ki < KERNEL_SIZE; ki++) {
                        for (int kj = 0; kj < KERNEL_SIZE; kj += UNROLL_FACTOR) {
                            // partial unroll
                            for (int uf = 0; uf < UNROLL_FACTOR; uf++) {
                                int kk = kj + uf;
                                if (kk < KERNEL_SIZE) {
                                    sum += input[i + ki][j + kk] 
                                        * kernel[ki][kk];
                                }
                            }
                        }
                    }
                    output[i][j] = sum;
                }
            }
        }
    }
    
    uint64_t end = read_mcycle();

    printf("output[0][0] = %f\n", output[0][0]);
    printf("output[%d][%d] = %f\n", MATRIX_SIZE - KERNEL_SIZE, MATRIX_SIZE - KERNEL_SIZE, output[MATRIX_SIZE - KERNEL_SIZE][MATRIX_SIZE - KERNEL_SIZE]);
    printf("Cycle count = %llu\n", (long long unsigned) (end - start));
    return 0;
}

