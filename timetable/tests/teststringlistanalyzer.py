import pytest
from timetable.management.commands.version_core.stringlistanalyzer import StringListAnalyzer

# --- Тесты для get_similar_string ---
class TestGetSimilarString:

    def test_single_character_strings(self):
        analyzer = StringListAnalyzer(["a"], ["b", "a"])
        assert analyzer.get_similar_string("a") == "a"

    def test_exact_match(self):
        analyzer = StringListAnalyzer(["hello"], ["hello", "world"])
        assert analyzer.get_similar_string("hello") == "hello"

    def test_partial_match1(self):
        analyzer = StringListAnalyzer(["hello"], ["hell", "world"])
        assert analyzer.get_similar_string("hello") == "hell"

    def test_partial_match2(self):
        analyzer = StringListAnalyzer(["hello"], ["hellier", "world"])
        assert analyzer.get_similar_string("hello") == "hellier"

    def test_partial_match3(self):
        analyzer = StringListAnalyzer(["hello"], ["he", "world"])
        assert analyzer.get_similar_string("hello") == "he"

    def test_whitespace_string(self):
        analyzer = StringListAnalyzer([" "], ["world", " "])
        assert analyzer.get_similar_string(" ") == " "

    def test_long_strings(self):
        long_string = "a" + "ab" * 50
        analyzer = StringListAnalyzer([long_string], [long_string, "ab" * 50 + "a"])
        assert analyzer.get_similar_string(long_string) == long_string

    def test_multiple_analyze_strings_one_compare_string(self):
        analyzer = StringListAnalyzer(["hello", "world", "python"], ["test"])
        assert analyzer.get_similar_string("hello") == "test"
        assert analyzer.get_similar_string("world") == "test"
        assert analyzer.get_similar_string("python") == "test"

    def test_one_analyze_string_multiple_compare_strings(self):
        analyzer = StringListAnalyzer(["hello"], ["hell", "hero", "help"])
        assert analyzer.get_similar_string("hello") == "hell"

    def test_multiple_strings_in_both_lists(self):
        analyzer = StringListAnalyzer(["hello", "world"], ["hell", "word"])
        assert analyzer.get_similar_string("hello") == "hell"
        assert analyzer.get_similar_string("world") == "word"

    def test_one_string_in_both_lists(self):
        analyzer = StringListAnalyzer(["hello"], ["world"])
        assert analyzer.get_similar_string("hello") == "world"

    def test_empty_lists(self):
        analyzer = StringListAnalyzer([], [])
        assert analyzer.get_similar_string("hello") == ""

    def test_big_dataset(self):
        small_analyze_strings = ["string1", "string2", "string3", "string4", "string5", "string6", "string7"]
        small_compare_strings = ["compare1", "compare2", "compare3", "compare4", "compare5", "compare6", "compare7"]
        analyzer = StringListAnalyzer(small_analyze_strings, small_compare_strings)
        assert analyzer.get_similar_string("string1") == "compare1"
        assert analyzer.get_similar_string("string2") == "compare2"
        assert analyzer.get_similar_string("string3") == "compare3"
        assert analyzer.get_similar_string("string4") == "compare4"
        assert analyzer.get_similar_string("string5") == "compare5"
        assert analyzer.get_similar_string("string6") == "compare6"
        assert analyzer.get_similar_string("string7") == "compare7"

# --- Тесты для get_ratio_for_string ---
class TestGetRatioForString:

    def test_single_character_strings_ratio(self):
        analyzer = StringListAnalyzer(["a"], ["b", "a"])
        assert analyzer.get_ratio_for_string("a") == 1.0

    def test_exact_match_ratio(self):
        analyzer = StringListAnalyzer(["hello"], ["hello", "world"])
        assert analyzer.get_ratio_for_string("hello") == 1.0

    def test_partial_match_ratio(self):
        analyzer = StringListAnalyzer(["hello"], ["hell", "world"])
        ratio = analyzer.get_ratio_for_string("hello")
        assert 0 < ratio < 1

    def test_no_match_ratio(self):
        analyzer = StringListAnalyzer(["hello"], ["world", "python"])
        assert analyzer.get_ratio_for_string("hello") == pytest.approx(0.4, 0.000001)

    def test_empty_string_ratio(self):
        analyzer = StringListAnalyzer([""], ["world", "python"])
        assert analyzer.get_ratio_for_string("") == 0

    def test_long_strings_ratio(self):
        long_string = "abc" * 50
        analyzer = StringListAnalyzer([long_string], [long_string, "bac" * 50])
        assert analyzer.get_ratio_for_string(long_string) == 1.0

    def test_multiple_analyze_strings_one_compare_string_ratio(self):
        analyzer = StringListAnalyzer(["hello", "world", "python"], ["test"])
        assert analyzer.get_ratio_for_string("hello") == pytest.approx(0.222222, 0.000005)
        assert analyzer.get_ratio_for_string("world") == 0
        assert analyzer.get_ratio_for_string("python") == pytest.approx(0.2, 0.000001)

    def test_empty_lists_ratio(self):
        analyzer = StringListAnalyzer([], [])
        assert analyzer.get_ratio_for_string("hello") == 0

# --- Тесты для get_max_ratio_words ---
class TestGetMaxRatioWords:

    def test_single_exact_match(self):
        analyzer = StringListAnalyzer(["hello"], ["hello"])
        assert analyzer.get_max_ratio_words() == ["hello"]

    def test_single_max_ratio_word(self):
        analyzer = StringListAnalyzer(["hello", "world"], ["hello", "word"])
        assert analyzer.get_max_ratio_words() == ["hello"]

    def test_multiple_max_ratio_words(self):
        analyzer = StringListAnalyzer(["hello", "world"], ["hell", "word"])
        assert set(analyzer.get_max_ratio_words()) == {"hello", "world"}

    def test_empty_lists_max_ratio_words(self):
        analyzer = StringListAnalyzer([], [])
        assert analyzer.get_max_ratio_words() == []

    def test_single_character_strings_max_ratio_words(self):
        analyzer = StringListAnalyzer(["a", "b"], ["a", "c"])
        assert analyzer.get_max_ratio_words() == ["a"]

    def test_long_strings_max_ratio_words(self):
        long_string1 = "a" * 50
        long_string2 = "b" * 50
        analyzer = StringListAnalyzer([long_string1, long_string2], [long_string1])
        assert analyzer.get_max_ratio_words() == [long_string1]

    def test_empty_strings_in_lists_max_ratio_words(self):
        analyzer = StringListAnalyzer(["", ""], ["world", "python"])
        assert analyzer.get_max_ratio_words() == [""]

    def test_no_analysis_performed_max_ratio_words(self):
        analyzer = StringListAnalyzer()
        assert analyzer.get_max_ratio_words() == []

# --- Тесты для get_strings_by_ratio ---
class TestGetStringsByRatio:

    def test_exact_match_ratio_strings(self):
        analyzer = StringListAnalyzer(["hello", "world"], ["hello", "word"])
        assert analyzer.get_strings_by_ratio(1.0) == ["hello"]

    def test_no_match_ratio_strings(self):
        analyzer = StringListAnalyzer(["hello"], ["world"])
        assert analyzer.get_strings_by_ratio(0.5) == []

    def test_partial_match_ratio_strings(self):
        analyzer = StringListAnalyzer(["hello", "python"], ["hell", "pytho"])
        assert analyzer.get_strings_by_ratio(0.9, 1) == ["hello", "python"]

    def test_zero_ratio_strings(self):
        analyzer = StringListAnalyzer(["hello"], ["world"])
        assert analyzer.get_strings_by_ratio(0.4) == ["hello"]

    def test_one_ratio_strings(self):
        analyzer = StringListAnalyzer(["hello"], ["hello"])
        assert analyzer.get_strings_by_ratio(1.0) == ["hello"]

    def test_rounding_ratio_strings(self):
        analyzer = StringListAnalyzer(["hello"], ["helloooo"])
        ratio = round(0.727272, 2)
        assert analyzer.get_strings_by_ratio(ratio, round_number=2) == ["hello"]

    def test_negative_round_number_strings(self):
        analyzer = StringListAnalyzer(["hello"], ["hell"])
        with pytest.raises(Exception, match="Round number must be greater than zero"):
            analyzer.get_strings_by_ratio(0.8, round_number=-1)

    def test_ratio_out_of_bounds_negative_strings(self):
        analyzer = StringListAnalyzer(["hello"], ["world"])
        assert analyzer.get_strings_by_ratio(-0.1) == []

    def test_ratio_out_of_bounds_greater_than_one_strings(self):
        analyzer = StringListAnalyzer(["hello"], ["world"])
        assert analyzer.get_strings_by_ratio(1.1) == []

    def test_empty_lists_strings_by_ratio(self):
        analyzer = StringListAnalyzer([], [])
        assert analyzer.get_strings_by_ratio(0.5) == []

# --- Тесты для get_strings_by_ratio_in_range ---
class TestGetStringsByRatioInRange:

    def test_range_covering_all_ratios_strings(self):
        analyzer = StringListAnalyzer(["hello", "world"], ["hello", "word"])
        assert analyzer.get_strings_by_ratio_in_range(0, 1) == ["hello", "world"]

    def test_range_with_one_matching_ratio_strings(self):
        analyzer = StringListAnalyzer(["hello", "python"], ["hell", "pytho"])
        assert analyzer.get_strings_by_ratio_in_range(0.8, 0.9) == ["hello"]

    def test_range_with_no_matching_ratios_strings(self):
        analyzer = StringListAnalyzer(["hello"], ["world"])
        assert analyzer.get_strings_by_ratio_in_range(0.5, 0.6) == []

    def test_min_and_max_ratio_equal_strings(self):
        analyzer = StringListAnalyzer(["hello"], ["hell"])
        assert analyzer.get_strings_by_ratio_in_range(0.9, 0.9) == []

    def test_range_from_zero_to_one_strings(self):
        analyzer = StringListAnalyzer(["hello", "world"], ["hello", "word"])
        assert analyzer.get_strings_by_ratio_in_range(0, 1) == ["hello", "world"]

    def test_rounded_ratios_strings_in_range(self):
        analyzer = StringListAnalyzer(["hello"], ["helloooo"])
        assert analyzer.get_strings_by_ratio_in_range(0.76, 0.77) == ["hello"]

    def test_min_ratio_greater_than_max_ratio_strings(self):
        analyzer = StringListAnalyzer(["hello"], ["world"])
        assert analyzer.get_strings_by_ratio_in_range(0.8, 0.5) == []

    def test_empty_lists_strings_by_ratio_in_range(self):
        analyzer = StringListAnalyzer([], [])
        assert analyzer.get_strings_by_ratio_in_range(0, 1) == []

    def test_ratios_out_of_bounds_strings_in_range(self):
        analyzer = StringListAnalyzer(["hello"], ["world"])
        assert analyzer.get_strings_by_ratio_in_range(-0.1, 1.1) == ["hello"]

# --- Тесты для get_max_ratio ---
class TestGetMaxRatio:

    def test_max_ratio_exact_match(self):
        analyzer = StringListAnalyzer(["hello"], ["hello", "world"])
        assert analyzer.get_max_ratio() == 1.0

    def test_max_ratio_partial_match(self):
        analyzer = StringListAnalyzer(["hello"], ["hell", "world"])
        ratio = analyzer.get_max_ratio()
        assert 0 < ratio < 1

    def test_max_ratio_multiple_strings(self):
        analyzer = StringListAnalyzer(["hello", "world"], ["hell", "word"])
        assert analyzer.get_max_ratio() > 0.88

    def test_max_ratio_empty_lists(self):
        analyzer = StringListAnalyzer([], [])
        assert analyzer.get_max_ratio() == 0

    def test_max_ratio_single_character_strings(self):
        analyzer = StringListAnalyzer(["a"], ["b", "a"])
        assert analyzer.get_max_ratio() == 1.0

    def test_max_ratio_long_strings(self):
        long_string = "a" * 50
        analyzer = StringListAnalyzer([long_string], [long_string, "b" * 50])
        assert analyzer.get_max_ratio() == 1.0

    def test_max_ratio_no_analysis_performed(self):
        analyzer = StringListAnalyzer()
        assert analyzer.get_max_ratio() == 0

