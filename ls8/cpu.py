"""CPU functionality."""

import sys

LDI = 0b10000010
PRN = 0b01000111
HLT = 0b00000001
MUL = 0b10100010
PUSH = 0b01000101
POP = 0b01000110


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
        self.branchtable[PUSH] = self.handlePUSH
        self.branchtable[POP] = self.handlePOP
        self.stack_pointer = 0xf4

    def load(self):
        """Load a program into memory."""

        # # For now, we've just hardcoded a program:
        # address = 0

        # program = [
        #     # From print8.ls8
        #     0b10000010,  # LDI R0,8
        #     0b00000000,
        #     0b00001000,
        #     0b01000111,  # PRN R0
        #     0b00000000,
        #     0b00000001,  # HLT
        # ]

        # for instruction in program:
        #     self.ram[address] = instruction
        #     address += 1

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
        # elif op == "SUB": etc
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

    def handleMUL(self, a, b):
        self.reg[a] = self.reg[a] * self.reg[b]
        self.pc += 3

    def handlePUSH(self, a, b=None):
        # decrement stack pointer
        self.stack_pointer -= 1

        # get register number and value stored at specified regn umber
        reg_num = self.ram[self.pc + 1]
        val = self.reg[reg_num]

        # store value in ram
        self.ram[self.stack_pointer] = val
        self.pc += 2

    def handlePOP(self, a, b=None):
        # get value from RAM
        address = self.stack_pointer
        val = self.ram[address]

        # store at given register
        reg_num = self.ram[self.pc + 1]
        self.reg[reg_num] = val

        # increment stack pointer and program counter
        self.stack_pointer += 1
        self.pc += 2

    def run(self):
        """Run the CPU."""

        while self.running:
            # instruction register, read memory address stored in register
            # IR = self.ram_read(self.pc)
            # operand_a = self.ram_read(self.pc + 1)
            # operand_b = self.ram_read(self.pc + 2)

            # if IR == HLT:
            #     # exit
            #     self.running = False
            # elif IR == LDI:
            #     # set specified register to specified value
            #     self.reg[operand_a] = operand_b
            #     self.pc += 3
            # elif IR == PRN:
            #     # print value from specified register
            #     print(self.reg[operand_a])
            #     self.pc += 2
            # elif IR == MUL:
            #     product = self.reg[operand_a] * self.reg[operand_b]
            #     self.reg[operand_a] = product
            #     self.pc += 3
            # else:
            #     print(f'unknown instruction {IR} at address {self.pc}')
            #     self.running = False
            #     # exit ?

            IR = self.ram_read(self.pc)
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)
            if IR not in self.branchtable:
                print(f'unknown instruction {IR} at address {self.pc}')
                self.running = False
            else:
                f = self.branchtable[IR]
                f(operand_a, operand_b)
