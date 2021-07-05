import re

def one_barony_one_county(input_landed_tile_file_path: str, output_landed_tile_file_path: str):
    with open(input_landed_tile_file_path, 'r') as f:
        input_lines = f.readlines()
    edit_lines = parse_and_edit_lines(input_lines)
    with open(output_landed_tile_file_path, 'w') as f:
        f.writelines(edit_lines)


def parse_and_edit_lines(input_lines: list) -> list:
    counties = set()
    edit_lines = []
    i = 0
    while i < len(input_lines):
        line = input_lines[i]
        county_declaration_or_none = re.search('c_\w*\W*=', line)
        if county_declaration_or_none is None:
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
            tokens = line.strip().split('=')
            if len(tokens) > 2:
                raise Exception(f'Too much = in {line}')
            if tokens[0].startswith('b_'):
                barony_name, barony_attributes, i = parse_barony(input_lines, i)
                barony_with_county_name = barony_with_county_name | (barony_name == county_name)
                baronies.append({'name': barony_name, 'attributes': barony_attributes})
            else:
                county_attributes[tokens[0].replace(' ', '')] = tokens[1]
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
            tokens = line.strip().split('=')
            if len(tokens) > 2:
                raise Exception(f'Too much = in {line}')
            key = tokens[0].replace(' ', '')
            value = tokens[1]
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
            barony_attributes[key] = value
        bracket_level += line.count("{") - line.count("}")
    return barony_name, barony_attributes, i


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
        for key, value in county_attributes.items():
            res.append('\t' * (tab_nb + 1) + key + ' =' + value + '\n')
        res.append('\n' + '\t' * (tab_nb + 1) + "b_" + baronies[i]['name'] + ' = {\n')
        for key, value in baronies[i]['attributes'].items():
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
    one_barony_one_county('../00_landed_tiles.txt', '../00_landed_tiles_modified.txt')
