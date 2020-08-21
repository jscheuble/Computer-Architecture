"""CPU functionality."""

import sys

# instruction variables
LDI = 0b10000010
PRN = 0b01000111
HLT = 0b00000001
MUL = 0b10100010
ADD = 0b10100000
PUSH = 0b01000101
POP = 0b01000110
CALL = 0b01010000
RET = 0b00010001

# sprint instruction variables
CMP = 0b10100111
JMP = 0b01010100

# flags
EFLAG = 0b001
LFLAG = 0b011
GFLAG = 0b010


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.pc = 0
        self.running = True

        self.branchtable = {}
        self.branchtable[LDI] = self.handleLDI
        self.branchtable[PRN] = self.handlePRN
        self.branchtable[HLT] = self.handleHLT
        self.branchtable[MUL] = self.handleMUL
        self.branchtable[ADD] = self.handleADD
        self.branchtable[PUSH] = self.handlePUSH
        self.branchtable[POP] = self.handlePOP
        self.branchtable[CALL] = self.handleCALL
        self.branchtable[RET] = self.handleRET
        self.branchtable[CMP] = self.handleCMP
        self.branchtable[JMP] = self.handleJMP

        self.stack_pointer = 0xf4
        self.reg[7] = self.stack_pointer

    def load(self):
        """Load a program into memory."""

        address = 0
        filename = sys.argv[1]

        if filename:
            with open(filename) as f:
                for line in f:
                    line = line.split('#')
                    if line[0] == '' or line[0] == '\n':
                        continue

                    self.ram[address] = int(line[0], 2)
                    address += 1

        else:
            print('missing command line argument')
            sys.exit(0)

    def ram_read(self, MAR):
        return self.ram[MAR]

    def ram_write(self, MAR, MDR):
        self.ram[MAR] = MDR

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] = self.reg[reg_a] * self.reg[reg_b]
        elif op == "CMP":
            a = self.reg[reg_a]
            b = self.reg[reg_b]
            if a > b:
                self.flag = GFLAG
            elif a < b:
                self.flag = LFLAG
            else:
                self.flag = EFLAG
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def handleHLT(self, a=None, b=None):
        self.running = False

    def handleLDI(self, a, b):
        self.reg[a] = b
        self.pc += 3

    def handlePRN(self, a, b=None):
        print(self.reg[a])
        self.pc += 2

    def handleADD(self, a, b):
        self.alu('ADD', a, b)
        self.pc += 3

    def handleMUL(self, a, b):
        self.reg[a] = self.reg[a] * self.reg[b]
        self.pc += 3

    def handlePUSH(self, a, b=None):
        # decrement stack pointer
        self.stack_pointer -= 1
        self.stack_pointer &= 0xff  # keep in range of 00-FF

        # get register number and value stored at specified reg number
        reg_num = self.ram[self.pc + 1]
        val = self.reg[reg_num]

        # store value in ram
        self.ram[self.stack_pointer] = val
        self.pc += 2

    def handlePOP(self, a, b=None):
        # get value from RAM
        val = self.ram[self.stack_pointer]

        # store at given register
        reg_num = self.ram[self.pc + 1]
        self.reg[reg_num] = val

        # increment stack pointer and program counter
        self.stack_pointer += 1
        self.stack_pointer &= 0xff  # keep in range of 00-FF

        self.pc += 2

    def handleCALL(self, a, b):
        # return counter, save to stack
        rc = self.pc + 2
        self.stack_pointer -= 1
        self.ram[self.stack_pointer] = rc

        self.pc = self.reg[a]

    def handleRET(self, a, b):
        # pop from stack
        val = self.ram[self.stack_pointer]
        # set pc back to previous
        self.pc = val
        # increment stack pointer
        self.stack_pointer += 1

    def handleCMP(self, a, b):
        self.alu('CMP', a, b)
        self.pc += 3

    def handleJMP(self, a, b):
        self.pc = self.reg[a]

    def run(self):
        """Run the CPU."""

        while self.running:

            IR = self.ram_read(self.pc)
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)
            if IR not in self.branchtable:
                print(f'unknown instruction {IR} at address {self.pc}')
                self.running = False
            else:
                f = self.branchtable[IR]
                f(operand_a, operand_b)
