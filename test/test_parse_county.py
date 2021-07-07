import os
import sys
import unittest

sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
from src.one_barony_one_county import parse_county


class TestParseCounty(unittest.TestCase):
    def test_cultural_names_no_copy(self):
        input_lines = [
            'c_middlesex = {\n',
            '\n\tb_london = {\n',
            '\t\tcultural_names = {\n',
            '\t\t\tfrench = cn_londres\n',
            '\t\t}\n',
            '\t}\n',
            '}\n']
        new_lines, i = parse_county(input_lines, 0, set())
        self.assertEqual(i, 6)
        self.assertEqual(new_lines, input_lines)

    def test_cultural_names_duplicates(self):
        input_lines = [
            'c_london = {\n',
            '\tcultural_names = {\n',
            '\t\tfrench = cn_londres\n',
            '\t}\n',
            '\n\tb_london = {\n',
            '\t\tcultural_names = {\n',
            '\t\t\tfrench = cn_londres\n',
            '\t\t}\n',
            '\t}\n',
            '}\n']
        new_lines, i = parse_county(input_lines, 0, set())
        self.assertEqual(i, 9)
        self.assertEqual(new_lines, input_lines)

    def test_cultural_names_copy(self):
        input_lines = [
            'c_london = {\n',
            '\n\tb_london = {\n',
            '\t\tcultural_names = {\n',
            '\t\t\tfrench = cn_londres\n',
            '\t\t}\n',
            '\t}\n',
            '}\n']
        new_lines, i = parse_county(input_lines, 0, set())
        self.assertEqual(i, 6)
        expected_lines = [
            'c_london = {\n',
            '\tcultural_names = {\n',
            '\t\tfrench = cn_londres\n',
            '\t}\n',
            '\n\tb_london = {\n',
            '\t\tcultural_names = {\n',
            '\t\t\tfrench = cn_londres\n',
            '\t\t}\n',
            '\t}\n',
            '}\n']
        self.assertEqual(new_lines, expected_lines)

    def test_invalid_several_egal(self):
        with self.assertRaises(Exception):
            parse_county(['c_machin = {', 'a = b = c', '}'], 0, set())

    def test_valid_several_egal(self):
        parse_county(['c_machin = { # =', '}'], 0, set())

    def test_valid_several_egal2(self):
        parse_county(['c_machin = {', 'a = b # = c', '}'], 0, set())

    def test_commented_attribute(self):
        input_lines = ['c_machin = {\n',
            '#a = b\n',
            '\n\tb_bidule = {\n',
            '\t}\n',
            '}\n'
        ]
        new_lines, i = parse_county(input_lines, 0, set())
        self.assertEqual(i, 4)
        expected_lines = ['c_machin = {\n',
            '\n\tb_bidule = {\n',
            '\t}\n',
            '}\n'
        ]
        self.assertEqual(new_lines, expected_lines)

    def test_ai_primary_priority(self):
        input_lines = [
            'c_cumberland = {\n',
            '\tai_primary_priority = {\n',
			'\t\tif = {\n',
			'\t\t\tlimit = {\n',
			'\t\t\t\tculture = culture:cumbrian\n',
            '\t\t\t}\n',
            '\t\t\tadd = @correct_culture_primary_score\n',
            '\t\t}\n',
            '\t}\n',
            '\n\tb_london = {\n',
            '\t}\n',
            '}\n']
        new_lines, i = parse_county(input_lines, 0, set())
        self.assertEqual(i, 11)
        self.assertEqual(new_lines, input_lines)



if __name__ == '__main__':
    unittest.main()
