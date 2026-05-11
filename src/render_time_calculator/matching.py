import re
from difflib import SequenceMatcher

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

STRICT_CANDIDATE_VARIANTS = {
    "oem",
    "mobile",
    "maxq",
}


def extract_variant_flags(name: str) -> set[str]:
    raw = name.lower()
    flags = set()

    if re.search(r"\boem\b", raw):
        flags.add("oem")

    if re.search(r"\blaptop\b|\bmobile\b|\bmobility\b", raw):
        flags.add("mobile")

    if re.search(r"\bmax[-\s]?q\b", raw):
        flags.add("maxq")

    return flags


def variants_are_compatible(input_variants: set[str], candidate_variants: set[str]) -> bool:
    """
    Candidate-specific variants should not be guessed.

    Example:
      input:     GeForce RTX 3050
      candidate: GeForce RTX 3050 OEM
      -> reject, because OEM was not present in input

      input:     GeForce RTX 3050 Laptop GPU
      candidate: GeForce RTX 3050
      -> allow, because base card may be the closest available fallback

      input:     GeForce RTX 3050
      candidate: GeForce RTX 3050 Laptop GPU
      -> reject, because Laptop was not present in input
    """
    candidate_strict_variants = candidate_variants & STRICT_CANDIDATE_VARIANTS
    missing_from_input = candidate_strict_variants - input_variants

    return not missing_from_input


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


def build_gpu_index(gpu_data: dict) -> dict:
    return {
        key: {
            "normalized": normalize_gpu_name(key),
            "numbers": extract_model_numbers(key),
            "signatures": extract_model_signatures(key),
            "variants": extract_variant_flags(key),
        }
        for key in gpu_data.keys()
    }


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


def find_gpu_key(input_name: str, gpu_data: dict, gpu_index: dict, threshold: float = 0.88):
    if input_name in gpu_data:
        return input_name, 1.0, True

    normalized_input = normalize_gpu_name(input_name)
    input_numbers = extract_model_numbers(input_name)
    input_signatures = extract_model_signatures(input_name)
    input_variants = extract_variant_flags(input_name)

    best_key = None
    best_score = 0.0

    for key, meta in gpu_index.items():
        # Hard reject if numbers do not match exactly.
        # This also prevents no-number inputs from matching numbered GPUs.
        if input_numbers != meta["numbers"]:
            continue

        # Hard reject bad letter+number model matches.
        # Example: P2000 should not match T2000.
        if input_signatures and input_signatures != meta["signatures"]:
            continue

        # Hard reject candidate-only variants.
        # Example: RTX 3050 should not match RTX 3050 OEM.
        if not variants_are_compatible(input_variants, meta["variants"]):
            continue

        score = similarity(normalized_input, meta["normalized"])

        if score > best_score:
            best_score = score
            best_key = key

    if best_score >= threshold:
        return best_key, best_score, True

    return None, best_score, False
