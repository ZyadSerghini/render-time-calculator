import csv
import json

from render_time_calculator.handlers import (
    handleV1,
    handleV2,
    handleV3,
    handleV4,
)
from render_time_calculator.matching import (
    build_gpu_index,
    find_gpu_key,
)
from render_time_calculator.stats import (
    end_timer,
    load_stats,
    save_stats,
    start_timer,
)

GPU_READ_PATH = "data/processed/gpu-data.json"
WRITE_PATH = "data/processed/cleaned_data.csv"

DEBUG = {
    "nameMatching": True,
    "matchingPath": "data/debug/GPU_name_matching.csv",
    "nameNotMatching": True,
    "notMatchingPath": "data/debug/GPU_not_matching.csv",
    "loopLimit": False,
    "loopLimitVal": 1,
}
BENCHMARK_METRICS = ("renderTime", "renderedObject", "gpuName", "gpuBackend")
GPU_METRICS = (
    "releaseYear",
    "baseClock",
    "boostClock",
    "textureRate",
    "pixelRate",
    "architecture",
    "memoryType",
    "generation",
    "busInterface",
    "rtCores",
    "tensorCores",
)

HANDLERS = {
    "v1": handleV1,
    "v2": handleV2,
    "v3": handleV3,
    "v4": handleV4,
}


def process_benchmark_file(benchmark_read_path) -> None:
    start_timer()

    with open(file=GPU_READ_PATH) as gpu_datafile:
        gpu_data = json.load(gpu_datafile)

    benchmark_to_csv(benchmark_read_path, gpu_data)

    end_timer()


def benchmark_to_csv(filepath, gpu_data):
    stats = load_stats()

    if DEBUG["nameMatching"]:
        debug_file_match = open(DEBUG["matchingPath"], "w")
        debug_file_match.write("device_name,matched_key,score\n")

    if DEBUG["nameNotMatching"]:
        debug_file_nomatch = open(DEBUG["notMatchingPath"], "w")
        debug_file_nomatch.write("device_name,score\n")

    with open(filepath) as infile, open(WRITE_PATH, "w", newline="") as outfile:
        writer = csv.writer(outfile)
        writer.writerow(BENCHMARK_METRICS + GPU_METRICS)

        if DEBUG["loopLimit"]:
            counter = 1

        # content = ''
        match_cache = {}

        gpu_index = {}
        gpu_index = build_gpu_index(gpu_data)

        for line in infile:
            data = json.loads(line)
            schema_version = data["schema_version"]
            stats["totalAnalyzed"] += 1

            fieldAttributes = HANDLERS[schema_version](data)

            for entry in fieldAttributes:
                if entry["gpuBackend"] == "CPU":
                    continue
                stats["totalGPUAnalyzed"] += 1

                gpu_name = entry["gpuName"]
                if gpu_name in match_cache:
                    found_key, score, matched = match_cache[gpu_name]
                else:
                    found_key, score, matched = find_gpu_key(
                        gpu_name, gpu_data, gpu_index
                    )
                    match_cache[gpu_name] = (found_key, score, matched)

                if not matched:
                    stats["noMatch"] += 1
                    debug_file_nomatch.write(f"{gpu_name},{score}\n")
                    continue

                if score == 1:
                    stats["perfectMatch"] += 1
                else:
                    if DEBUG["nameMatching"]:
                        debug_file_match.write(f"{gpu_name},{found_key},{score}\n")
                    stats["guessedMatch"] += 1

                row = tuple(entry.values()) + tuple(gpu_data[found_key].values())
                writer.writerow(row)  # content += ','.join(map(str, row)) + '\n'

            if DEBUG["loopLimit"]:
                if counter == DEBUG["loopLimitVal"]:
                    break
                counter += 1

    save_stats(stats)

    if DEBUG["nameMatching"]:
        debug_file_match.close()
    if DEBUG["nameNotMatching"]:
        debug_file_nomatch.close()
