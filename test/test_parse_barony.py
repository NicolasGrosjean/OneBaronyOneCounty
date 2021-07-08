import os
import sys
import unittest

sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
from src.one_barony_one_county import parse_barony


class TestParseBarony(unittest.TestCase):
    def test_cultural_names(self):
        input_lines = [
            '\tb_london = {\n',
            '\t\tcultural_names = {\n',
            '\t\t\tfrench = cn_londres\n',
            '\t\t}\n',
            '\t}\n']
        barony_name, barony_attributes, i = parse_barony(input_lines, 0)
        self.assertEqual(barony_name, 'london')
        self.assertEqual(i, 4)
        self.assertTrue('cultural_names' in barony_attributes)
        self.assertEqual(barony_attributes['cultural_names'], [' {\n', '\t\t\tfrench = cn_londres\n', '\t\t}\n'])

    
    def test_invalid_several_egal(self):
        with self.assertRaises(Exception):
            parse_barony(['b_machin = {', 'a = b = c', '}'], 0)

    def test_valid_several_egal(self):
        parse_barony(['b_machin = { # =', '}'], 0)

    def test_valid_several_egal2(self):
        parse_barony(['b_machin = {', 'a = b # = c', '}'], 0)

    def test_commented_attribute(self):
        input_lines = ['\tb_machin = {\n',
            '\t#a = b\n',
            '\t}\n'
        ]
        barony_name, barony_attributes, i = parse_barony(input_lines, 0)
        self.assertEqual(barony_name, 'machin')
        self.assertEqual(i, 2)
        self.assertEqual(barony_attributes, {})

    def test_commented_attribute2(self):
        input_lines = ['\tb_machin = {\n',
            '\t#}\n',
            '\ta = c\n',
            '\t}\n'
        ]
        barony_name, barony_attributes, i = parse_barony(input_lines, 0)
        self.assertEqual(barony_name, 'machin')
        self.assertEqual(i, 3)
        self.assertEqual(barony_attributes, {'a': ' c'})

    def test_complex_barony_name(self):
        barony_name, barony_attributes, i = parse_barony(['b_qaryat-al-asad = {\n', '}\n'], 0)
        self.assertEqual(barony_name, 'qaryat-al-asad')
        self.assertEqual(i, 1)
        self.assertEqual(barony_attributes, {})

    def test_complex_barony_name2(self):
        barony_name, barony_attributes, i = parse_barony(['b_mansa\'l-kharaz = {\n', '}\n'], 0)
        self.assertEqual(barony_name, 'mansa\'l-kharaz')
        self.assertEqual(i, 1)
        self.assertEqual(barony_attributes, {})


if __name__ == '__main__':
    unittest.main()
