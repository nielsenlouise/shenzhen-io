import sys
import re
import numpy as np

from machine_codes import *

# Every command looks like:
# LABEL CONDITION INSTRUCTION ARGUMENTS COMMENT
# Regex objects for each potential component of an instruction
LABEL = re.compile(r"(\w*:)")
CONDITION = re.compile(r"(\+|\-)")
INSTRUCTION = re.compile('|'.join(list(functs)))
ARG_REG = re.compile('|'.join(list(registers)))
ARG_INT = re.compile(r" -?\d+")
ARG_LABEL = re.compile(r" \w*$")

REGEX_LIST = [LABEL, CONDITION, INSTRUCTION, ARG_REG, ARG_INT, ARG_LABEL]

def parse_instr(instr):
    return [regex.findall(instr) for regex in REGEX_LIST]

def get_machine_code(regex_instr, labels):
    try:
        cond = conditionals.get(regex_instr[1][0])
    except IndexError:
        cond = "00"
    try:
        funct = functs.get(regex_instr[2][0])
    except IndexError:
        return "0000000000000000000000000000000"
    if funct == "0010":
        addr = np.binary_repr(labels.index([(regex_instr[5][0])[1:] + ":"]), width=11)
        return "".join([cond, opcodes.get("i"), funct, "0"*11, addr])
    regs = "".join([registers[reg] for reg in regex_instr[3]])
    imms = "".join([np.binary_repr(int(imm), width=11) for imm in reversed(regex_instr[4])])

    # Concatenate together appropriately based on number and type of arguments
    args_lens = (len(regex_instr[3]), len(regex_instr[4]))
    return {
        (0,0): "".join([cond, opcodes.get(""), funct, "0"*22]),             # _
        (1,0): "".join([cond, opcodes.get("r"), funct, regs, "0"*19]),      # r
        (2,0): "".join([cond, opcodes.get("rr"), funct, regs, "0"*16]),     # rr
        (0,1): "".join([cond, opcodes.get("i"), funct, "0"*11, imms]),      # i
        (0,2): "".join([cond, opcodes.get("ii"), funct, imms]),             # ii
        (1,1): "".join([cond, opcodes.get("ri"), funct, regs, "0"*8, imms]) # ri
    }.get(args_lens)

def get_instrs(fname):
    with open(fname) as f:
        return f.read().splitlines()

def write_to_file(destfname, instrs):
    with open(destfname, 'w') as f:
        f.write("\n".join(instrs))

def assemble(fname, destfname):
    instrs = get_instrs(fname)
    labels = [LABEL.findall(instr) for instr in instrs]
    instrs = [get_machine_code(parse_instr(instr), labels) for instr in instrs]
    instrs.append("0000100100000000000000000000000")
    write_to_file(destfname, instrs)

if __name__ == "__main__":
    assemble(sys.argv[1], sys.argv[2])
    # assemble('xbus_example_1.asm', 'xbus_example_1.text')
