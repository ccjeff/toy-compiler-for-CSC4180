#!/usr/bin/python 
# -*- coding: utf-8 -*-

import sys

class Translator:
    def __init__(self, filename):
        self.filename = filename
        self.threeAddrs = []
        self.memory = {}
        self.idCounter = 1
    
    def readFile(self):
        startFromLine = 0
        with open(self.filename) as f:
            for line in f:
                if startFromLine:
                    self.threeAddrs.append(line.rstrip())
                if line.rstrip() == "/////START COMPILING/////":
                    startFromLine = 1
        self.threeAddrs = self.threeAddrs[:-2]

    def translation(self,line):
        triplet = line.split(",")
        token = triplet[0]
        if (token == "Declare"):
            # everytime on declaration, should increase the sp by 4
            print("addi $sp,$sp,4")
            # save to memory
            self.memory[triplet[1]] = self.idCounter
            counterIdx = self.idCounter * 4
            print("sw $zero,%d($fp)" % counterIdx)
            self.idCounter+=1
        elif (token == "Store"):
            # switch on token type: intliteral or store from other variable
            # case 0: store from literal
            if (triplet[2].isdigit()):
                print("li $t1,%d" % int(triplet[2]))
                idx = self.memory.get(triplet[1]) * 4
                print("sw $t1,%d($fp)" % idx)
            else:  ## case 1: store from variable
                srcIdx = self.memory.get(triplet[2]) * 4  # addr for id2
                targetIdx = self.memory.get(triplet[1]) * 4 # addr for id1
                print("lw $t1,%d($fp)" % srcIdx)
                print("sw $t1,%d($fp)" % targetIdx)
        elif (token == "Read"):
            targetIdx = self.memory.get(triplet[1]) * 4
            print("li $v0,5") # MIPS syscall 5
            print("syscall")
            print("move $t1,$v0")
            print("sw $t1,%d($fp)" % targetIdx)
        elif (token == "Write"):
            targetIdx = self.memory.get(triplet[1]) * 4
            print("lw $t1,%d($fp)" % targetIdx)
            print("li $v0,1") # MIPS syscall 1
            print("move $a0,$t1")
            print("syscall")
        elif (token == "Add"):
            #### for add, there can be these cases: 
            #### token 1: must be a temp variable previously declared
            #### token 2: can be int or var
            #### token 3: can be int or var
            ## fix for wrong position in 3 addr when all are temp
            if (not triplet[2].isdigit()) and (not triplet[3].isdigit()):
                temp1 = triplet[1]
                temp2 = triplet[2]
                temp3 = triplet[3]
                triplet[1] = temp3
                triplet[2] = temp1
                triplet[3] = temp2
            targetIdx = self.memory.get(triplet[1]) * 4
            print("lw $t1,%d($fp)" % targetIdx)
            if (triplet[2].isdigit()):
                print("addi $t2,$t1,%d" % int(triplet[2]))
            else:
                t2Idx = self.memory.get(triplet[2]) * 4
                print("lw $t2,%d($fp)"%t2Idx)
                print("add $t2,$t1,$t2")
            if (triplet[3] == None):
                pass
            elif (triplet[3].isdigit()):
                print("addi $t3,$t2,%d" % int(triplet[3]))
            else:
                t3Idx = self.memory.get(triplet[3]) * 4
                print("lw $t3,%d($fp)"%t3Idx)
                print("add $t3,$t2,$t3")
            print("sw $t3,%d($fp)" % targetIdx)
        elif (token == "Min"):
            if (not triplet[2].isdigit()) and (not triplet[3].isdigit()):
                targetIdx = self.memory.get(triplet[3]) * 4
                r1Idx = self.memory.get(triplet[1]) * 4
                r2Idx = self.memory.get(triplet[2]) * 4
                print("lw $t1,%d($fp)" % targetIdx)
                print("lw $t2,%d($fp)" % r1Idx)
                print("lw $t3,%d($fp)"%r2Idx)
                print("sub $t1,$t2,$t3")   
                print("sw $t1,%d($fp)" % targetIdx)    
                return;
            targetIdx = self.memory.get(triplet[1]) * 4
            print("lw $t1,%d($fp)" % targetIdx)
            if (triplet[2].isdigit()):
                print("addi $t2,$t1,%d" % int(triplet[2]))
            else:
                t2Idx = self.memory.get(triplet[2]) * 4
                print("lw $t2,%d($fp)"%t2Idx)
                print("sub $t2,$t1,$t2")
            if (triplet[3].isdigit()):
                ## add negative to be equal to minus
                print("addi $t3,$t2,%d" % -int(triplet[3]))
            else:
                t3Idx = self.memory.get(triplet[3]) * 4
                print("lw $t3,%d($fp)"%t3Idx)
                print("sub $t3,$t2,$t3")
            print("sw $t3,%d($fp)" % targetIdx)



    def translationRoutine(self):
        self.readFile()
        print("move $sp,$fp")   #initializing stack pointer $29 to 0
        for i in self.threeAddrs:
            self.translation(i)


if __name__ == "__main__":
    try:
        MIPSTranslator = Translator("a.txt")
        MIPSTranslator.translationRoutine()
    except:
        sys.exit("Compile Error")