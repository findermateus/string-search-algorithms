import pytest

from algorithms import BoyerMooreSearch, KMPSearch, NaiveSearch, RabinKarpSearch
from algorithms.base import SearchResult, SearchStrategy

ALL_ALGORITHMS = [NaiveSearch, KMPSearch, BoyerMooreSearch, RabinKarpSearch]

@pytest.mark.parametrize("AlgClass", ALL_ALGORITHMS)
def test_implements_strategy_interface(AlgClass):
    """Verifica que a classe implementa corretamente a interface SearchStrategy."""
    alg = AlgClass()
    assert isinstance(alg, SearchStrategy)
    assert isinstance(alg.name, str) and alg.name
    assert isinstance(alg.description, str) and alg.description
    assert isinstance(alg.complexity_best, str) and alg.complexity_best
    assert isinstance(alg.complexity_average, str) and alg.complexity_average
    assert isinstance(alg.complexity_worst, str) and alg.complexity_worst


@pytest.mark.parametrize("AlgClass", ALL_ALGORITHMS)
def test_search_returns_search_result(AlgClass):
    """O método search() deve retornar um objeto SearchResult."""
    alg = AlgClass()
    result = alg.search("hello world", "lo")
    assert isinstance(result, SearchResult)

@pytest.mark.parametrize("AlgClass", ALL_ALGORITHMS)
def test_single_occurrence(AlgClass):
    """Padrão com uma única ocorrência no texto."""
    alg = AlgClass()
    result = alg.search("abcdef", "cde")
    assert result.occurrences == [2]


@pytest.mark.parametrize("AlgClass", ALL_ALGORITHMS)
def test_multiple_occurrences(AlgClass):
    """Padrão com múltiplas ocorrências não sobrepostas."""
    alg = AlgClass()
    result = alg.search("ababab", "ab")
    assert result.occurrences == [0, 2, 4]


@pytest.mark.parametrize("AlgClass", ALL_ALGORITHMS)
def test_overlapping_occurrences(AlgClass):
    """Padrão com ocorrências sobrepostas (ex.: 'aa' em 'aaaa')."""
    alg = AlgClass()
    result = alg.search("aaaa", "aa")
    assert result.occurrences == [0, 1, 2]


@pytest.mark.parametrize("AlgClass", ALL_ALGORITHMS)
def test_pattern_at_start(AlgClass):
    """Padrão encontrado apenas no início do texto."""
    alg = AlgClass()
    result = alg.search("patternXYZ", "pattern")
    assert result.occurrences == [0]


@pytest.mark.parametrize("AlgClass", ALL_ALGORITHMS)
def test_pattern_at_end(AlgClass):
    """Padrão encontrado apenas no final do texto."""
    alg = AlgClass()
    result = alg.search("XYZpattern", "pattern")
    assert result.occurrences == [3]


@pytest.mark.parametrize("AlgClass", ALL_ALGORITHMS)
def test_no_occurrence(AlgClass):
    """Padrão que não existe no texto deve retornar lista vazia."""
    alg = AlgClass()
    result = alg.search("hello world", "xyz")
    assert result.occurrences == []


@pytest.mark.parametrize("AlgClass", ALL_ALGORITHMS)
def test_pattern_equals_text(AlgClass):
    """Padrão idêntico ao texto deve ter exatamente uma ocorrência em 0."""
    alg = AlgClass()
    result = alg.search("abc", "abc")
    assert result.occurrences == [0]


@pytest.mark.parametrize("AlgClass", ALL_ALGORITHMS)
def test_pattern_longer_than_text(AlgClass):
    """Padrão maior que o texto não pode ter ocorrências."""
    alg = AlgClass()
    result = alg.search("ab", "abcde")
    assert result.occurrences == []


@pytest.mark.parametrize("AlgClass", ALL_ALGORITHMS)
def test_single_char_pattern(AlgClass):
    """Padrão de um único caractere."""
    alg = AlgClass()
    result = alg.search("aabaa", "a")
    assert result.occurrences == [0, 1, 3, 4]


@pytest.mark.parametrize("AlgClass", ALL_ALGORITHMS)
def test_known_positions(AlgClass):
    """Verifica posição exata com texto e padrão conhecidos."""
    text = "ababcabcabababd"
    pattern = "ababd"
    alg = AlgClass()
    result = alg.search(text, pattern)
    assert result.occurrences == [9]

@pytest.mark.parametrize("AlgClass", ALL_ALGORITHMS)
def test_metrics_text_and_pattern_length(AlgClass):
    """text_length e pattern_length devem refletir os inputs."""
    text, pattern = "hello world", "lo"
    alg = AlgClass()
    result = alg.search(text, pattern)
    assert result.text_length == len(text)
    assert result.pattern_length == len(pattern)


@pytest.mark.parametrize("AlgClass", ALL_ALGORITHMS)
def test_metrics_total_comparisons_positive(AlgClass):
    """Para uma busca com resultado, comparisons deve ser > 0."""
    alg = AlgClass()
    result = alg.search("abcabc", "abc")
    assert result.total_comparisons > 0


@pytest.mark.parametrize("AlgClass", ALL_ALGORITHMS)
def test_metrics_execution_time_non_negative(AlgClass):
    """O tempo de execução deve ser >= 0."""
    alg = AlgClass()
    result = alg.search("hello", "ll")
    assert result.execution_time_ms >= 0


@pytest.mark.parametrize("AlgClass", ALL_ALGORITHMS)
def test_steps_recorded(AlgClass):
    """Pelo menos um passo deve ser registrado durante a busca."""
    alg = AlgClass()
    result = alg.search("abcabc", "bc")
    assert len(result.steps) > 0


@pytest.mark.parametrize("AlgClass", ALL_ALGORITHMS)
def test_algorithm_name_in_result(AlgClass):
    """O campo algorithm do resultado deve coincidir com alg.name."""
    alg = AlgClass()
    result = alg.search("test", "es")
    assert result.algorithm == alg.name


@pytest.mark.parametrize("AlgClass", ALL_ALGORITHMS)
def test_complexity_fields_in_result(AlgClass):
    """Campos de complexidade no resultado devem ser strings não vazias."""
    alg = AlgClass()
    result = alg.search("test", "es")
    assert result.complexity_best
    assert result.complexity_average
    assert result.complexity_worst

def test_all_algorithms_agree_on_occurrences():
    """Todos os algoritmos devem encontrar as mesmas posições para o mesmo input."""
    text = "the quick brown fox jumps over the lazy dog"
    pattern = "the"
    results = [AlgClass().search(text, pattern).occurrences for AlgClass in ALL_ALGORITHMS]
    assert all(r == results[0] for r in results), (
        f"Divergência de resultados: {dict(zip([c.__name__ for c in ALL_ALGORITHMS], results))}"
    )


def test_all_algorithms_agree_no_match():
    """Todos os algoritmos devem retornar lista vazia quando o padrão não existe."""
    text = "abcdefgh"
    pattern = "xyz"
    results = [AlgClass().search(text, pattern).occurrences for AlgClass in ALL_ALGORITHMS]
    assert all(r == [] for r in results)

@pytest.mark.parametrize("AlgClass", ALL_ALGORITHMS)
def test_reuse_after_reset(AlgClass):
    """Instância reutilizada após reset() deve produzir resultado correto."""
    alg = AlgClass()
    alg.search("first search", "first")

    result2 = alg.search("second search", "second")
    assert result2.occurrences == [0]
    assert result2.text_length == len("second search")

