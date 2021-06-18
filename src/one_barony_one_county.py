def one_barony_one_county(input_landed_tile_file_path: str, output_landed_tile_file_path: str):
    with open(input_landed_tile_file_path, 'r') as f:
        input_lines = f.readlines()
    with open(output_landed_tile_file_path, 'w') as f:
        for line in input_lines:
            f.write(line)


if __name__ == '__main__':
    one_barony_one_county('../00_landed_tiles.txt', '../00_landed_tiles_modified.txt')
