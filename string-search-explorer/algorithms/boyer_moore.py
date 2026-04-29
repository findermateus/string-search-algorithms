import time
from typing import List, Dict
from .base import SearchStrategy, SearchResult


class BoyerMooreSearch(SearchStrategy):

    @property
    def name(self) -> str:
        return "Boyer-Moore (Bad Character)"

    @property
    def description(self) -> str:
        return (
            "Varre o padrão da direita para a esquerda e usa a tabela Bad Character "
            "para saltar posições após um mismatch. Implementação com heurística "
            "Bad Character; o algoritmo completo inclui também Good Suffix."
        )

    @property
    def complexity_best(self) -> str:
        return "O(n / m)"

    @property
    def complexity_average(self) -> str:
        return "O(n / m)"

    @property
    def complexity_worst(self) -> str:
        return "O(n * m)"

    def _build_bad_char_table(self, pattern: str) -> Dict[str, int]:
        table: Dict[str, int] = {}
        for i, ch in enumerate(pattern):
            table[ch] = i
        return table

    def search(self, text: str, pattern: str) -> SearchResult:
        self.reset()
        n = len(text)
        m = len(pattern)
        occurrences: List[int] = []

        start_time = time.perf_counter()

        bad_char = self._build_bad_char_table(pattern)
        bad_char_display = dict(sorted(bad_char.items()))

        self._add_step(
            text_index=0,
            pattern_index=0,
            comparison="Building Bad Character heuristic table",
            result="info",
            aux_data={"bad_char_table": bad_char_display, "pattern": pattern},
            note="Bad character table: maps each character to its last occurrence in pattern",
        )

        shift = 0

        while shift <= n - m:
            j = m - 1

            while j >= 0:
                self.comparisons += 1
                char_text = text[shift + j]
                char_pat = pattern[j]
                matched = char_text == char_pat

                self._add_step(
                    text_index=shift + j,
                    pattern_index=j,
                    comparison=f"text[{shift+j}]='{char_text}' vs pattern[{j}]='{char_pat}'",
                    result="match" if matched else "mismatch",
                    highlight_text=list(range(shift, shift + m)),
                    highlight_pattern=[j],
                    aux_data={"bad_char_table": bad_char_display, "shift": shift, "j": j},
                    note=f"Comparing right-to-left at window shift={shift}, j={j}",
                )

                if not matched:
                    break
                j -= 1

            if j < 0:
                occurrences.append(shift)
                self._add_step(
                    text_index=shift,
                    pattern_index=0,
                    comparison=f"Pattern found at index {shift}",
                    result="found",
                    highlight_text=list(range(shift, shift + m)),
                    highlight_pattern=list(range(m)),
                    aux_data={"bad_char_table": bad_char_display},
                    note=f"Full match at position {shift}",
                )
                next_char_idx = bad_char.get(text[shift + m], -1) if shift + m < n else -1
                skip = m - next_char_idx
                shift += skip
                self._add_step(
                    text_index=shift,
                    pattern_index=0,
                    comparison=f"Shifting pattern by {skip} positions",
                    result="shift",
                    aux_data={"bad_char_table": bad_char_display, "skip": skip},
                    note=f"After match: shift by {skip}",
                )
            else:
                bad_char_val = bad_char.get(text[shift + j], -1)
                skip = max(1, j - bad_char_val)
                shift += skip
                self._add_step(
                    text_index=shift,
                    pattern_index=0,
                    comparison=(
                        f"Bad char '{text[shift - skip + j]}': "
                        f"last occurrence at {bad_char_val}, skip by {skip}"
                    ),
                    result="shift",
                    highlight_text=list(range(shift, min(shift + m, n))),
                    aux_data={
                        "bad_char_table": bad_char_display,
                        "mismatch_char": text[shift - skip + j],
                        "bad_char_val": bad_char_val,
                        "skip": skip,
                    },
                    note=f"Using bad character heuristic: skip {skip} positions",
                )

        elapsed = (time.perf_counter() - start_time) * 1000
        return self._build_result(
            text, pattern, occurrences, elapsed,
            aux_structures={"bad_char_table": bad_char_display},
        )
