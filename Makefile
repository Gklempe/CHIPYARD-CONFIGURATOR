########################################
# Minimal Makefile for matrix_mult and conv_bench
########################################

# 1) Define the cross-compiler.
#    Overridable if you set CC=riscv64-unknown-elf-gcc from the shell.
CC := riscv64-unknown-elf-gcc
OBJDUMP ?= riscv64-unknown-elf-objdump

# Basic compile/link flags for a bare-metal environment
CFLAGS  = -O2 -fno-common -fno-builtin-printf -Wall -fPIE -mcmodel=medany
CFLAGS += -march=rv64imafdc -mabi=lp64d
LDFLAGS = -static -mcmodel=medany  -lc -lm -lgcc -T htif.ld

########################################
# Our two programs
########################################
PROGRAMS = matrix_mult conv_bench

# 'all' is the default target: build both .riscv binaries
all: $(addsuffix .riscv, $(PROGRAMS))

# # Generate config_params.h (if needed) before building .o
# MYCONFIG_JSON ?= ../sims/verilator/generated-src/chipyard.harness.TestHarness.MyRandomCPUConfig/chipyard.harness.TestHarness.MyRandomCPUConfig.json
# MATRIX_SIZE   ?= 4
# KERNEL_SIZE   ?= 3

# config_params.h:
# 	./generate_config.sh $(MYCONFIG_JSON) $(MATRIX_SIZE) $(KERNEL_SIZE)

########################################
# matrix_mult
########################################
matrix_mult.o: matrix_mult.c config_params.h
	$(CC) $(CFLAGS) -c matrix_mult.c -o matrix_mult.o

matrix_mult.riscv: matrix_mult.o
	$(CC) $(LDFLAGS) matrix_mult.o -o matrix_mult.riscv

########################################
# conv_bench
########################################
conv_bench.o: conv_bench.c config_params.h
	$(CC) $(CFLAGS) -c conv_bench.c -o conv_bench.o

conv_bench.riscv: conv_bench.o
	$(CC) $(LDFLAGS) conv_bench.o -o conv_bench.riscv

########################################
# (Optional) Dump
########################################
%.dump: %.riscv
	$(OBJDUMP) -D $< > $@

########################################
# Cleanup
########################################
clean:
	rm -f *.o *.riscv *.dump #config_params.h

.PHONY: all clean
