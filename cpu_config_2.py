# # import json
# # import sys
# # import subprocess
# # import multiprocessing
# # from pathlib import Path

# # class CPUConfigValidator:
# #     def __init__(self, json_data):
# #         self.json_data = json_data
# #         self.validate()

# #     def _is_power_of_two(self, n):
# #         """Check if a number is a power of two."""
# #         return (n != 0) and (n & (n - 1)) == 0

# #     def _validate_cache_set_size(self, sets, cache_name):
# #         """Validate that the cache size does not exceed 4 KiB."""
# #         block_size = 64  # Default cache block size in bytes
# #         set_size = sets * block_size
# #         if set_size > 4096:  # 4 KiB
# #             raise ValueError(
# #                 f"{cache_name} set size must not exceed 4 KiB; got {set_size // 1024} KiB. "
# #             )

# #     def validate(self):
# #         """Validate the JSON structure and content."""
# #         if "NAME" not in self.json_data:
# #             raise ValueError("Missing 'NAME' field in JSON.")
# #         if "ROCKET_CORES" not in self.json_data:
# #             raise ValueError("Missing 'ROCKET_CORES' field in JSON.")

# #         rocket_cores = self.json_data["ROCKET_CORES"]
# #         if not rocket_cores:
# #             raise ValueError("At least one Rocket core must be specified in 'ROCKET_CORES'.")

# #         for i, core in enumerate(rocket_cores):
# #             if "NUMBER" not in core:
# #                 raise ValueError(f"Missing 'NUMBER' field in Rocket core {i}.")
# #             if not isinstance(core["NUMBER"], int) or core["NUMBER"] <= 0:
# #                 raise ValueError(f"Invalid 'NUMBER' for Rocket core {i}. It must be an integer greater than 0.")

# #             if "L1I_CACHE" not in core:
# #                 raise ValueError(f"Missing 'L1I_CACHE' field in Rocket core {i}.")
# #             if "SETS" not in core["L1I_CACHE"] or "WAYS" not in core["L1I_CACHE"]:
# #                 raise ValueError(f"Missing 'SETS' or 'WAYS' in L1I_CACHE for Rocket core {i}.")
# #             if not self._is_power_of_two(core["L1I_CACHE"]["SETS"]):
# #                 raise ValueError(f"L1I_CACHE SETS for Rocket core {i} must be a power of 2.")
# #             if not self._is_power_of_two(core["L1I_CACHE"]["WAYS"]):
# #                 raise ValueError(f"L1I_CACHE WAYS for Rocket core {i} must be a power of 2.")

# #             if "L1D_CACHE" not in core:
# #                 raise ValueError(f"Missing 'L1D_CACHE' field in Rocket core {i}.")
# #             if "SETS" not in core["L1D_CACHE"] or "WAYS" not in core["L1D_CACHE"]:
# #                 raise ValueError(f"Missing 'SETS' or 'WAYS' in L1D_CACHE for Rocket core {i}.")
# #             if not self._is_power_of_two(core["L1D_CACHE"]["SETS"]):
# #                 raise ValueError(f"L1D_CACHE SETS for Rocket core {i} must be a power of 2.")
# #             if not self._is_power_of_two(core["L1D_CACHE"]["WAYS"]):
# #                 raise ValueError(f"L1D_CACHE WAYS for Rocket core {i} must be a power of 2.")

# #             # Validate L1D_CACHE size
# #             self._validate_cache_set_size(
# #                 core["L1D_CACHE"]["SETS"],
# #                 f"L1D_CACHE for Rocket core {i}"
# #             )

# #             if "USE_TLB" not in core:
# #                 raise ValueError(f"Missing 'USE_TLB' field in Rocket core {i}.")

# #         # Validate L2_CACHE
# #         if "L2_CACHE" not in self.json_data:
# #             raise ValueError("Missing 'L2_CACHE' field in JSON.")
# #         l2_cache = self.json_data["L2_CACHE"]
# #         if "WAYS" not in l2_cache or "CAPACITY_KB" not in l2_cache or "SUB_BANKING_FACTOR" not in l2_cache:
# #             raise ValueError("Missing 'WAYS', 'CAPACITY_KB', or 'SUB_BANKING_FACTOR' in L2_CACHE.")
# #         if not self._is_power_of_two(l2_cache["WAYS"]):
# #             raise ValueError("L2_CACHE WAYS must be a power of 2.")
# #         if not self._is_power_of_two(l2_cache["SUB_BANKING_FACTOR"]):
# #             raise ValueError("L2_CACHE SUB_BANKING_FACTOR must be a power of 2.")
# #         if not self._is_power_of_two(l2_cache["CAPACITY_KB"]):
# #             raise ValueError("L2_CACHE CAPACITY_KB must be a power of 2.")

# #     def get_config(self):
# #         """Return the validated JSON configuration."""
# #         return self.json_data


# # class ScalaFileGenerator:
# #     def __init__(self, config, chipyard_base_dir):
# #         self.config = config
# #         self.chipyard_base_dir = Path(chipyard_base_dir)
# #         self.scala_file_path = self._get_scala_file_path()
# #         self.class_name = None  # The class name for the Scala file

# #     def _get_scala_file_path(self):
# #         """Return the path to the Scala file based on the JSON configuration."""
# #         name = self.config["NAME"]
# #         return self.chipyard_base_dir / "generators" / "chipyard" / "src" / "main" / "scala" / "config" / f"{name}.scala"

# #     def _generate_imports(self):
# #         """Generate the imports section of the Scala file."""
# #         return """package chipyard

# # import chisel3.util._
# # import org.chipsalliance.cde.config._
# # import freechips.rocketchip.devices.debug._
# # import freechips.rocketchip.devices.tilelink._
# # import freechips.rocketchip.diplomacy._
# # import freechips.rocketchip.rocket._
# # import freechips.rocketchip.tile._
# # import freechips.rocketchip.util._
# # import freechips.rocketchip.subsystem._
# # import freechips.rocketchip.subsystem.RocketTileAttachParams

# # """

# #     def _generate_rocket_core_class(self, core, index):
# #         """Generate a class for a Rocket core configuration."""
# #         number = core["NUMBER"]
# #         l1i_sets = core["L1I_CACHE"]["SETS"]
# #         l1i_ways = core["L1I_CACHE"]["WAYS"]
# #         l1d_sets = core["L1D_CACHE"]["SETS"]
# #         l1d_ways = core["L1D_CACHE"]["WAYS"]
# #         use_tlb = core["USE_TLB"]

# #         # Default TLB values if USE_TLB is true
# #         tlb_sets = 1
# #         tlb_ways = 4

# #         class_definition = f"""class RocketCore_{index}(
# #   n: Int,
# #   crossing: RocketCrossingParams = RocketCrossingParams(),
# # ) extends Config((site, here, up) => {{
# #   case TilesLocated(InSubsystem) => {{
# #     val prev = up(TilesLocated(InSubsystem), site)
# #     val idOffset = up(NumTiles)
# #     val med = RocketTileParams(
# #       core = RocketCoreParams(useVM = {'true' if use_tlb else 'false'}, fpu = None),
# #       btb = None,
# #       dcache = Some(DCacheParams(
# #         rowBits = site(SystemBusKey).beatBits,
# #         nSets = {l1d_sets},
# #         nWays = {l1d_ways},
# #         nTLBSets = {tlb_sets},
# #         nTLBWays = {tlb_ways},
# #         nMSHRs = 0,
# #         blockBytes = site(CacheBlockBytes))),
# #       icache = Some(ICacheParams(
# #         rowBits = site(SystemBusKey).beatBits,
# #         nSets = {l1i_sets},
# #         nWays = {l1i_ways},
# #         nTLBSets = {tlb_sets},
# #         nTLBWays = {tlb_ways},
# #         blockBytes = site(CacheBlockBytes))))
# #     List.tabulate(n)(i => RocketTileAttachParams(
# #       med.copy(tileId = i + idOffset),
# #       crossing
# #     )) ++ prev
# #   }}
# #   case NumTiles => up(NumTiles) + n
# # }})
# # """
# #         return class_definition

# #     def _generate_main_class(self):
# #         """Generate the main configuration class."""
# #         name = self.config["NAME"]
# #         self.class_name = name + "Config"
# #         rocket_cores = self.config["ROCKET_CORES"]
# #         l2_cache = self.config["L2_CACHE"]

# #         main_class_definition = f"class {name}Config extends Config(\n"
# #         for i, core in enumerate(rocket_cores):
# #             main_class_definition += f"  new RocketCore_{i}({core['NUMBER']}) ++\n"
# #         main_class_definition += (
# #             f"  new freechips.rocketchip.subsystem.WithInclusiveCache("
# #             f"nWays={l2_cache['WAYS']}, capacityKB={l2_cache['CAPACITY_KB']}, "
# #             f"subBankingFactor={l2_cache['SUB_BANKING_FACTOR']}) ++\n"
# #         )
# #         main_class_definition += "  new chipyard.config.AbstractConfig\n)"
# #         return main_class_definition

# #     def generate_scala_file(self):
# #         """Generate and save the Scala file."""
# #         scala_content = self._generate_imports()

# #         # Generate Rocket core classes
# #         for i, core in enumerate(self.config["ROCKET_CORES"]):
# #             scala_content += self._generate_rocket_core_class(core, i) + "\n"

# #         # Generate the main configuration class
# #         scala_content += self._generate_main_class()

# #         # Ensure the directory exists
# #         self.scala_file_path.parent.mkdir(parents=True, exist_ok=True)

# #         # Write the Scala file
# #         with open(self.scala_file_path, "w") as file:
# #             file.write(scala_content)

# #         print(f"Scala file generated at: {self.scala_file_path}")


# # class CPUConfigurator:
# #     def __init__(self, json_file_path, chipyard_base_dir):
# #         self.json_file_path = json_file_path
# #         self.chipyard_base_dir = Path(chipyard_base_dir)
# #         self.json_data = self._load_json()
# #         self.validator = CPUConfigValidator(self.json_data)
# #         self.scala_generator = ScalaFileGenerator(self.validator.get_config(), self.chipyard_base_dir)

# #     def _load_json(self):
# #         """Load and return the JSON data from the file."""
# #         try:
# #             with open(self.json_file_path, "r") as file:
# #                 return json.load(file)
# #         except FileNotFoundError:
# #             raise FileNotFoundError(f"JSON file not found: {self.json_file_path}")
# #         except json.JSONDecodeError:
# #             raise ValueError(f"Invalid JSON format in file: {self.json_file_path}")

# #     def configure(self):
# #         """Process the validated configuration and generate the Scala file."""
# #         config = self.validator.get_config()
# #         print(f"Configuring CPU with name: {config['NAME']}")
# #         print(f"Chipyard base directory: {self.chipyard_base_dir}")
# #         print("Rocket core configurations:")
# #         for i, core in enumerate(config["ROCKET_CORES"]):
# #             print(f"  - Rocket Core {i}:")
# #             print(f"    - Number: {core['NUMBER']}")
# #             print(f"    - L1I Cache: Sets={core['L1I_CACHE']['SETS']}, Ways={core['L1I_CACHE']['WAYS']}")
# #             print(f"    - L1D Cache: Sets={core['L1D_CACHE']['SETS']}, Ways={core['L1D_CACHE']['WAYS']}")
# #             print(f"    - Use TLB: {core['USE_TLB']}")
# #         print("L2 Cache configuration:")
# #         print(f"  - Ways: {config['L2_CACHE']['WAYS']}")
# #         print(f"  - Capacity (KB): {config['L2_CACHE']['CAPACITY_KB']}")
# #         print(f"  - Sub-banking Factor: {config['L2_CACHE']['SUB_BANKING_FACTOR']}")

# #         # Generate the Scala file
# #         self.scala_generator.generate_scala_file()

# #     def highestPowerof2(self, x):
# #         """Find the highest power of 2 less than or equal to x."""
# #         if x <= 2:
# #             return 1
# #         if (x & (x - 1)) == 0:
# #             return x >> 1
# #         x |= x >> 1
# #         x |= x >> 2
# #         x |= x >> 4
# #         x |= x >> 8
# #         x |= x >> 16
# #         return x ^ (x >> 1)

# #     def build_verilog(self):
# #         """Build Verilog using the generated configuration."""
# #         if not self.scala_generator.class_name:
# #             raise ValueError("Scala file not generated. Run `configure()` first.")

# #         # Determine the number of threads to use
# #         num_cores = self.highestPowerof2(multiprocessing.cpu_count())

# #         # Change to the verilator directory
# #         verilator_dir = self.chipyard_base_dir / "sims" / "verilator"
# #         if not verilator_dir.exists():
# #             raise FileNotFoundError(f"Verilator directory not found: {verilator_dir}")

# #         # Log file path
# #         log_file = Path.cwd() / f"{self.json_data['NAME']}.out"

# #         # Run make clean
# #         print("Running `make clean`...")
# #         subprocess.run(["make", "clean"], cwd=verilator_dir, check=True)

# #         # Run make verilog
# #         print(f"Running `makex CONFIG={self.scala_generator.class_name} -j{num_cores}`...")
# #         with open(log_file, "w", encoding='utf-8') as log:
# #             result = subprocess.run(
# #                 ["make", "verilog", f"CONFIG={self.scala_generator.class_name}", f"-j{num_cores}"],
# #                 cwd=verilator_dir,
# #                 stdout=log,
# #                 stderr=subprocess.STDOUT,
# #                 text=True
# #             )

# #         if result.returncode == 0:
# #             print(f"Verilog build successful. Log saved to: {log_file}")
# #         else:
# #             print(f"Verilog build failed. Check log file: {log_file}")


# # def main():
# #     if len(sys.argv) != 3:
# #         print("Usage: python configure_cpu.py <json_file_path> <chipyard_base_dir>")
# #         sys.exit(1)

# #     json_file_path = sys.argv[2].strip()
# #     chipyard_base_dir = sys.argv[1].strip()

# #     try:
# #         configurator = CPUConfigurator(json_file_path, chipyard_base_dir)
# #         configurator.configure()
# #         configurator.build_verilog()
# #     except Exception as e:
# #         print(f"Error: {e}")
# #         sys.exit(1)


# # if __name__ == "__main__":
# #     main()
# import json
# import sys
# import subprocess
# import multiprocessing
# from pathlib import Path

# class CPUConfigValidator:
#     def __init__(self, json_data):
#         self.json_data = json_data
#         self.validate()

#     def _is_power_of_two(self, n):
#         """Check if a number is a power of two."""
#         return (n != 0) and (n & (n - 1)) == 0

#     def _validate_cache_set_size(self, sets, cache_name):
#         """Validate that the cache size does not exceed 4 KiB."""
#         block_size = 64  # Default cache block size in bytes
#         set_size = sets * block_size
#         if set_size > 4096:  # 4 KiB
#             raise ValueError(
#                 f"{cache_name} set size must not exceed 4 KiB; got {set_size // 1024} KiB. "
#             )

#     def validate(self):
#         """Validate the JSON structure and content."""
#         if "NAME" not in self.json_data:
#             raise ValueError("Missing 'NAME' field in JSON.")
#         if "ROCKET_CORES" not in self.json_data:
#             raise ValueError("Missing 'ROCKET_CORES' field in JSON.")

#         rocket_cores = self.json_data["ROCKET_CORES"]
#         if not rocket_cores:
#             raise ValueError("At least one Rocket core must be specified in 'ROCKET_CORES'.")

#         for i, core in enumerate(rocket_cores):
#             if "NUMBER" not in core:
#                 raise ValueError(f"Missing 'NUMBER' field in Rocket core {i}.")
#             if not isinstance(core["NUMBER"], int) or core["NUMBER"] <= 0:
#                 raise ValueError(f"Invalid 'NUMBER' for Rocket core {i}. It must be an integer greater than 0.")

#             if "L1I_CACHE" not in core:
#                 raise ValueError(f"Missing 'L1I_CACHE' field in Rocket core {i}.")
#             if "SETS" not in core["L1I_CACHE"] or "WAYS" not in core["L1I_CACHE"]:
#                 raise ValueError(f"Missing 'SETS' or 'WAYS' in L1I_CACHE for Rocket core {i}.")
#             if not self._is_power_of_two(core["L1I_CACHE"]["SETS"]):
#                 raise ValueError(f"L1I_CACHE SETS for Rocket core {i} must be a power of 2.")
#             if not self._is_power_of_two(core["L1I_CACHE"]["WAYS"]):
#                 raise ValueError(f"L1I_CACHE WAYS for Rocket core {i} must be a power of 2.")

#             if "L1D_CACHE" not in core:
#                 raise ValueError(f"Missing 'L1D_CACHE' field in Rocket core {i}.")
#             if "SETS" not in core["L1D_CACHE"] or "WAYS" not in core["L1D_CACHE"]:
#                 raise ValueError(f"Missing 'SETS' or 'WAYS' in L1D_CACHE for Rocket core {i}.")
#             if not self._is_power_of_two(core["L1D_CACHE"]["SETS"]):
#                 raise ValueError(f"L1D_CACHE SETS for Rocket core {i} must be a power of 2.")
#             if not self._is_power_of_two(core["L1D_CACHE"]["WAYS"]):
#                 raise ValueError(f"L1D_CACHE WAYS for Rocket core {i} must be a power of 2.")

#             # Validate L1D_CACHE size
#             self._validate_cache_set_size(
#                 core["L1D_CACHE"]["SETS"],
#                 f"L1D_CACHE for Rocket core {i}"
#             )

#             if "USE_TLB" not in core:
#                 raise ValueError(f"Missing 'USE_TLB' field in Rocket core {i}.")

#         # Validate L2_CACHE
#         if "L2_CACHE" not in self.json_data:
#             raise ValueError("Missing 'L2_CACHE' field in JSON.")
#         l2_cache = self.json_data["L2_CACHE"]
#         if "WAYS" not in l2_cache or "CAPACITY_KB" not in l2_cache or "SUB_BANKING_FACTOR" not in l2_cache:
#             raise ValueError("Missing 'WAYS', 'CAPACITY_KB', or 'SUB_BANKING_FACTOR' in L2_CACHE.")
#         if not self._is_power_of_two(l2_cache["WAYS"]):
#             raise ValueError("L2_CACHE WAYS must be a power of 2.")
#         if not self._is_power_of_two(l2_cache["SUB_BANKING_FACTOR"]):
#             raise ValueError("L2_CACHE SUB_BANKING_FACTOR must be a power of 2.")

#     def get_config(self):
#         """Return the validated JSON configuration."""
#         return self.json_data


# class ScalaFileGenerator:
#     def __init__(self, config, chipyard_base_dir):
#         self.config = config
#         self.chipyard_base_dir = Path(chipyard_base_dir)
#         self.scala_file_path = self._get_scala_file_path()
#         self.class_name = None  # The class name for the Scala file

#     def _get_scala_file_path(self):
#         """Return the path to the Scala file based on the JSON configuration."""
#         name = self.config["NAME"]
#         return self.chipyard_base_dir / "generators" / "chipyard" / "src" / "main" / "scala" / "config" / f"{name}.scala"

#     def _generate_imports(self):
#         """Generate the imports section of the Scala file."""
#         return """package chipyard

# import chisel3.util._
# import org.chipsalliance.cde.config._
# import freechips.rocketchip.devices.debug._
# import freechips.rocketchip.devices.tilelink._
# import freechips.rocketchip.diplomacy._
# import freechips.rocketchip.rocket._
# import freechips.rocketchip.tile._
# import freechips.rocketchip.util._
# import freechips.rocketchip.subsystem._
# import freechips.rocketchip.subsystem.RocketTileAttachParams

# """

#     def _generate_rocket_core_class(self, core, index):
#         """Generate a class for a Rocket core configuration."""
#         number = core["NUMBER"]
#         l1i_sets = core["L1I_CACHE"]["SETS"]
#         l1i_ways = core["L1I_CACHE"]["WAYS"]
#         l1d_sets = core["L1D_CACHE"]["SETS"]
#         l1d_ways = core["L1D_CACHE"]["WAYS"]
#         use_tlb = core["USE_TLB"]

#         # Default TLB values if USE_TLB is true
#         tlb_sets = 1
#         tlb_ways = 4

#         class_definition = f"""class RocketCore_{index}(
#   n: Int,
#   crossing: RocketCrossingParams = RocketCrossingParams(),
# ) extends Config((site, here, up) => {{
#   case TilesLocated(InSubsystem) => {{
#     val prev = up(TilesLocated(InSubsystem), site)
#     val idOffset = up(NumTiles)
#     val med = RocketTileParams(
#       core = RocketCoreParams(useVM = {'true' if use_tlb else 'false'}, fpu = None),
#       btb = None,
#       dcache = Some(DCacheParams(
#         rowBits = site(SystemBusKey).beatBits,
#         nSets = {l1d_sets},
#         nWays = {l1d_ways},
#         nTLBSets = {tlb_sets},
#         nTLBWays = {tlb_ways},
#         nMSHRs = 0,
#         blockBytes = site(CacheBlockBytes))),
#       icache = Some(ICacheParams(
#         rowBits = site(SystemBusKey).beatBits,
#         nSets = {l1i_sets},
#         nWays = {l1i_ways},
#         nTLBSets = {tlb_sets},
#         nTLBWays = {tlb_ways},
#         blockBytes = site(CacheBlockBytes))))
#     List.tabulate(n)(i => RocketTileAttachParams(
#       med.copy(tileId = i + idOffset),
#       crossing
#     )) ++ prev
#   }}
#   case NumTiles => up(NumTiles) + n
# }})
# """
#         return class_definition

#     def _generate_main_class(self):
#         """Generate the main configuration class."""
#         name = self.config["NAME"]
#         self.class_name = name + "Config"
#         rocket_cores = self.config["ROCKET_CORES"]
#         l2_cache = self.config["L2_CACHE"]

#         main_class_definition = f"class {name}Config extends Config(\n"
#         for i, core in enumerate(rocket_cores):
#             main_class_definition += f"  new RocketCore_{i}({core['NUMBER']}) ++\n"
#         main_class_definition += (
#             f"  new freechips.rocketchip.subsystem.WithInclusiveCache("
#             f"nWays={l2_cache['WAYS']}, capacityKB={l2_cache['CAPACITY_KB']}, "
#             f"subBankingFactor={l2_cache['SUB_BANKING_FACTOR']}) ++\n"
#         )
#         main_class_definition += "  new chipyard.config.AbstractConfig\n)"
#         return main_class_definition

#     def generate_scala_file(self):
#         """Generate and save the Scala file."""
#         scala_content = self._generate_imports()

#         # Generate Rocket core classes
#         for i, core in enumerate(self.config["ROCKET_CORES"]):
#             scala_content += self._generate_rocket_core_class(core, i) + "\n"

#         # Generate the main configuration class
#         scala_content += self._generate_main_class()

#         # Ensure the directory exists
#         self.scala_file_path.parent.mkdir(parents=True, exist_ok=True)

#         # Write the Scala file
#         with open(self.scala_file_path, "w") as file:
#             file.write(scala_content)

#         print(f"Scala file generated at: {self.scala_file_path}")


# class CPUConfigurator:
#     def __init__(self, json_file_path, chipyard_base_dir):
#         self.json_file_path = json_file_path
#         # self.chipyard_base_dir = Path(chipyard_base_dir)
#         self.chipyard_base_dir = chipyard_base_dir.resolve()  # Ensure absolute path
#         self.json_data = self._load_json()
#         self.validator = CPUConfigValidator(self.json_data)
#         self.scala_generator = ScalaFileGenerator(self.validator.get_config(), self.chipyard_base_dir)

#     def _load_json(self):
#         """Load and return the JSON data from the file."""
#         try:
#             with open(self.json_file_path, "r") as file:
#                 return json.load(file)
#         except FileNotFoundError:
#             raise FileNotFoundError(f"JSON file not found: {self.json_file_path}")
#         except json.JSONDecodeError:
#             raise ValueError(f"Invalid JSON format in file: {self.json_file_path}")

#     def configure(self):
#         """Process the validated configuration and generate the Scala file."""
#         config = self.validator.get_config()
#         print(f"Configuring CPU with name: {config['NAME']}")
#         print(f"Chipyard base directory: {self.chipyard_base_dir}")
#         print("Rocket core configurations:")
#         for i, core in enumerate(config["ROCKET_CORES"]):
#             print(f"  - Rocket Core {i}:")
#             print(f"    - Number: {core['NUMBER']}")
#             print(f"    - L1I Cache: Sets={core['L1I_CACHE']['SETS']}, Ways={core['L1I_CACHE']['WAYS']}")
#             print(f"    - L1D Cache: Sets={core['L1D_CACHE']['SETS']}, Ways={core['L1D_CACHE']['WAYS']}")
#             print(f"    - Use TLB: {core['USE_TLB']}")
#         print("L2 Cache configuration:")
#         print(f"  - Ways: {config['L2_CACHE']['WAYS']}")
#         print(f"  - Capacity (KB): {config['L2_CACHE']['CAPACITY_KB']}")
#         print(f"  - Sub-banking Factor: {config['L2_CACHE']['SUB_BANKING_FACTOR']}")

#         # Generate the Scala file
#         self.scala_generator.generate_scala_file()

#     def highestPowerof2(self, x):
#         """Find the highest power of 2 less than or equal to x."""
#         if x <= 2:
#             return 1
#         if (x & (x - 1)) == 0:
#             return x >> 1
#         x |= x >> 1
#         x |= x >> 2
#         x |= x >> 4
#         x |= x >> 8
#         x |= x >> 16
#         return x ^ (x >> 1)

#     def build_verilog(self):
#         """Build Verilog using the generated configuration."""
#         if not self.scala_generator.class_name:
#             raise ValueError("Scala file not generated. Run `configure()` first.")

#         # Determine the number of threads to use
#         num_cores = self.highestPowerof2(multiprocessing.cpu_count())

#         # Change to the verilator directory
#         verilator_dir = self.chipyard_base_dir / "sims" / "verilator"
#         if not verilator_dir.exists():
#             raise FileNotFoundError(f"Verilator directory not found: {verilator_dir}")

#         # Log file path
#         log_file = Path.cwd() / f"{self.json_data['NAME']}.out"

#         # Run make clean
#         print("Running `make clean`...")
#         subprocess.run(["make", "clean"], cwd=verilator_dir, check=True)

#         # Run make
#         print(f"Running `make CONFIG={self.scala_generator.class_name} -j{num_cores}`...")
#         with open(log_file, "w", encoding='utf-8') as log:
#             result = subprocess.run(
#                 ["make", f"CONFIG={self.scala_generator.class_name}", f"-j{num_cores}"],
#                 cwd=verilator_dir,
#                 stdout=log,
#                 stderr=subprocess.STDOUT,
#                 text=True
#             )

#         if result.returncode == 0:
#             print(f"Make successful. Log saved to: {log_file}")
#         else:
#             print(f"Make failed. Check log file: {log_file}")

#     def run_generate_config(self):
#         """Run the generate_config.sh script and makefile in the tests directory."""
#         # Resolve the chipyard base directory to an absolute path
#         chipyard_base_dir = self.chipyard_base_dir.resolve()
#         tests_dir = chipyard_base_dir / "tests"
#         if not tests_dir.exists():
#             raise FileNotFoundError(f"Tests directory not found: {tests_dir}")

#         # Path to the generated JSON file
#         json_file = (
#             chipyard_base_dir / "sims" / "verilator" / "generated-src" /
#             f"chipyard.harness.TestHarness.{self.json_data['NAME']}Config" /
#             f"chipyard.harness.TestHarness.{self.json_data['NAME']}Config.json"
#         )
#         if not json_file.exists():
#             raise FileNotFoundError(f"Generated JSON file not found: {json_file}")

#         # Calculate the minimum L1 data cache size (in KB) across all Rocket cores
#         l1_dcache_sizes = []
#         for core in self.json_data["ROCKET_CORES"]:
#             sets = core["L1D_CACHE"]["SETS"]
#             ways = core["L1D_CACHE"]["WAYS"]
#             block_size = 64  # Default cache block size in bytes
#             cache_size_bytes = sets * ways * block_size
#             l1_dcache_sizes.append(cache_size_bytes)

#         min_l1_dcache_size = min(l1_dcache_sizes)

#         # Run generate_config.sh
#         generate_config_script = tests_dir / "generate_config.sh"
#         if not generate_config_script.exists():
#             raise FileNotFoundError(f"generate_config.sh not found: {generate_config_script}")

#         print(f"Running {generate_config_script}...")
#         subprocess.run(
#             [
#                 str(generate_config_script),
#                 str(json_file),  # Pass the JSON file path directly as the first argument
#                 "4",             # MATRIX_SIZE
#                 "3",             # KERNEL_SIZE
#                 str(min_l1_dcache_size)  # L1_DCACHE_SIZE in Bytes
#             ],
#             cwd=tests_dir,
#             check=True
#         )

#         # Run makefile in the tests directory
#         print ("Running 'make clean' in tests directory...")
#         subprocess.run(["make", "clean"], cwd=tests_dir, check=True)
#         print("Running makefile in tests directory...")
#         subprocess.run(["make"], cwd=tests_dir, check=True)


#     def run_spike(self):
#         """Run the generated RISC-V binaries using Spike and print the results."""
#         # Navigate to the tests directory
#         tests_dir = self.chipyard_base_dir / "tests"
#         if not tests_dir.exists():
#             raise FileNotFoundError(f"Tests directory not found: {tests_dir}")

#         # Paths to the generated binaries
#         matrix_mult_binary = tests_dir / "matrix_mult.riscv"
#         conv_benchmark_binary = tests_dir / "conv_bench.riscv"

#         # Check if the binaries exist
#         if not matrix_mult_binary.exists():
#             raise FileNotFoundError(f"Binary not found: {matrix_mult_binary}")
#         if not conv_benchmark_binary.exists():
#             raise FileNotFoundError(f"Binary not found: {conv_benchmark_binary}")

#         # Run matrix_mult.riscv with Spike and print output
#         print("Running matrix_mult.riscv with Spike...")
#         try:
#             result_matrix_mult = subprocess.run(
#                 ["spike", "pk", str(matrix_mult_binary)],
#                 cwd=tests_dir,
#                 check=True,
#                 text=True,
#                 capture_output=True
#             )
#             print(result_matrix_mult.stdout)  # Print the output of the command
#         except subprocess.CalledProcessError as e:
#             print(f"Error running matrix_mult.riscv: {e}")
#             print(e.stderr)  # Print the error output if the command fails

#         # Run conv_benchmark.riscv with Spike and print output
#         print("Running conv_benchmark.riscv with Spike...")
#         try:
#             result_conv_bench = subprocess.run(
#                 ["spike", "pk", str(conv_benchmark_binary)],
#                 cwd=tests_dir,
#                 check=True,
#                 text=True,
#                 capture_output=True
#             )
#             print(result_conv_bench.stdout)  # Print the output of the command
#         except subprocess.CalledProcessError as e:
#             print(f"Error running conv_benchmark.riscv: {e}")
#             print(e.stderr)  # Print the error output if the command fails

# def main():
#     if len(sys.argv) != 3:
#         print("Usage: python configure_cpu.py <json_file_path> <chipyard_base_dir>")
#         sys.exit(1)

#     # json_file_path = sys.argv[2].strip()
#     # chipyard_base_dir = sys.argv[1].strip()
#     json_file_path = Path(sys.argv[2].strip()).resolve()
#     chipyard_base_dir = Path(sys.argv[1].strip()).resolve()

#     try:
#         configurator = CPUConfigurator(json_file_path, chipyard_base_dir)
#         configurator.configure()
#         configurator.build_verilog()
#         configurator.run_generate_config()
#         configurator.run_spike()  # Run Spike on the generated binaries
#     except Exception as e:
#         print(f"Error: {e}")
#         sys.exit(1)


# if __name__ == "__main__":
#     main()
import json
import sys
import subprocess
import multiprocessing
from pathlib import Path

class CPUConfigValidator:
    def __init__(self, json_data):
        self.json_data = json_data
        self.validate()

    def _is_power_of_two(self, n):
        """Check if a number is a power of two."""
        return (n != 0) and (n & (n - 1)) == 0

    def _validate_cache_set_size(self, sets, cache_name):
        """Validate that the cache size does not exceed 4 KiB."""
        block_size = 64  # Default cache block size in bytes
        set_size = sets * block_size
        if set_size > 4096:  # 4 KiB
            raise ValueError(
                f"{cache_name} set size must not exceed 4 KiB; got {set_size // 1024} KiB. "
            )

    def validate(self):
        """Validate the JSON structure and content."""
        if "NAME" not in self.json_data:
            raise ValueError("Missing 'NAME' field in JSON.")

        # Ensure at least one of ROCKET_CORES or BOOM_CORES is present
        if "ROCKET_CORES" not in self.json_data and "BOOM_CORES" not in self.json_data:
            raise ValueError("At least one of 'ROCKET_CORES' or 'BOOM_CORES' must be specified.")

        # Validate ROCKET_CORES if present
        if "ROCKET_CORES" in self.json_data:
            rocket_cores = self.json_data["ROCKET_CORES"]
            if not rocket_cores:
                raise ValueError("At least one Rocket core must be specified in 'ROCKET_CORES'.")

            for i, core in enumerate(rocket_cores):
                if "NUMBER" not in core:
                    raise ValueError(f"Missing 'NUMBER' field in Rocket core {i}.")
                if not isinstance(core["NUMBER"], int) or core["NUMBER"] <= 0:
                    raise ValueError(f"Invalid 'NUMBER' for Rocket core {i}. It must be an integer greater than 0.")

                if "L1I_CACHE" not in core:
                    raise ValueError(f"Missing 'L1I_CACHE' field in Rocket core {i}.")
                if "SETS" not in core["L1I_CACHE"] or "WAYS" not in core["L1I_CACHE"]:
                    raise ValueError(f"Missing 'SETS' or 'WAYS' in L1I_CACHE for Rocket core {i}.")
                if not self._is_power_of_two(core["L1I_CACHE"]["SETS"]):
                    raise ValueError(f"L1I_CACHE SETS for Rocket core {i} must be a power of 2.")
                if not self._is_power_of_two(core["L1I_CACHE"]["WAYS"]):
                    raise ValueError(f"L1I_CACHE WAYS for Rocket core {i} must be a power of 2.")

                if "L1D_CACHE" not in core:
                    raise ValueError(f"Missing 'L1D_CACHE' field in Rocket core {i}.")
                if "SETS" not in core["L1D_CACHE"] or "WAYS" not in core["L1D_CACHE"]:
                    raise ValueError(f"Missing 'SETS' or 'WAYS' in L1D_CACHE for Rocket core {i}.")
                if not self._is_power_of_two(core["L1D_CACHE"]["SETS"]):
                    raise ValueError(f"L1D_CACHE SETS for Rocket core {i} must be a power of 2.")
                if not self._is_power_of_two(core["L1D_CACHE"]["WAYS"]):
                    raise ValueError(f"L1D_CACHE WAYS for Rocket core {i} must be a power of 2.")

                # Validate L1D_CACHE size
                self._validate_cache_set_size(
                    core["L1D_CACHE"]["SETS"],
                    f"L1D_CACHE for Rocket core {i}"
                )

                if "USE_TLB" not in core:
                    raise ValueError(f"Missing 'USE_TLB' field in Rocket core {i}.")

        # Validate BOOM_CORES if present
        if "BOOM_CORES" in self.json_data:
            boom_cores = self.json_data["BOOM_CORES"]
            if not boom_cores:
                raise ValueError("At least one BOOM core must be specified in 'BOOM_CORES'.")

            for i, core in enumerate(boom_cores):
                if "NUMBER" not in core:
                    raise ValueError(f"Missing 'NUMBER' field in BOOM core {i}.")
                if not isinstance(core["NUMBER"], int) or core["NUMBER"] <= 0:
                    raise ValueError(f"Invalid 'NUMBER' for BOOM core {i}. It must be an integer greater than 0.")

                if "L1_ICACHE" not in core:
                    raise ValueError(f"Missing 'L1_ICACHE' field in BOOM core {i}.")
                if "SETS" not in core["L1_ICACHE"] or "WAYS" not in core["L1_ICACHE"]:
                    raise ValueError(f"Missing 'SETS' or 'WAYS' in L1_ICACHE for BOOM core {i}.")
                if not self._is_power_of_two(core["L1_ICACHE"]["SETS"]):
                    raise ValueError(f"L1_ICACHE SETS for BOOM core {i} must be a power of 2.")
                if not self._is_power_of_two(core["L1_ICACHE"]["WAYS"]):
                    raise ValueError(f"L1_ICACHE WAYS for BOOM core {i} must be a power of 2.")

                if "L1_DCACHE" not in core:
                    raise ValueError(f"Missing 'L1_DCACHE' field in BOOM core {i}.")
                if "SETS" not in core["L1_DCACHE"] or "WAYS" not in core["L1_DCACHE"]:
                    raise ValueError(f"Missing 'SETS' or 'WAYS' in L1_DCACHE for BOOM core {i}.")
                if not self._is_power_of_two(core["L1_DCACHE"]["SETS"]):
                    raise ValueError(f"L1_DCACHE SETS for BOOM core {i} must be a power of 2.")
                if not self._is_power_of_two(core["L1_DCACHE"]["WAYS"]):
                    raise ValueError(f"L1_DCACHE WAYS for BOOM core {i} must be a power of 2.")

                if "USE_TLB" not in core:
                    raise ValueError(f"Missing 'USE_TLB' field in BOOM core {i}.")

        # Validate L2_CACHE
        if "L2_CACHE" not in self.json_data:
            raise ValueError("Missing 'L2_CACHE' field in JSON.")
        l2_cache = self.json_data["L2_CACHE"]
        if "WAYS" not in l2_cache or "CAPACITY_KB" not in l2_cache or "SUB_BANKING_FACTOR" not in l2_cache:
            raise ValueError("Missing 'WAYS', 'CAPACITY_KB', or 'SUB_BANKING_FACTOR' in L2_CACHE.")
        if not self._is_power_of_two(l2_cache["WAYS"]):
            raise ValueError("L2_CACHE WAYS must be a power of 2.")
        if not self._is_power_of_two(l2_cache["SUB_BANKING_FACTOR"]):
            raise ValueError("L2_CACHE SUB_BANKING_FACTOR must be a power of 2.")

    def get_config(self):
        """Return the validated JSON configuration."""
        return self.json_data


class ScalaFileGenerator:
    def __init__(self, config, chipyard_base_dir):
        self.config = config
        self.chipyard_base_dir = Path(chipyard_base_dir)
        self.scala_file_path = self._get_scala_file_path()
        self.class_name = None  # The class name for the Scala file

    def _get_scala_file_path(self):
        """Return the path to the Scala file based on the JSON configuration."""
        name = self.config["NAME"]
        return self.chipyard_base_dir / "generators" / "chipyard" / "src" / "main" / "scala" / "config" / f"{name}.scala"

    def _generate_imports(self):
        """Generate the imports section of the Scala file."""
        return """package chipyard

import chisel3.util._
import org.chipsalliance.cde.config._
import freechips.rocketchip.devices.debug._
import freechips.rocketchip.devices.tilelink._
import freechips.rocketchip.diplomacy._
import freechips.rocketchip.rocket._
import freechips.rocketchip.tile._
import freechips.rocketchip.util._
import freechips.rocketchip.subsystem._
import freechips.rocketchip.subsystem.RocketTileAttachParams
import boom.common._
import boom.ifu._
import boom.exu._
import boom.lsu._

"""

    def _generate_rocket_core_class(self, core, index):
        """Generate a class for a Rocket core configuration."""
        number = core["NUMBER"]
        l1i_sets = core["L1I_CACHE"]["SETS"]
        l1i_ways = core["L1I_CACHE"]["WAYS"]
        l1d_sets = core["L1D_CACHE"]["SETS"]
        l1d_ways = core["L1D_CACHE"]["WAYS"]
        use_tlb = core["USE_TLB"]

        # Default TLB values if USE_TLB is true
        tlb_sets = 1
        tlb_ways = 4

        class_definition = f"""class RocketCore_{index}(
  n: Int,
  crossing: RocketCrossingParams = RocketCrossingParams(),
) extends Config((site, here, up) => {{
  case TilesLocated(InSubsystem) => {{
    val prev = up(TilesLocated(InSubsystem), site)
    val idOffset = up(NumTiles)
    val med = RocketTileParams(
      core = RocketCoreParams(useVM = {'true' if use_tlb else 'false'}, fpu = None),
      btb = None,
      dcache = Some(DCacheParams(
        rowBits = site(SystemBusKey).beatBits,
        nSets = {l1d_sets},
        nWays = {l1d_ways},
        nTLBSets = {tlb_sets},
        nTLBWays = {tlb_ways},
        nMSHRs = 0,
        blockBytes = site(CacheBlockBytes))),
      icache = Some(ICacheParams(
        rowBits = site(SystemBusKey).beatBits,
        nSets = {l1i_sets},
        nWays = {l1i_ways},
        nTLBSets = {tlb_sets},
        nTLBWays = {tlb_ways},
        blockBytes = site(CacheBlockBytes))))
    List.tabulate(n)(i => RocketTileAttachParams(
      med.copy(tileId = i + idOffset),
      crossing
    )) ++ prev
  }}
  case NumTiles => up(NumTiles) + n
}})
"""
        return class_definition

    def _generate_boom_core_class(self, core, index):
        """Generate a class for a BOOM core configuration."""
        number = core["NUMBER"]
        l1i_sets = core["L1_ICACHE"]["SETS"]
        l1i_ways = core["L1_ICACHE"]["WAYS"]
        l1d_sets = core["L1_DCACHE"]["SETS"]
        l1d_ways = core["L1_DCACHE"]["WAYS"]
        use_tlb = core["USE_TLB"]

        class_definition = f"""class BoomCore_{index}(n: Int = 1) extends Config(
  new WithTAGELBPD ++ // Default to TAGE-L BPD
  new Config((site, here, up) => {{
    case TilesLocated(InSubsystem) => {{
      val prev = up(TilesLocated(InSubsystem), site)
      val idOffset = up(NumTiles)
      (0 until n).map {{ i =>
        BoomTileAttachParams(
          tileParams = BoomTileParams(
            core = BoomCoreParams(
              fetchWidth = 8,
              decodeWidth = 3,
              numRobEntries = 96,
              issueParams = Seq(
                IssueParams(issueWidth=1, numEntries=16, iqType=IQT_MEM.litValue, dispatchWidth=3),
                IssueParams(issueWidth=3, numEntries=32, iqType=IQT_INT.litValue, dispatchWidth=3),
                IssueParams(issueWidth=1, numEntries=24, iqType=IQT_FP.litValue , dispatchWidth=3)),
              numIntPhysRegisters = 100,
              numFpPhysRegisters = 96,
              numLdqEntries = 24,
              numStqEntries = 24,
              maxBrCount = 16,
              numFetchBufferEntries = 24,
              ftq = FtqParameters(nEntries=32),
              fpu = Some(freechips.rocketchip.tile.FPUParams(sfmaLatency=4, dfmaLatency=4, divSqrt=true))
            ),
            dcache = Some(
              DCacheParams(rowBits = 128, nSets={l1d_sets}, nWays={l1d_ways}, nMSHRs=4, nTLBWays=16)
            ),
            icache = Some(
              ICacheParams(rowBits = 128, nSets={l1i_sets}, nWays={l1i_ways}, fetchBytes=4*4)
            ),
            tileId = i + idOffset
          ),
          crossingParams = RocketCrossingParams()
        )
      }} ++ prev
    }}
    case XLen => 64
    case NumTiles => up(NumTiles) + n
  }})
)
"""
        return class_definition

    def _generate_main_class(self):
        """Generate the main configuration class."""
        name = self.config["NAME"]
        self.class_name = name + "Config"
        rocket_cores = self.config.get("ROCKET_CORES", [])
        boom_cores = self.config.get("BOOM_CORES", [])
        l2_cache = self.config["L2_CACHE"]

        main_class_definition = f"class {name}Config extends Config(\n"
        for i, core in enumerate(rocket_cores):
            main_class_definition += f"  new RocketCore_{i}({core['NUMBER']}) ++\n"
        for i, core in enumerate(boom_cores):
            main_class_definition += f"  new BoomCore_{i}({core['NUMBER']}) ++\n"
        main_class_definition += (
            f"  new freechips.rocketchip.subsystem.WithInclusiveCache("
            f"nWays={l2_cache['WAYS']}, capacityKB={l2_cache['CAPACITY_KB']}, "
            f"subBankingFactor={l2_cache['SUB_BANKING_FACTOR']}) ++\n"
        )
        main_class_definition += "  new chipyard.config.AbstractConfig\n)"
        return main_class_definition

    def generate_scala_file(self):
        """Generate and save the Scala file."""
        scala_content = self._generate_imports()

        # Generate Rocket core classes
        for i, core in enumerate(self.config.get("ROCKET_CORES", [])):
            scala_content += self._generate_rocket_core_class(core, i) + "\n"

        # Generate BOOM core classes
        for i, core in enumerate(self.config.get("BOOM_CORES", [])):
            scala_content += self._generate_boom_core_class(core, i) + "\n"

        # Generate the main configuration class
        scala_content += self._generate_main_class()

        # Ensure the directory exists
        self.scala_file_path.parent.mkdir(parents=True, exist_ok=True)

        # Write the Scala file
        with open(self.scala_file_path, "w") as file:
            file.write(scala_content)

        print(f"Scala file generated at: {self.scala_file_path}")


class CPUConfigurator:
    def __init__(self, json_file_path, chipyard_base_dir):
        self.json_file_path = json_file_path
        self.chipyard_base_dir = Path(chipyard_base_dir).resolve()
        self.json_data = self._load_json()
        self.validator = CPUConfigValidator(self.json_data)
        self.scala_generator = ScalaFileGenerator(self.validator.get_config(), self.chipyard_base_dir)

    def _load_json(self):
        """Load and return the JSON data from the file."""
        try:
            with open(self.json_file_path, "r") as file:
                return json.load(file)
        except FileNotFoundError:
            raise FileNotFoundError(f"JSON file not found: {self.json_file_path}")
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON format in file: {self.json_file_path}")

    def configure(self):
        """Process the validated configuration and generate the Scala file."""
        config = self.validator.get_config()
        print(f"Configuring CPU with name: {config['NAME']}")
        print(f"Chipyard base directory: {self.chipyard_base_dir}")

        if "ROCKET_CORES" in config:
            print("Rocket core configurations:")
            for i, core in enumerate(config["ROCKET_CORES"]):
                print(f"  - Rocket Core {i}:")
                print(f"    - Number: {core['NUMBER']}")
                print(f"    - L1I Cache: Sets={core['L1I_CACHE']['SETS']}, Ways={core['L1I_CACHE']['WAYS']}")
                print(f"    - L1D Cache: Sets={core['L1D_CACHE']['SETS']}, Ways={core['L1D_CACHE']['WAYS']}")
                print(f"    - Use TLB: {core['USE_TLB']}")

        if "BOOM_CORES" in config:
            print("BOOM core configurations:")
            for i, core in enumerate(config["BOOM_CORES"]):
                print(f"  - BOOM Core {i}:")
                print(f"    - Number: {core['NUMBER']}")
                print(f"    - L1I Cache: Sets={core['L1_ICACHE']['SETS']}, Ways={core['L1_ICACHE']['WAYS']}")
                print(f"    - L1D Cache: Sets={core['L1_DCACHE']['SETS']}, Ways={core['L1_DCACHE']['WAYS']}")
                print(f"    - Use TLB: {core['USE_TLB']}")

        print("L2 Cache configuration:")
        print(f"  - Ways: {config['L2_CACHE']['WAYS']}")
        print(f"  - Capacity (KB): {config['L2_CACHE']['CAPACITY_KB']}")
        print(f"  - Sub-banking Factor: {config['L2_CACHE']['SUB_BANKING_FACTOR']}")

        # Generate the Scala file
        self.scala_generator.generate_scala_file()

    def highestPowerof2(self, x):
        """Find the highest power of 2 less than or equal to x."""
        if x <= 2:
            return 1
        if (x & (x - 1)) == 0:
            return x >> 1
        x |= x >> 1
        x |= x >> 2
        x |= x >> 4
        x |= x >> 8
        x |= x >> 16
        return x ^ (x >> 1)

    def build_verilog(self):
        """Build Verilog using the generated configuration."""
        if not self.scala_generator.class_name:
            raise ValueError("Scala file not generated. Run `configure()` first.")

        # Determine the number of threads to use
        num_cores = self.highestPowerof2(multiprocessing.cpu_count())

        # Change to the verilator directory
        verilator_dir = self.chipyard_base_dir / "sims" / "verilator"
        if not verilator_dir.exists():
            raise FileNotFoundError(f"Verilator directory not found: {verilator_dir}")

        # Log file path
        log_file = Path.cwd() / f"{self.json_data['NAME']}.out"

        # Run make clean
        print("Running `make clean`...")
        subprocess.run(["make", "clean"], cwd=verilator_dir, check=True)

        # Run make
        print(f"Running `make CONFIG={self.scala_generator.class_name} -j{num_cores}`...")
        with open(log_file, "w", encoding='utf-8') as log:
            result = subprocess.run(
                ["make", f"CONFIG={self.scala_generator.class_name}", f"-j{num_cores}"],
                cwd=verilator_dir,
                stdout=log,
                stderr=subprocess.STDOUT,
                text=True
            )

        if result.returncode == 0:
            print(f"Make successful. Log saved to: {log_file}")
        else:
            print(f"Make failed. Check log file: {log_file}")

    def run_generate_config(self):
        """Run the generate_config.sh script and makefile in the tests directory."""
        tests_dir = self.chipyard_base_dir / "tests"
        if not tests_dir.exists():
            raise FileNotFoundError(f"Tests directory not found: {tests_dir}")

        # Path to the generated JSON file
        json_file = (
            self.chipyard_base_dir / "sims" / "verilator" / "generated-src" /
            f"chipyard.harness.TestHarness.{self.json_data['NAME']}Config" /
            f"chipyard.harness.TestHarness.{self.json_data['NAME']}Config.json"
        )
        if not json_file.exists():
            raise FileNotFoundError(f"Generated JSON file not found: {json_file}")

        # Calculate the minimum L1 data cache size (in KB) across all Rocket cores
        l1_dcache_sizes = []
        for core in self.json_data.get("ROCKET_CORES", []):
            sets = core["L1D_CACHE"]["SETS"]
            ways = core["L1D_CACHE"]["WAYS"]
            block_size = 64  # Default cache block size in bytes
            cache_size_bytes = sets * ways * block_size
            l1_dcache_sizes.append(cache_size_bytes)

        min_l1_dcache_size = min(l1_dcache_sizes)

        # Run generate_config.sh
        generate_config_script = tests_dir / "generate_config.sh"
        if not generate_config_script.exists():
            raise FileNotFoundError(f"generate_config.sh not found: {generate_config_script}")

        print(f"Running {generate_config_script}...")
        subprocess.run(
            [
                str(generate_config_script),
                str(json_file),  # Pass the JSON file path directly as the first argument
                "4",             # MATRIX_SIZE
                "3",             # KERNEL_SIZE
                str(min_l1_dcache_size)  # L1_DCACHE_SIZE in Bytes
            ],
            cwd=tests_dir,
            check=True
        )

        # Run makefile in the tests directory
        print("Running 'make clean' in tests directory...")
        subprocess.run(["make", "clean"], cwd=tests_dir, check=True)
        print("Running makefile in tests directory...")
        subprocess.run(["make"], cwd=tests_dir, check=True)

    def run_spike(self):
        """Run the generated RISC-V binaries using Spike and print the results."""
        tests_dir = self.chipyard_base_dir / "tests"
        if not tests_dir.exists():
            raise FileNotFoundError(f"Tests directory not found: {tests_dir}")

        # Paths to the generated binaries
        matrix_mult_binary = tests_dir / "matrix_mult.riscv"
        conv_benchmark_binary = tests_dir / "conv_bench.riscv"

        # Check if the binaries exist
        if not matrix_mult_binary.exists():
            raise FileNotFoundError(f"Binary not found: {matrix_mult_binary}")
        if not conv_benchmark_binary.exists():
            raise FileNotFoundError(f"Binary not found: {conv_benchmark_binary}")

        # Run matrix_mult.riscv with Spike and print output
        print("Running matrix_mult.riscv with Spike...")
        try:
            result_matrix_mult = subprocess.run(
                ["spike", "pk", str(matrix_mult_binary)],
                cwd=tests_dir,
                check=True,
                text=True,
                capture_output=True
            )
            print(result_matrix_mult.stdout)  # Print the output of the command
        except subprocess.CalledProcessError as e:
            print(f"Error running matrix_mult.riscv: {e}")
            print(e.stderr)  # Print the error output if the command fails

        # Run conv_benchmark.riscv with Spike and print output
        print("Running conv_benchmark.riscv with Spike...")
        try:
            result_conv_bench = subprocess.run(
                ["spike", "pk", str(conv_benchmark_binary)],
                cwd=tests_dir,
                check=True,
                text=True,
                capture_output=True
            )
            print(result_conv_bench.stdout)  # Print the output of the command
        except subprocess.CalledProcessError as e:
            print(f"Error running conv_benchmark.riscv: {e}")
            print(e.stderr)  # Print the error output if the command fails


def main():
    if len(sys.argv) != 3:
        print("Usage: python configure_cpu.py <json_file_path> <chipyard_base_dir>")
        sys.exit(1)

    json_file_path = Path(sys.argv[2].strip()).resolve()
    chipyard_base_dir = Path(sys.argv[1].strip()).resolve()

    try:
        configurator = CPUConfigurator(json_file_path, chipyard_base_dir)
        configurator.configure()
        configurator.build_verilog()
        configurator.run_generate_config()
        configurator.run_spike()  # Run Spike on the generated binaries
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()