import json
from datetime import datetime

READ_PATH = "cleaned_gpu.json"
WRITE_PATH = "gpu_metrics.csv"

RELEVANT_METRICS = ("Model name",
                    "Core clock (MHz)",
                    "Memory clock (MHz)",
                    "Memory Size (MiB)",
                    "Memory Bandwidth (GB/s)",
                    "Memory Bus width (bit)",
                    "Fillrate MTexels/s",
                    "Fillrate MPixels/s",
                    # "Fab (nm)",
                    "Transistors (million)"
                    # "Die size (mm)"
)

with open(READ_PATH) as infile:
    gpus_json = json.loads(infile.read())

outfile = open(WRITE_PATH, 'w')
debug_file = open("problematic_GPUs.txt", 'w')

outfile.write(f"{','.join(RELEVANT_METRICS)}\n")

counter = 0
processed_gpus = []

for metrics in gpus_json.values():
    counter += 1

    if 'Launch' not in metrics:
        continue

    entry_date = datetime.strptime(metrics["Launch"].split()[0], "%Y-%m-%d").date()
    if entry_date.year < 2010:
        continue

    format = ""
    try:
        for i in range(len(RELEVANT_METRICS)):
            format += str(metrics[RELEVANT_METRICS[i]])
            if i != len(RELEVANT_METRICS) - 1:
                format += ','

        outfile.write(format + '\n')

    except KeyError as e:
        # print(counter, metrics["Model name"])

        if metrics["Model name"] not in processed_gpus and metrics["Model name"] != "nan":
            debug_file.write(f"{counter} {metrics["Model name"]}\t{e}\n")

        processed_gpus.append(metrics["Model name"])  # 167 w/o duplicates

    # if counter == 1:
    #     break

outfile.close()
debug_file.close()
