import json

INPUT_FILE, OUTPUT_FILE = 'data/raw/gpu-raw-data.json', 'data/processed/gpu-data.json'

OUTPUT_NAMES_PATH = 'data/debug/GPU_names.txt'

METRICS = ('baseClock',
           'boostClock',
           'textureRate',
           'pixelRate',
           'architecture',
           'memoryType',
           'generation',
           'busInterface'
)

PARTIAL_METRICS = (
            'rtCores',
           'tensorCores'
)

DEBUG = False


def clean_GPUs(input_file=INPUT_FILE, output_file=OUTPUT_FILE):
    '''
    Skipping:
        - Any GPU released before 2008
        - The 56 remaining GPUs that do not have "busInterface" as an attribute because they are gaming consoles/handhelds GPUs.
        - The 27 remaining GPUs that do not have "pixelRate" as an attribute because they are not not desktop/laptop GPUs.
    '''

    with open(input_file) as infile:
        content = eval(infile.read())

    new_content = dict()

    counter = 0

    for entry in content:
        entry_name = entry['name']
        entry_releaseDate = entry['releaseDate'][:4]

        if int(entry_releaseDate) < 2008:
            continue

        if any(metric not in entry for metric in ('busInterface', 'pixelRate')):
            continue

        attributes = {'releaseYear': entry_releaseDate}

        try:
            for met in METRICS:
                attributes[met] = entry[met]

            for met in PARTIAL_METRICS:
                if met not in entry.keys():
                    attributes[met] = 0
                else:
                    attributes[met] = entry[met]

        except KeyError as e:
            if DEBUG:
                print(e, entry_name)
            counter += 1

        new_content[entry['name']] = attributes

    if DEBUG and counter != 0:
        print(counter)

    with open(output_file, 'w') as file:
        json.dump(new_content, file, indent=4)


def get_GPU_names(input_file=INPUT_FILE, output_file=OUTPUT_NAMES_PATH):
    '''
    List all GPU names in output_file, purely for debugging purposes.
    '''

    with open(input_file) as infile:
        content = eval(infile.read())

    with open(output_file, 'w') as outfile:
        for key in content:
            outfile.write(f'{key['name']}\n')
