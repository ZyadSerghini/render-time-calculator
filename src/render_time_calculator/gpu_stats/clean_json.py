import json
import re

# def extract_max(values):
#     numbers = re.findall(r"\d+", values)
#     if not numbers:
#         return None
#     return max(map(int, numbers))


# def convert_gib_to_mib(gib_value):
#     return gib_value * 1024  # 1 GiB = 1024 MiB


# def process_file(input_path, output_path):
#     with open(input_path) as f:
#         data = json.load(f)

#     for key, gpu in data.items():
#         if "Memory configuration Size (GiB)" in gpu:
#             raw = gpu["Memory configuration Size (GiB)"]

#             max_gib = extract_max(raw)
#             if max_gib is not None:
#                 gpu["Memory configuration Size (MiB)"] = convert_gib_to_mib(max_gib)
#                 del gpu["Memory configuration Size (GiB)"]

#     with open(output_path, "w") as f:
#         json.dump(data, f, indent=2)


# # usage
# process_file("gpu.json", "output.json")

# def convert_gt_to_mtexels(value):
#     if value is None:
#         return None

#     # ✅ Case 1: already numeric
#     if isinstance(value, (int, float)):
#         return value * 1000

#     # ✅ Case 2: string → extract number
#     if isinstance(value, str):
#         match = re.findall(r"\d+\.?\d*", value)
#         if not match:
#             return None
#         return float(match[0]) * 1000

#     return None


# def process_file(input_path, output_path):
#     with open(input_path) as f:
#         data = json.load(f)

#     for key, gpu in data.items():
#         if "Fillrate Texture (GT/s)" in gpu:
#             gt_value = gpu["Fillrate Texture (GT/s)"]

#             mtexels = convert_gt_to_mtexels(gt_value)

#             gpu["Fillrate Texture (MTexels/s)"] = mtexels
#             del gpu["Fillrate Texture (GT/s)"]

#     with open(output_path, "w") as f:
#         json.dump(data, f, indent=2)


# # usage
# process_file("cleaned_gpu_old.json", "cleaned_gpu.json")


# def convert_gp_to_mp(value):
#     """
#     Converts GP/s → MP/s
#     Handles float, int, and string values
#     """

#     if value is None:
#         return None

#     # Case 1: numeric
#     if isinstance(value, (int, float)):
#         return value * 1000

#     # Case 2: string
#     if isinstance(value, str):
#         # extract numbers (handles "10", "10.5", "10 12", "10/12")
#         numbers = re.findall(r"\d+\.?\d*", value)

#         if not numbers:
#             return value  # leave unchanged if nothing found

#         # convert each number
#         converted = [str(float(n) * 1000) for n in numbers]

#         return " ".join(converted)

#     return value


# def process_file(input_path, output_path):
#     with open(input_path) as f:
#         data = json.load(f)

#     for key, gpu in data.items():
#         if "Fillrate Pixel (GP/s)" in gpu:
#             gpu["Fillrate Pixel (GP/s)"] = convert_gp_to_mp(
#                 gpu["Fillrate Pixel (GP/s)"]
#             )

#     with open(output_path, "w") as f:
#         json.dump(data, f, indent=2)


# # Usage
# process_file("cleaned_gpu_oldd.json", "cleaned_gpu.json")

# def convert_gt_to_mhz(value):
#     """
#     Converts GT/s → MHz (×1000)
#     Handles int, float, and string cases
#     """
#     if value is None:
#         return None

#     # Case 1: numeric
#     if isinstance(value, (int, float)):
#         return value * 1000

#     # Case 2: string
#     if isinstance(value, str):
#         numbers = re.findall(r"\d+\.?\d*", value)
#         if not numbers:
#             return value

#         converted = [str(float(n) * 1000) for n in numbers]
#         return " ".join(converted)

#     return value


# def process_file(input_path, output_path):
#     with open(input_path) as f:
#         data = json.load(f)

#     for key, gpu in data.items():
#         if "Clock speeds Memory (GT/s)" in gpu:
#             value = gpu["Clock speeds Memory (GT/s)"]

#             new_value = convert_gt_to_mhz(value)

#             # replace key
#             gpu["Memory clock (MHz)"] = new_value
#             del gpu["Clock speeds Memory (GT/s)"]

#     with open(output_path, "w") as f:
#         json.dump(data, f, indent=2)


# # usage
# process_file("cleaned_gpu.json", "cleaned_gpu2.json")


# def convert_gib_to_mib(value):
#     """
#     Converts GiB → MiB (×1024)
#     Handles int, float, and string cases
#     """
#     if value is None:
#         return None

#     # Case 1: numeric
#     if isinstance(value, (int, float)):
#         return value * 1024

#     # Case 2: string
#     if isinstance(value, str):
#         numbers = re.findall(r"\d+\.?\d*", value)
#         if not numbers:
#             return value

#         converted = [str(float(n) * 1024) for n in numbers]
#         return " ".join(converted)

#     return value


# def process_file(input_path, output_path):
#     with open(input_path) as f:
#         data = json.load(f)

#     for key, gpu in data.items():
#         if "Memory Size (GiB)" in gpu:
#             value = gpu["Memory Size (GiB)"]

#             new_value = convert_gib_to_mib(value)

#             # replace key
#             gpu["Memory Size (MiB)"] = new_value
#             del gpu["Memory Size (GiB)"]

#     with open(output_path, "w") as f:
#         json.dump(data, f, indent=2)

# def extract_max_mhz(value):
#     """
#     Extracts MHz values from pattern:
#     "1375-1500 11-12 11-12 1375-1750 11-14 11-14"

#     Keeps only MHz (every 3rd value starting at index 0),
#     then returns the max.
#     """

#     if value is None:
#         return None

#     # Extract all numbers (including ranges like 1375-1500)
#     tokens = value.split()

#     mhz_values = []

#     for i in range(0, len(tokens), 3):  # every 3rd = MHz
#         part = tokens[i]

#         # handle ranges like "1375-1500"
#         numbers = re.findall(r"\d+\.?\d*", part)
#         if numbers:
#             mhz_values.extend([float(n) for n in numbers])

#     if not mhz_values:
#         return None

#     return max(mhz_values)


# def process_file(input_path, output_path):
#     with open(input_path) as f:
#         data = json.load(f)

#     for key, gpu in data.items():
#         if "Clock speeds Memory (MHz) (Gb/s) (GT/s)" in gpu:
#             raw_value = gpu["Clock speeds Memory (MHz) (Gb/s) (GT/s)"]

#             max_mhz = extract_max_mhz(raw_value)

#             if max_mhz is not None:
#                 gpu["Memory clock (MHz)"] = max_mhz

#             del gpu["Clock speeds Memory (MHz) (Gb/s) (GT/s)"]

#     with open(output_path, "w") as f:
#         json.dump(data, f, indent=2)


def convert_billion_to_million(value):
    """
    Converts billions → millions (×1000)
    Handles int, float, and string cases
    """
    if value is None:
        return None

    # Case 1: numeric
    if isinstance(value, (int, float)):
        return value * 1000

    # Case 2: string
    if isinstance(value, str):
        numbers = re.findall(r"\d+\.?\d*", value)
        if not numbers:
            return value

        converted = [str(float(n) * 1000) for n in numbers]
        return " ".join(converted)

    return value


def process_file(input_path, output_path):
    with open(input_path) as f:
        data = json.load(f)

    for key, gpu in data.items():
        if "Transistors (billion)" in gpu:
            value = gpu["Transistors (billion)"]

            new_value = convert_billion_to_million(value)

            gpu["Transistors (million)"] = new_value
            del gpu["Transistors (billion)"]

    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)


# usage
process_file("cleaned_gpuaa.json", "cleaned_gpu.json")
