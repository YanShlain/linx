import pytest

from matching.word_matcher import build_match_pattern, match_word_in_file
from testing.fake_line_reader import FakeLineReader

SENSITIVE_WORD = "goat"


@pytest.fixture
def pattern():
    return build_match_pattern(SENSITIVE_WORD)


def test_tp_2_1_case_insensitive_match(pattern):
    reader = FakeLineReader(["Does a goat eat meat?"])
    assert match_word_in_file(reader, pattern) is True


def test_tp_2_2_uppercase_match(pattern):
    reader = FakeLineReader(["GOAT is an abbreviation"])
    assert match_word_in_file(reader, pattern) is True


def test_tp_2_3_go_at_no_match(pattern):
    reader = FakeLineReader(["Riddle: You go at red"])
    assert match_word_in_file(reader, pattern) is False


def test_tp_2_4_possessive_no_match(pattern):
    reader = FakeLineReader(["The main part of a goat's diet"])
    assert match_word_in_file(reader, pattern) is False


def test_tp_2_5_goatttttt_no_match(pattern):
    reader = FakeLineReader(["GOATttttt wandered"])
    assert match_word_in_file(reader, pattern) is False


def test_tp_2_6_goatt_no_match(pattern):
    reader = FakeLineReader(["Mountain Goatt mammal"])
    assert match_word_in_file(reader, pattern) is False


def test_tp_2_7_multiline_match_stops_early(pattern):
    reader = FakeLineReader(["no match here", "still nothing", "a goat appeared"])
    assert match_word_in_file(reader, pattern) is True
    assert reader.read_count == 3


def test_tp_2_8_empty_reader(pattern):
    reader = FakeLineReader([])
    assert match_word_in_file(reader, pattern) is False
