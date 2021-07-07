import re

BARONY_ATTR_TO_NOT_COPY = ['definite_form', 'province']

def one_barony_one_county(input_landed_tile_file_path: str, output_landed_tile_file_path: str):
    with open(input_landed_tile_file_path, 'r', encoding='utf8') as f:
        input_lines = f.readlines()
    input_lines = format_lines(input_lines)
    edit_lines = parse_and_edit_lines(input_lines)
    with open(output_landed_tile_file_path, 'w', encoding='utf8') as f:
        f.writelines(edit_lines)


def format_lines(lines: list) -> list:
    format_needed = False
    for line in lines:
        if need_format(line):
            format_needed = True
            break
    if not format_needed:
        return lines
    else:
        res = []
        for line in lines:
            if need_format(line):
                print(f'WARNING : Invalid format detected (in line {line[:-1]}, we try to solve it but it can cause some bugs')
                split_line = line.split('{')
                tab_nb = split_line[0].count('\t')
                for l in split_line:
                    res.append('\t' * tab_nb + l + '{\n')
                    tab_nb += 1
                res[-1] = res[-1][:-2]
            else:
                res.append(line)
        return res


def need_format(line: str) -> bool:
    """
    Return true if line as a title declaration followed by content
    """
    return (re.search('\t+e_\w*\W*=', line) is not None and re.search('\t+e_\w*\W*=\W*{[\w\t]*\n', line) is None and re.search('\t+e_\w*\W*=\W*{\W*#', line) is None) or \
        (re.search('\t+k_\w*\W*=', line) is not None and re.search('\t+k_\w*\W*=\W*{[\w\t]*\n', line) is None and re.search('\t+k_\w*\W*=\W*{\W*#', line) is None) or \
        (re.search('\t+d_\w*\W*=', line) is not None and re.search('\t+d_\w*\W*=\W*{[\w\t]*\n', line) is None and re.search('\t+d_\w*\W*=\W*{\W*#', line) is None) or \
        (re.search('\t+c_\w*\W*=', line) is not None and re.search('\t+c_\w*\W*=\W*{[\w\t]*\n', line) is None and re.search('\t+c_\w*\W*=\W*{\W*#', line) is None)


def parse_and_edit_lines(input_lines: list) -> list:
    counties = set()
    edit_lines = []
    i = 0
    while i < len(input_lines):
        line = input_lines[i]
        county_declaration_or_none = re.search('c_\w*\W*=', line)
        if county_declaration_or_none is None or re.search('automatic_claim', line) is not None:
            edit_lines.append(line)
        else:
            county_edit_lines, i = parse_county(input_lines, i, counties)
            for line in county_edit_lines:
                edit_lines.append(line)
        i += 1
    return edit_lines

# https://ck3.paradoxwikis.com/Title_modding#List_of_attributes
def parse_county(input_lines: list, line_index: int, counties: set):
    i = line_index
    line = input_lines[i]
    county_match = re.search('c_\w*', line).regs[0]
    county_name = line[county_match[0]:county_match[1]][2:]
    tab_nb = line.count('\t')
    county_attributes = dict()
    baronies = []
    barony_with_county_name = False
    bracket_level = 0
    line = line[line.find('{')+1:]
    while bracket_level >= 0:
        i += 1
        line = input_lines[i]
        if '=' in line:
            if '#' in line:
                tokens = line.split('#')[0].strip().split('=')
            else:
                tokens = line.strip().split('=')
            if len(tokens) > 2:
                raise Exception(f'Too much = in {line}')
            elif len(tokens) == 1:
                # The equal is in fact in a comment,
                continue
            if tokens[0].startswith('b_'):
                barony_name, barony_attributes, i = parse_barony(input_lines, i)
                barony_with_county_name = barony_with_county_name | (barony_name == county_name)
                baronies.append({'name': barony_name, 'attributes': barony_attributes})
            else:
                value, i, bracket_level = extract_attribute_value(tokens[1], input_lines, i, bracket_level)
                county_attributes[tokens[0].replace(' ', '')] = value
                bracket_level += line.count("{") - line.count("}")
        else:
            bracket_level += line.count("{") - line.count("}")
    new_lines = generate_new_county_lines(county_name, county_attributes, baronies, barony_with_county_name, counties, tab_nb)
    counties.add(county_name)
    return new_lines, i


def parse_barony(input_lines: list, line_index: int):
    i = line_index
    line = input_lines[i]
    barony_match = re.search('b_\w*', line).regs[0]
    barony_name = line[barony_match[0]:barony_match[1]][2:]
    barony_attributes = dict()
    bracket_level = 0
    while bracket_level >= 0:
        i += 1
        line = input_lines[i]
        if '=' in line:
            if '#' in line:
                tokens = line.split('#')[0].strip().split('=')
            else:
                tokens = line.strip().split('=')
            if len(tokens) > 2:
                raise Exception(f'Too much = in {line}')
            elif len(tokens) == 1:
                # The equal is in fact in a comment,
                continue
            value, i, bracket_level = extract_attribute_value(tokens[1], input_lines, i, bracket_level)
            barony_attributes[tokens[0].replace(' ', '')] = value
        bracket_level += line.count("{") - line.count("}")
    return barony_name, barony_attributes, i

def extract_attribute_value(value: str, input_lines:list, i: int, bracket_level: int):
    if value.count("{") > value.count("}"):
        value = [value + '\n']
        i += 1
        attribute_line = input_lines[i]
        while '}' not in attribute_line:
            value.append(attribute_line)
            i += 1
            attribute_line = input_lines[i]
        value.append(attribute_line)
        bracket_level -= 1
    return value, i, bracket_level


def generate_new_county_lines(county_name: str, county_attributes: dict, baronies: list, barony_with_county_name: bool, counties: set, tab_nb: int):
    res = []
    for i in range(len(baronies)):
        if i == 0:
            # Ensure the original county name is kept
            new_county_name = get_non_duplicated_county_name(
                baronies[0]['name'] if barony_with_county_name else county_name, counties)
        else:
            new_county_name = get_non_duplicated_county_name(baronies[i]['name'], counties)
        res.append('\t' * tab_nb + "c_" + new_county_name + ' = {\n')
        if baronies[i]['name'] == new_county_name:
            new_county_attributes = baronies[i]['attributes'].copy()
            for attr in BARONY_ATTR_TO_NOT_COPY:
                if attr in new_county_attributes:
                    del new_county_attributes[attr]
            remove_tab_nb = -1
        else:
            new_county_attributes = county_attributes 
            remove_tab_nb = 0
        for key, value in new_county_attributes.items():
            if type(value) == list:
                res.append('\t' * (tab_nb + 1) + key + ' =' + value[0])
                for val in value[1:]:
                    res.append(val[-remove_tab_nb:])
            else:
                res.append('\t' * (tab_nb + 1) + key + ' =' + value + '\n')
        res.append('\n' + '\t' * (tab_nb + 1) + "b_" + baronies[i]['name'] + ' = {\n')
        for key, value in baronies[i]['attributes'].items():
            if type(value) == list:
                res.append('\t' * (tab_nb + 2) + key + ' =' + value[0])
                for val in value[1:]:
                    res.append(val)
            else:
                res.append('\t' * (tab_nb + 2) + key + ' =' + value + '\n')
        res.append('\t' * (tab_nb + 1) + '}\n')
        res.append('\t' * tab_nb + '}\n')
    return res

def get_non_duplicated_county_name(county_name: str, counties: set):
    if county_name not in counties:
        return county_name
    suffix = 2
    new_county_name = county_name + str(suffix)
    while new_county_name in counties:
        suffix += 1
        new_county_name = county_name + str(suffix)
    return new_county_name


if __name__ == '__main__':
    one_barony_one_county('00_landed_titles.txt', '00_landed_titles_modified.txt')
