from script_tools.jarowinkler_place_combinator.place_combiner import combine_places
import pytest


class TestJaroWinklerPlaceCombiner:

    def test_shortest_name_selection(self):
        results = combine_places('./tests/script_tools/jarowinkler_combiner/testset1.csv')
        assert results[0]['name'] == 'Australia'

    def test_prioritize_name_with_coordinates(self):
        results = combine_places('./tests/script_tools/jarowinkler_combiner/testset1.csv')
        assert results[1]['name'] == 'Alastaro'
