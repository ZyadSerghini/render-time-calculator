import json
import re
from difflib import SequenceMatcher


def normalize_gpu_name(name: str) -> str:
    name = name.lower()

    # Remove common noisy descriptors from detected GPU names
    noise_phrases = [
        "series",
        "graphics",
        "laptop gpu",
        "amd",
        "nvidia",
        "with",
        "design",
        "series",
    ]

    for phrase in noise_phrases:
        name = name.replace(phrase, "")

    # # Remove VRAM markers like 3GB, 6GB, 24GB
    # name = re.sub(r"\b\d+\s*gb\b", "", name)

    # Normalize spacing and punctuation
    name = re.sub(r"[^a-z0-9]+", " ", name)
    name = re.sub(r"\s+", " ", name).strip()

    # Remove CPU descriptors like "8 core processor", "16-core processor"
    name = re.sub(r"\b\d+\s*-?\s*cores?\s+processor\b", "", name)

    return name


def tokenize_gpu_name(name: str) -> list[str]:
    """
    Turns things like:
      P2000 -> p 2000
      RX550 -> rx 550
      940M  -> 940 m
    """
    normalized = normalize_gpu_name(name)

    normalized = re.sub(r"([a-z])(\d)", r"\1 \2", normalized)
    normalized = re.sub(r"(\d)([a-z])", r"\1 \2", normalized)

    return normalized.split()


def extract_model_numbers(name: str) -> set[str]:
    normalized = normalize_gpu_name(name)

    # Use a set so RX550/550 becomes just {"550"}
    return set(re.findall(r"\d+", normalized))


def numbers_are_compatible(input_name: str, candidate_key: str) -> bool:
    input_numbers = extract_model_numbers(input_name)
    candidate_numbers = extract_model_numbers(candidate_key)

    # If the input has no numbers, don't use this filter
    if not input_numbers:
        return True

    return input_numbers == candidate_numbers


GENERIC_MODEL_WORDS = {
    "geforce",
    "radeon",
    "quadro",
    "tesla",
    "graphics",
    "series",
    "gpu",
    "laptop",
}

MODEL_SUFFIX_WORDS = {
    "ti",
    "super",
    "xt",
    "xtx",
    "m",
    "x",
    "pro",
}


def extract_model_signatures(name: str) -> set[str]:
    """
    Examples:
      Quadro P2000 with Max-Q Design -> {"p2000"}
      Quadro T2000 Max-Q             -> {"t2000"}
      GeForce GTX 1660 Ti            -> {"gtx1660ti"}
      Radeon RX 5700 XT              -> {"rx5700xt"}
      Radeon RX550/550 Series        -> {"rx550"}
      Radeon RX Vega 10 Graphics     -> {"vega10"}
      GeForce 940M                   -> {"940m"}
    """
    tokens = tokenize_gpu_name(name)
    signatures = set()
    skip_indexes = set()

    for i, token in enumerate(tokens):
        if i in skip_indexes:
            continue

        if not token.isdigit():
            continue

        # Find nearest meaningful letter/token before the number
        prefix = ""
        j = i - 1

        while j >= 0:
            previous = tokens[j]

            if previous.isdigit():
                j -= 1
                continue

            if previous not in GENERIC_MODEL_WORDS:
                prefix = previous
                break

            j -= 1

        # Optional suffix after the number: Ti, SUPER, XT, M, etc.
        suffix = ""

        if i + 1 < len(tokens) and tokens[i + 1] in MODEL_SUFFIX_WORDS:
            suffix = tokens[i + 1]

            # Handle X2-style names like "Radeon HD 3850 X2"
            if suffix == "x" and i + 2 < len(tokens) and tokens[i + 2].isdigit():
                suffix += tokens[i + 2]
                skip_indexes.add(i + 2)

        signatures.add(f"{prefix}{token}{suffix}")

    return signatures


def model_signatures_are_compatible(input_name: str, candidate_key: str) -> bool:
    input_signatures = extract_model_signatures(input_name)
    candidate_signatures = extract_model_signatures(candidate_key)

    # If the input has no model signature, don't use this filter
    if not input_signatures:
        return True

    return input_signatures == candidate_signatures


def similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


def find_gpu_key(input_name: str, gpu_data: dict, threshold: float = 0.88):
    if input_name in gpu_data:
        return input_name, 1.0

    normalized_input = normalize_gpu_name(input_name)

    best_key = None
    best_score = 0.0

    for key in gpu_data.keys():
        # Hard reject bad number matches
        if not numbers_are_compatible(input_name, key):
            continue

        # Hard reject bad letter+number model matches
        # Example: P2000 should not match T2000
        if not model_signatures_are_compatible(input_name, key):
            continue

        score = similarity(normalized_input, normalize_gpu_name(key))

        if score > best_score:
            best_score = score
            best_key = key

    if best_score >= threshold:
        return best_key, best_score

    return None, best_score


# Usage

if __name__ == '__main__':

    from cleaner import GPU_READ_PATH

    with open(GPU_READ_PATH, encoding="utf-8") as f:
        gpu_data = json.load(f)

    print(find_gpu_key("Quadro T1000 with Max-Q Design", gpu_data))

    quit()

    examples = [
        "Radeon RX 570 Series",
        "GeForce GTX 1660 Ti with Max-Q Design",
        "GeForce RTX 3070 Laptop GPU",
        "GeForce GTX 1060 6GB",
    ]

    for name in examples:
        key, score = find_gpu_key(name, gpu_data)
        print(name, "=>", key, score)
