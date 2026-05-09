import json

from matching import find_gpu_key

from render_time_calculator.stats.stats import (
    end_timer,
    load_stats,
    save_stats,
    start_timer,
)

BENCHMARK_READ_PATH = "data/raw/benchmark-input-files/opendata-2026-04-10-000000+0000.jsonl"
GPU_READ_PATH = "data/processed/gpu-data.json"
WRITE_PATH = "data/processed/cleaned_data.csv"

DEBUG = {
    "nameMatching": False,
    "loopLimit": False,
    "loopLimitVal": 1000
}
DEBUG_PATH = "data/debug/GPU_name_matching.csv"

METRICS = ['render_time_no_sync']


def main() -> None:

    start_timer()
    stats = load_stats()

    if DEBUG["nameMatching"]:
        debug_file = open(DEBUG_PATH, 'w')
        debug_file.write('device_name,matched_key,score\n')

    with open(file=GPU_READ_PATH) as gpu_datafile:
        GPUs = json.load(gpu_datafile)

    with open(BENCHMARK_READ_PATH) as infile, open(WRITE_PATH, 'w') as outfile:

        outfile.write("heading\n")

        if DEBUG["loopLimit"]:
            counter = 1

        for line in infile:

            data = json.loads(line)
            if data["schema_version"] != 'v3':
                continue

            device_name = data['data'][0]["device_info"]["compute_devices"][0]["name"]
            device_type = data['data'][0]["device_info"]["device_type"]

            stats["totalAnalyzed"] += 1

            if device_type == "CPU":
                continue
            stats["totalGPUAnalyzed"] += 1

            found_key, score = find_gpu_key(device_name, GPUs)
            if score == 1:
                stats["perfectMatch"] += 1

            elif score != 1 and found_key:
                if DEBUG["nameMatching"]:
                    debug_file.write(f'{device_name},{found_key},{score}\n')  # print(f'{device_name}///{found_key} {score}')

                stats["guessedMatch"] += 1

            if DEBUG["loopLimit"]:
                if counter == DEBUG["loopLimitVal"]:
                    break
                counter += 1

    end_timer()
    save_stats(stats)

    if DEBUG["nameMatching"]:
        debug_file.close()


if __name__ == '__main__':
    main()


json_entry = {
    "created_at": "2021-02-09T07:53:10.072659+00:00",
    "data": [
        {
            "benchmark_launcher": {
                "label": "2.0.4"
            },
            "benchmark_script": {
                "label": "2.0.1"
            },
            "blender_version": {
                "version": "2.91.2",
                "build_date": "2021-01-19",
                "build_hash": "5be9ef417703"
            },
            "device_info": {
                "device_type": "CPU",
                "num_cpu_threads": 8,
                "compute_devices": [
                    {"name": "AMD Ryzen 3 3100", "type": "CPU"}
                ]
            },
            "scene": {
                "label": "bmw27"
            },
            "stats": {
                "render_time_no_sync": 384.355,
                "total_render_time": 384.782,
                "device_peak_memory": 144.22
            },
            "system_info": {
                "system": "Windows",
                "machine": "AMD64",
                "num_cpu_cores": 4,
                "num_cpu_threads": 8,
                "devices": [
                    {"name": "AMD Ryzen 3 3100", "type": "CPU"},
                    {"name": "GeForce GTX 1050 Ti", "type": "CUDA"},
                    {"name": "GeForce GTX 1050 Ti", "type": "OPTIX"}
                ]
            },
            "timestamp": "2021-02-09T07:50:04.046554+00:00"
        }
    ],
    "id": "8b78e6e0-c83e-4f40-9282-455bb6d29652",
    "schema_version": "v3"
}

json_entry2 = {
    "created_at": "2021-02-11T17:15:18.796276+00:00",
    "data": [
        {
            "benchmark_launcher": {
                "label": "2.0.4",
                "checksum": "90a38d4b1d932bb175837039382af3ea733bb4c819d8e55e4fe7da2a0f752179"
            },
            "benchmark_script": {
                "label": "2.0.1",
                "checksum": "dee17c82d883838f6da21e7c86f368cda2ab8399eac10b660e199628aca09ec0"
            },
            "blender_version": {
                "version": "2.91.2",
                "label": "2.91.2",
                "build_date": "2021-01-19",
                "build_time": "16:25:50",
                "build_commit_date": "2021-01-19",
                "build_commit_time": "16:15",
                "build_hash": "5be9ef417703",
                "checksum": "52582e09379c36bd7a26d99ec72cbbe2d1d200773e63e73f57ebfc1c1a5918c4"
            },
            "device_info": {
                "device_type": "OPTIX",
                "num_cpu_threads": 12,
                "compute_devices": [
                    {
                        "name": "GeForce RTX 3070",
                        "type": "OPTIX",
                        "is_display": False
                    }
                ]
            },
            "scene": {
                "label": "classroom",
                "checksum": "0089a8807b16e07be5fba59beca64def206249df49c74f7c6aaa15d2e1a483ec"
            },
            "stats": {
                "render_time_no_sync": 55.8695,
                "total_render_time": 56.5559,
                "device_peak_memory": 345.3
            },
            "system_info": {
                "system": "Windows",
                "machine": "AMD64",
                "bitness": "64bit",
                "num_cpu_cores": 6,
                "num_cpu_threads": 12,
                "num_cpu_sockets": 1,
                "dist_name": "",
                "dist_version": "",
                "devices": [
                    {"name": "AMD Ryzen 5 5600X 6-Core Processor", "type": "CPU"},
                    {"name": "AMD Ryzen 5 5600X 6-Core Processor", "type": "CPU"},
                    {"name": "GeForce RTX 3070", "type": "CUDA", "is_display": False},
                    {"name": "AMD Ryzen 5 5600X 6-Core Processor", "type": "CPU"},
                    {"name": "GeForce RTX 3070", "type": "OPTIX", "is_display": False},
                    {"name": "AMD Ryzen 5 5600X 6-Core Processor", "type": "CPU"}
                ]
            },
            "timestamp": "2021-02-11T17:14:59.086047+00:00"
        }
    ],
    "id": "dc84efd7-2c74-4a1b-8e23-0a5",
    "schema_version": "v3"
}
