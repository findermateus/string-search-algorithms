import dataclasses
from typing import Any, Dict, List, Optional

from algorithms import BoyerMooreSearch, KMPSearch, NaiveSearch, RabinKarpSearch
from algorithms.base import SearchStrategy

MAX_STEPS: int = 2_000
MAX_TEXT_LENGTH: int = 500_000
MAX_FILE_SIZE_BYTES: int = 16 * 1024 * 1024

ALGORITHMS: Dict[str, type[SearchStrategy]] = {
    "naive": NaiveSearch,
    "rabin_karp": RabinKarpSearch,
    "kmp": KMPSearch,
    "boyer_moore": BoyerMooreSearch,
}


def get_algorithm_metadata() -> List[Dict[str, str]]:
    metadata = []
    for alg_id, AlgClass in ALGORITHMS.items():
        instance = AlgClass()
        metadata.append(
            {
                "id": alg_id,
                "name": instance.name,
                "description": instance.description,
                "complexity_best": instance.complexity_best,
                "complexity_average": instance.complexity_average,
                "complexity_worst": instance.complexity_worst,
            }
        )
    return metadata


def run_search(text: str, pattern: str, algorithm_id: str) -> Optional[Dict[str, Any]]:
    AlgClass = ALGORITHMS.get(algorithm_id)
    if not AlgClass:
        return None

    alg = AlgClass()
    result = alg.search(text, pattern)
    result_dict = dataclasses.asdict(result)

    if len(result_dict["steps"]) > MAX_STEPS:
        result_dict["steps"] = result_dict["steps"][:MAX_STEPS]
        result_dict["steps_truncated"] = True

    return result_dict


def run_all(text: str, pattern: str) -> Dict[str, Optional[Dict[str, Any]]]:
    return {alg_id: run_search(text, pattern, alg_id) for alg_id in ALGORITHMS}
