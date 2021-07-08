import re

def compare_landed_titles(landed_tile_file_path1: str, landed_tile_file_path2: str):
    with open(landed_tile_file_path1, 'r', encoding='utf8') as f:
        lines1 = f.readlines()
    baronies1 = get_barony_set(lines1)
    print('===========================')
    with open(landed_tile_file_path2, 'r', encoding='utf8') as f:
        lines2 = f.readlines()
    baronies2 = get_barony_set(lines2)
    print('===========================')
    for barony in baronies1:
        if barony not in baronies2:
            print(f'b_{barony} not in generated file')
    print('===========================')
    for barony in baronies2:
        if barony not in baronies1:
            print(f'b_{barony} not in original file')


def get_barony_set(lines: list) -> set():
    baronies = set()
    i = 0
    for line in lines:
        if '#' in line:
            line = line.split('#')[0]
        barony_declaration_matching = re.search('b_\w*\W*=', line)
        if barony_declaration_matching is not None:
            barony_name = line[barony_declaration_matching.regs[0][0]:barony_declaration_matching.regs[0][1]][2:]
            barony_name = barony_name.replace('=', '').replace(' ', '')
            if barony_name in baronies:
                print(f'Duplicated barony declaration b_{barony_name}')
            baronies.add(barony_name)
        i += 1
    return baronies


if __name__ == '__main__':
    compare_landed_titles('00_landed_titles.txt', '00_landed_titles_modified.txt')