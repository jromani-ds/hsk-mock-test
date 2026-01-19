import pytest

from hsk.data_engine import DataEngine


@pytest.fixture
def data_engine():
    # Use the actual data directory for now since we created sample files there
    return DataEngine()


def test_load_level_1(data_engine):
    """Test loading Level 1 data."""
    data_engine.load_level_data(1)

    words = data_engine.get_words_for_level(1)
    assert len(words) >= 3
    assert words[0].hanzi == "爱"
    assert words[0].level == 1

    grammar = data_engine.get_grammar_for_level(1)
    assert len(grammar) >= 2
    assert grammar[1].name == "动词 - 能愿动词"


def test_load_radicals(data_engine):
    """Test loading radical hints."""
    data_engine.load_radicals()

    hint = data_engine.get_radical_hint("爱")
    assert hint == "爫"

    hint_missing = data_engine.get_radical_hint("XYZ")
    assert hint_missing is None


def test_missing_file():
    """Test that loading a non-existent level raises FileNotFoundError."""
    engine = DataEngine()
    with pytest.raises(FileNotFoundError):
        engine.load_level_data(999)
