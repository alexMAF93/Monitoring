#!/usr/bin/env python3


import sys
from os.path import basename


N_lines = int(sys.argv[1])
FILE = sys.argv[2]
name_file = basename(FILE)


def write_to_file(FILE, lines):
    with open(FILE, 'w') as f:
        for line in lines:
            f.write(line)


with open(FILE, 'r') as f:
    file_content = tuple(f.readlines())
    T_lines = len(file_content)
    N_full_docs = T_lines // N_lines
    N_part_docs = T_lines % N_lines
    for ind in range(0, N_full_docs):
        write_to_file('/tmp/' + name_file +'_' + str(ind), file_content[ind*N_lines:(ind+1)*N_lines])
    write_to_file('/tmp/' + name_file +'_' + str(N_full_docs), file_content[len(file_content)-N_part_docs:])
        
