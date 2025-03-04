#!/usr/bin/env bash


set -e


MYCONFIG_JSON="$1"
MATRIX_SIZE="$2"
KERNEL_SIZE="$3"
L1_DCACHE_SIZE="$4"

if [ -z "$MYCONFIG_JSON" ] || [ -z "$MATRIX_SIZE" ] || [ -z "$KERNEL_SIZE" ] || [ -z "$L1_DCACHE_SIZE" ]; then
  echo "Usage: $0 <MYCONFIG_JSON> <MATRIX_SIZE> <KERNEL_SIZE> <L1_DCACHE_SIZE>"
  exit 1
fi


NUM_ROCKET_CORES=$(cat "$MYCONFIG_JSON" | jq '[.cpus | to_entries[]
  | select(.key | startswith("cpu@"))
  | select(.value.compatible[]? | contains("rocket0")) ]
  | length')

NUM_BOOM_CORES=$(cat "$MYCONFIG_JSON" | jq '[.cpus | to_entries[]
  | select(.key | startswith("cpu@"))
  | select(.value.compatible[]? | contains("boom0")) ]
  | length')

NUM_TOTAL_CORES=$(( NUM_ROCKET_CORES + NUM_BOOM_CORES ))


# ΝΑ ΠΑΙΡΝΩ ΣΑΝ ARGUMENT ΤΟ L1 CACHE SIZE
# ΝΑ ΤΡΕΧΩ ΜΕΣΩ ΤΟ SPIKE (spike pk matrix_mult.riscv)

cat <<EOF > config_params.h
#ifndef __CONFIG_PARAMS_H__
#define __CONFIG_PARAMS_H__

// Automatically extracted from $MYCONFIG_JSON
#define NUM_ROCKET_CORES $NUM_ROCKET_CORES
#define NUM_BOOM_CORES   $NUM_BOOM_CORES
#define TOTAL_CORES      $NUM_TOTAL_CORES

// Additional user-provided arguments
#define MATRIX_SIZE      $MATRIX_SIZE
#define KERNEL_SIZE      $KERNEL_SIZE
#define L1_DCACHE_SIZE   $L1_DCACHE_SIZE
#endif // __CONFIG_PARAMS_H__
EOF

echo "Generated config_params.h with:"
echo "  - NUM_ROCKET_CORES=$NUM_ROCKET_CORES"
echo "  - NUM_BOOM_CORES=$NUM_BOOM_CORES"
echo "  - TOTAL_CORES=$NUM_TOTAL_CORES"
echo "  - MATRIX_SIZE=$MATRIX_SIZE"
echo "  - KERNEL_SIZE=$KERNEL_SIZE"
echo "  - L1_DCACHE_SIZE=$L1_DCACHE_SIZE"
