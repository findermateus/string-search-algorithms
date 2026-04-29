import time
from typing import List
from .base import SearchStrategy, SearchResult

_BASE: int = 256
_MOD: int = 101


class RabinKarpSearch(SearchStrategy):

    @property
    def name(self) -> str:
        return "Rabin-Karp"

    @property
    def description(self) -> str:
        return (
            "Usa hash de janela deslizante (rolling hash) para identificar candidatos "
            "rapidamente. Apenas quando os hashes coincidem verifica caractere a caractere, "
            f"usando BASE={_BASE} e MOD={_MOD}."
        )

    @property
    def complexity_best(self) -> str:
        return "O(n + m)"

    @property
    def complexity_average(self) -> str:
        return "O(n + m)"

    @property
    def complexity_worst(self) -> str:
        return "O(n * m)"

    def search(self, text: str, pattern: str) -> SearchResult:
        self.reset()
        n = len(text)
        m = len(pattern)
        occurrences: List[int] = []

        if m > n:
            return self._build_result(text, pattern, occurrences, 0.0)

        start_time = time.perf_counter()

        h = 1
        for _ in range(m - 1):
            h = (h * _BASE) % _MOD

        pattern_hash = 0
        window_hash = 0
        for i in range(m):
            pattern_hash = (_BASE * pattern_hash + ord(pattern[i])) % _MOD
            window_hash = (_BASE * window_hash + ord(text[i])) % _MOD

        self._add_step(
            text_index=0,
            pattern_index=0,
            comparison=f"Initial hash: pattern_hash={pattern_hash}, window_hash={window_hash}",
            result="info",
            highlight_text=list(range(m)),
            highlight_pattern=list(range(m)),
            aux_data={"pattern_hash": pattern_hash, "window_hash": window_hash, "h": h,
                      "base": _BASE, "mod": _MOD},
            note="Computing initial rolling hashes",
        )

        for i in range(n - m + 1):
            hash_match = pattern_hash == window_hash

            self._add_step(
                text_index=i,
                pattern_index=0,
                comparison=f"window_hash={window_hash} vs pattern_hash={pattern_hash}",
                result="hash_match" if hash_match else "hash_mismatch",
                highlight_text=list(range(i, i + m)),
                highlight_pattern=list(range(m)),
                aux_data={"pattern_hash": pattern_hash, "window_hash": window_hash,
                          "window": text[i: i + m]},
                note=f"Comparing hashes at window i={i}",
            )

            if hash_match:
                match = True
                for j in range(m):
                    self.comparisons += 1
                    char_text = text[i + j]
                    char_pat = pattern[j]
                    char_match = char_text == char_pat

                    self._add_step(
                        text_index=i + j,
                        pattern_index=j,
                        comparison=f"Verify: text[{i+j}]='{char_text}' vs pattern[{j}]='{char_pat}'",
                        result="match" if char_match else "mismatch",
                        highlight_text=list(range(i, i + j + 1)),
                        highlight_pattern=list(range(j + 1)),
                        note="Hash matched — verifying character by character",
                    )

                    if not char_match:
                        match = False
                        break

                if match:
                    occurrences.append(i)
                    self._add_step(
                        text_index=i,
                        pattern_index=0,
                        comparison=f"Pattern found at index {i}",
                        result="found",
                        highlight_text=list(range(i, i + m)),
                        highlight_pattern=list(range(m)),
                        note=f"Complete match confirmed at position {i}",
                    )

            if i < n - m:
                window_hash = (_BASE * (window_hash - ord(text[i]) * h) + ord(text[i + m])) % _MOD
                if window_hash < 0:
                    window_hash += _MOD

                self._add_step(
                    text_index=i + 1,
                    pattern_index=0,
                    comparison=f"Rolling hash: remove '{text[i]}', add '{text[i+m]}'",
                    result="roll",
                    highlight_text=list(range(i + 1, i + m + 1)),
                    aux_data={"new_window_hash": window_hash, "window": text[i + 1: i + m + 1]},
                    note=f"Rolling window forward: new hash={window_hash}",
                )

        elapsed = (time.perf_counter() - start_time) * 1000
        return self._build_result(
            text, pattern, occurrences, elapsed,
            aux_structures={"base": _BASE, "mod": _MOD},
        )
