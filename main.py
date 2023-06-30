from bdb import effective
from math import fabs
from os import stat
import re
import pprint
import gc
from tempfile import tempdir

gc.disable()
global_pc = 0 
global branch_flag
branch_flag = False
global instructions_encountered 
instructions_encountered = 0
global branches_encountered
branches_encountered = 0
global branches_mispredicted
branches_mispredicted = 0


class RS:
  def __init__(self, name, busy, op, vj, vk, qj, qk, a,pc, inst_name):
    self.name = name
    self.busy = busy
    self.op = op
    self.vj = vj
    self.vk = vk
    self.qj = qj
    self.qk = qk
    self.a = a
    self.pc = pc
    self.inst_name = inst_name


class RegisterStat:
  def __init__(self, R0, R1, R2, R3, R4, R5, R6, R7):
    self.R0 = R0 
    self.R1 = R1
    self.R2 = R2
    self.R3 = R3
    self.R4 = R4
    self.R5 = R5
    self.R6 = R6
    self.R7 = R7
    

global current_clock_cycle
current_clock_cycle = -1

branchFlag = False
output_dict= {}

load1 = RS('load1','N','-','-','-','-','-','-',0,'-')
load2 = RS('load2','N','-','-','-','-','-','-',0,'-')
store1 = RS('store1','N','-','-','-','-','-','-',0,'-')
store2 = RS('store2','N','-','-','-','-','-','-',0,'-')
branch_res = RS('beq','N','-','-','-','-','-','-',0,'-')
JalRet = RS('jal','N','-','-','-','-','-','-',0,'-')
add1 = RS('add1','N','-','-','-','-','-','-',0,'-')
add2 = RS('add2','N','-','-','-','-','-','-',0,'-')
add3 = RS('add3','N','-','-','-','-','-','-',0,'-')
negat = RS('neg','N','-','-','-','-','-','-',0,'-')
nand_res = RS('nand','N','-','-','-','-','-','-',0,'-')
mult = RS('mul','N','-','-','-','-','-','-',0,'-')

all_stations    = [  'add1','add2','add3','load1','load2','store1','store2','mult','JalRet','nand_res','negat','branch_res']


RegisterStatInst = RegisterStat('-','-','-','-','-','-','-','-') 

register_List = {'R0':0,
                 'R1':0,
                 'R2':0,
                 'R3':0,
                 'R4':0,
                 'R5':0,
                 'R6':0,
                 'R7':0}

mem = [None] * 1000

add_stations    = ['add1','add2','add3']
load_stations   = ['load1','load2']
store_stations  = ['store1','store2']
branch_stations = ['branch_res']
JalRet_stations = ['JalRet']
neg_stations    = ['negat']
nand_stations   = ['nand_res']
mul_stations    = ['mult']

value = ''
address = ''
pc=0
load_store_dict = {}
label_dict={}
print("Please Enter The Starting Address : ")
starting_address = input()
global_pc = int(starting_address)

print("\n")
print("---------------------------------------------------------------------------")

print("Please Enter The Memory Address Followed by The Value You Want to Input  : ")
print("---------To stop entering values enter x for both memory and value---------")

while(address != 'x' or value != 'x' ):
  print("Address : ")
  address = input()
  print("Value : ")
  value = input()
  if address != 'x' and value != 'x':
    mem[int(address)] = int(value)



def wb(clock_cycle):
  global global_pc
  global branch_flag
  global branches_encountered
  global branches_mispredicted
  for station in all_stations:
    if globals()[station].pc == '-' or output_dict[globals()[station].pc]['end_exec'] == current_clock_cycle:
        continue
    temp_index = globals()[station].pc
    if output_dict[temp_index]['end_exec'] != '-':
      if globals()[station].inst_name =='nand' or globals()[station].inst_name =='mul' or globals()[station].inst_name =='add' or globals()[station].inst_name =='neg':
        rd = output_dict[temp_index]['rd']
        rs1 = output_dict[temp_index]['rs1']
        rs2 = output_dict[temp_index]['rs2']

        if globals()[station].inst_name =='nand':
          temp = nand(rd,rs1,rs2)
        
        if globals()[station].inst_name =='add':
          temp = add(rd,rs1,rs2)
          
        if globals()[station].inst_name =='mul':
          temp = mul(rd,rs1,rs2)

        if globals()[station].inst_name == "neg":
            temp = neg(rd, rs1)

        if getattr(RegisterStatInst, rd) == station:
          setattr(RegisterStatInst,rd,'-')
        
        for station2 in all_stations:
            if globals()[station2].qj == station:
                globals()[station2].vj = temp
                globals()[station2].qj = '-'

            if globals()[station2].qk == station:
                globals()[station2].vk = temp
                globals()[station2].qk = '-'
        
        globals()[station].name = station
        globals()[station].busy = 'N'
        globals()[station].op = '-'
        globals()[station].vj = '-'
        globals()[station].vk = '-'
        globals()[station].qj = '-'
        globals()[station].qk = '-'
        globals()[station].a = '-'
        globals()[station].pc = '-'
        globals()[station].inst_name = '-'
        output_dict[temp_index]['wb'] = clock_cycle
        return True

        break
        
      elif globals()[station].inst_name =='addi':
        rd = output_dict[temp_index]['rd']
        rs1 = output_dict[temp_index]['rs1']
        imm = output_dict[temp_index]['imm']

        temp = addi(rd,rs1,int(imm))
        
       
        if getattr(RegisterStatInst, rd) == station:
          setattr(RegisterStatInst,rd,'-')
        
        for station2 in all_stations:
            if globals()[station2].qj == station:
                globals()[station2].vj = temp
                globals()[station2].qj = '-'

            if globals()[station2].qk == station:
                globals()[station2].vk = temp
                globals()[station2].qk = '-'


        
        globals()[station].name = station
        globals()[station].busy = 'N'
        globals()[station].op = '-'
        globals()[station].vj = '-'
        globals()[station].vk = '-'
        globals()[station].qj = '-'
        globals()[station].qk = '-'
        globals()[station].a = '-'
        globals()[station].pc = '-'
        globals()[station].inst_name = '-'
        output_dict[temp_index]['wb'] = clock_cycle
        return True
        break
        
      elif globals()[station].inst_name =='ret':
        rd = output_dict[temp_index]['rd']
        rs1 = output_dict[temp_index]['rs1']
        
       
        if getattr(RegisterStatInst, rd) == station:
          setattr(RegisterStatInst,rd,'-')
        
        
        branch_flag = False
        global_pc = globals()[station].vj
        
        globals()[station].name = station
        globals()[station].busy = 'N'
        globals()[station].op = '-'
        globals()[station].vj = '-'
        globals()[station].vk = '-'
        globals()[station].qj = '-'
        globals()[station].qk = '-'
        globals()[station].a = '-'
        globals()[station].pc = '-'
        globals()[station].inst_name = '-'
        output_dict[temp_index]['wb'] = clock_cycle
        return True

      elif globals()[station].inst_name =='jal':
        label = output_dict[temp_index]['label']
        register_List['R1'] = globals()[station].a + 1
        global_pc = label_dict[label]
        
        globals()[station].name = station
        globals()[station].busy = 'N'
        globals()[station].op = '-'
        globals()[station].vj = '-'
        globals()[station].vk = '-'
        globals()[station].qj = '-'
        globals()[station].qk = '-'
        globals()[station].a = '-'
        globals()[station].pc = '-'
        globals()[station].inst_name = '-'
        branch_flag = False
        output_dict[temp_index]['wb'] = clock_cycle
        return True

      if globals()[station].inst_name =='beq':
        rs1 = output_dict[temp_index]['rs1']
        rs2 = output_dict[temp_index]['rs2']
        label = output_dict[temp_index]['label']
        branches_encountered += 1
        if globals()[station].vk == globals()[station].vj:
          global_pc = label_dict[label]
          branches_mispredicted += 1
        else:
          global_pc = global_pc+1
        
        globals()[station].name = station  
        globals()[station].busy = 'N'
        globals()[station].op = '-'
        globals()[station].vj = '-'
        globals()[station].vk = '-'
        globals()[station].qj = '-'
        globals()[station].qk = '-'
        globals()[station].a = '-'
        globals()[station].pc = '-'
        globals()[station].inst_name = '-'
        branch_flag = False
        output_dict[temp_index]['wb'] = clock_cycle
        return True
        break
                
      if globals()[station].inst_name =='load':

        rd = output_dict[temp_index]['rd']
        rs1 = output_dict[temp_index]['rs1']
        imm = output_dict[temp_index]['imm']
        temp = register_List[rs1] + int(imm)
        register_List[rd] = load_store_dict[globals()[station].pc]['memory_state'][temp]

        for station2 in all_stations:
            if globals()[station2].qj == station:
                globals()[station2].vj = load_store_dict[globals()[station].pc]['memory_state'][temp]
                globals()[station2].qj = '-'

            if globals()[station2].qk == station:
                globals()[station2].vk = load_store_dict[globals()[station].pc]['memory_state'][temp]
                globals()[station2].qk = '-'

        load_store_dict[globals()[station].pc]['done'] = 'Y'
        globals()[station].name = station
        globals()[station].busy = 'N'
        globals()[station].op = '-'
        globals()[station].vj = '-'
        globals()[station].vk = '-'
        globals()[station].qj = '-'
        globals()[station].qk = '-'
        globals()[station].a = '-'
        globals()[station].pc = '-'
        globals()[station].inst_name = '-'
        
        output_dict[temp_index]['wb'] = clock_cycle
        return True
        break
        
      if globals()[station].inst_name =='store':

        rd = output_dict[temp_index]['rd']
        rs1 = output_dict[temp_index]['rs1']
        imm = output_dict[temp_index]['imm']
        temp = register_List[rs1] + int(imm)
        mem[temp] =  register_List[rd] 
        load_store_dict[globals()[station].pc]['done'] = 'Y'
        globals()[station].name = station
        globals()[station].busy = 'N'
        globals()[station].op = '-'
        globals()[station].vj = '-'
        globals()[station].vk = '-'
        globals()[station].qj = '-'
        globals()[station].qk = '-'
        globals()[station].a = '-'
        globals()[station].pc = '-'
        globals()[station].inst_name = '-'
        
        output_dict[temp_index]['wb'] = clock_cycle

        return True
        break
  return False

  
def execute(current_clock_cycle):
  for station in all_stations:
      temp_index = globals()[station].pc
      if globals()[station].inst_name =='nand' or globals()[station].inst_name =='add' or globals()[station].inst_name =='mul' or globals()[station].inst_name =='beq':
        if globals()[station].qj == '-' and globals()[station].qk == '-' and output_dict[temp_index]['issue'] != '-' and output_dict[temp_index]['start_exec'] == '-':
          output_dict[temp_index]['start_exec'] = current_clock_cycle
          output_dict[temp_index]['end_exec'] = '-'

        if output_dict[temp_index]['start_exec'] == '-':
            continue
        if (current_clock_cycle - int(output_dict[temp_index]['start_exec'])) == 2 and globals()[station].inst_name =='add':
          output_dict[temp_index]['end_exec'] = current_clock_cycle
        elif (current_clock_cycle - output_dict[temp_index]['start_exec']) == 1 and globals()[station].inst_name =='nand':
          output_dict[temp_index]['end_exec'] = current_clock_cycle
        elif (current_clock_cycle - output_dict[temp_index]['start_exec']) == 8 and globals()[station].inst_name =='mul':
          output_dict[temp_index]['end_exec'] = current_clock_cycle
        elif (current_clock_cycle - output_dict[temp_index]['start_exec']) == 1 and globals()[station].inst_name =='beq':
          output_dict[temp_index]['end_exec'] = current_clock_cycle  


      
      elif globals()[station].inst_name == 'neg' or globals()[station].inst_name == 'addi' or  globals()[station].inst_name =='ret':
          if globals()[station].qj == '-' and output_dict[temp_index]['issue'] != '-' and output_dict[temp_index]['start_exec'] == '-':
            temp_index = globals()[station].pc
            output_dict[temp_index]['start_exec'] = current_clock_cycle
            output_dict[temp_index]['end_exec'] = '-'
          if output_dict[temp_index]['start_exec'] == '-':
            continue
          if (current_clock_cycle - output_dict[temp_index]['start_exec']) == 1 and globals()[station].inst_name =='neg':
              output_dict[temp_index]['end_exec'] = current_clock_cycle
          elif (current_clock_cycle - output_dict[temp_index]['start_exec']) == 2 and globals()[station].inst_name =='addi':
              output_dict[temp_index]['end_exec'] = current_clock_cycle
          elif (current_clock_cycle - output_dict[temp_index]['start_exec']) == 1 and globals()[station].inst_name =='ret':
              output_dict[temp_index]['end_exec'] = current_clock_cycle

      elif globals()[station].inst_name == 'jal':
          if output_dict[temp_index]['issue'] != '-' and output_dict[temp_index]['start_exec'] == '-':
              temp_index = globals()[station].pc
              output_dict[temp_index]['start_exec'] = current_clock_cycle
              output_dict[temp_index]['end_exec'] = '-'
          if output_dict[temp_index]['start_exec'] == '-':
            continue
          if (current_clock_cycle - output_dict[temp_index]['start_exec']) == 1 and globals()[station].inst_name =='jal':
              output_dict[temp_index]['end_exec'] = current_clock_cycle
      
      elif globals()[station].inst_name == 'load':
          temp_index = globals()[station].pc
          
          if globals()[station].qj == '-' and output_dict[temp_index]['issue'] != '-' and output_dict[temp_index]['start_exec'] == '-' :
            for key in load_store_dict:
              index_of_load_or_store = list(load_store_dict.keys())
              temp_load_store_index = index_of_load_or_store.index(key)
              temp_index_index = index_of_load_or_store.index(temp_index)
              while temp_load_store_index <= temp_index_index:
                if load_store_dict[key]['l_or_s'] == 'S' and load_store_dict[key]['effective_address'] == load_store_dict[temp_index]['effective_address'] and load_store_dict[key]['done'] != 'Y' :
                  break
                else:
                  globals()[station].a = globals()[station].vj + int(globals()[station].a)
                  output_dict[temp_index]['start_exec'] = current_clock_cycle
                  output_dict[temp_index]['end_exec'] = '-'
                break
              

          if output_dict[temp_index]['start_exec'] == '-':
                continue
          if (current_clock_cycle - output_dict[temp_index]['start_exec']) == 6 and globals()[station].inst_name =='load':
              output_dict[temp_index]['end_exec'] = current_clock_cycle
        
            
      elif globals()[station].inst_name == 'store':
          temp_index = globals()[station].pc
          
          if globals()[station].qj == '-' and output_dict[temp_index]['issue'] != '-' and output_dict[temp_index]['start_exec'] == '-':
            for key in load_store_dict:
              index_of_load_or_store = list(load_store_dict.keys())
              temp_load_store_index = index_of_load_or_store.index(key)
              temp_index_index = index_of_load_or_store.index(temp_index)
              while temp_load_store_index <= temp_index_index:
                if load_store_dict[key]['effective_address'] == load_store_dict[temp_index]['effective_address'] and load_store_dict[key]['done'] != 'Y' :
                  break
                else:
                    globals()[station].a = globals()[station].vj + int(globals()[station].a)
                    output_dict[temp_index]['start_exec'] = current_clock_cycle
                    output_dict[temp_index]['end_exec'] = '-'
                    break
          if output_dict[temp_index]['start_exec'] == '-':
                continue
          if (current_clock_cycle - output_dict[temp_index]['start_exec']) == 2+1 and globals()[station].inst_name =='store':
              output_dict[temp_index]['end_exec'] = current_clock_cycle
    

def issue(current_clock_cycle,inst, rd, rs1,rs2,imm, pc):
  global global_pc
  global branch_flag
  flag = False
  if branch_flag == True:
    return
  if inst == 'add':
    for station in add_stations:
      station = str(station)
      if globals()[station].busy == 'N':
        if getattr(RegisterStatInst, rs1) != '-': 
          globals()[station].qj = getattr(RegisterStatInst, rs1)
        else:
          globals()[station].vj = register_List[rs1]
          globals()[station].qj = '-'
          
        if getattr(RegisterStatInst, rs2) != '-': 
          globals()[station].qk = getattr(RegisterStatInst, rs2)
        else:
          globals()[station].vk = register_List[rs2]
          globals()[station].qk = '-'
        
        globals()[station].busy = 'Y'
        globals()[station].inst_name = inst        
        globals()[station].pc = pc

        output_dict[pc]['issue'] = current_clock_cycle
        setattr(RegisterStatInst,rd,station)
        flag = True
        global_pc += 1
        break
    
  if inst == 'addi':
    for station in add_stations:
      if globals()[station].busy == 'N':
        if getattr(RegisterStatInst, rs1) != '-': 
          globals()[station].qj = getattr(RegisterStatInst, rs1)
        else:
          globals()[station].vj = register_List[rs1]
          globals()[station].qj = '-'
          
        globals()[station].busy = 'Y'
        globals()[station].inst_name = inst
        globals()[station].pc = pc       
        output_dict[pc]['issue'] = current_clock_cycle
        setattr(RegisterStatInst, rd ,station)
        global_pc += 1
        break

  if inst == 'nand':
    for station in nand_stations:
      if globals()[station].busy == 'N':
        if getattr(RegisterStatInst, rs1) != '-': 
          globals()[station].qj = getattr(RegisterStatInst, rs1)
        else:
          globals()[station].vj = register_List[rs1]
          globals()[station].qj = '-'
          
        if getattr(RegisterStatInst, rs2) != '-': 
          globals()[station].qk = getattr(RegisterStatInst, rs2)
        else:
          globals()[station].vk = getattr(RegisterStatInst, rs2)
          globals()[station].qk = '-'
          
        globals()[station].busy = 'Y'
        globals()[station].inst_name = inst
        globals()[station].pc = pc
        output_dict[pc]['issue'] = current_clock_cycle
        setattr(RegisterStatInst,rd ,station)
        global_pc += 1
      break

  if inst == 'mul':
    for station in mul_stations:
      if globals()[station].busy == 'N':
        if getattr(RegisterStatInst, rs1) != '-': 
          globals()[station].qj = getattr(RegisterStatInst, rs1)
        else:
          globals()[station].vj = register_List[rs1]
          globals()[station].qj = '-'
          
        if getattr(RegisterStatInst, rs2) != '-': 
          globals()[station].qk = getattr(RegisterStatInst, rs2)
        else:
          globals()[station].vk = register_List[rs2]
          globals()[station].qk = '-'
          
        globals()[station].busy = 'Y'
        globals()[station].inst_name = inst
        globals()[station].pc = pc
        output_dict[pc]['issue'] = current_clock_cycle
        setattr(RegisterStatInst,rd ,station)
        global_pc += 1
        break

  if inst == 'beq':
    for station in branch_stations:
      if globals()[station].busy == 'N':
        if getattr(RegisterStatInst, rs1) != '-': 
          globals()[station].qj = getattr(RegisterStatInst, rs1)
        else:
          globals()[station].vj = register_List[rs1]
          globals()[station].qj = '-'
          
        if getattr(RegisterStatInst, rs2) != '-': 
          globals()[station].qk = getattr(RegisterStatInst, rs2)
        else:
          globals()[station].vk = register_List[rs2]
          globals()[station].qk = '-'
        branch_flag = True
        globals()[station].busy = 'Y'
        globals()[station].pc = pc
        globals()[station].inst_name= inst  
        globals()[station].a = global_pc
        output_dict[pc]['issue'] = current_clock_cycle
        RegisterStatInst.R1 = station
        global_pc += 1
        break
  

  if inst == 'jal':
    for station in JalRet_stations:
      if globals()[station].busy == 'N':
        globals()[station].busy = 'Y'
        globals()[station].inst_name= inst
        globals()[station].pc = pc
        globals()[station].a = global_pc
        output_dict[pc]['issue'] = current_clock_cycle
        RegisterStatInst.R1 = station
        branch_flag = True

        global_pc += 1
        break
        
  if inst == 'ret':
    for station in JalRet_stations:
      if globals()[station].busy == 'N':
        if RegisterStatInst.R1 != '-': 
          globals()[station].qj = RegisterStatInst.R1
        else:
          globals()[station].vj = register_List['R1']
          globals()[station].qj = '-'
          
        globals()[station].busy = 'Y'
        globals()[station].inst_name = inst
        globals()[station].pc = pc
        output_dict[pc]['issue'] = current_clock_cycle
        setattr(RegisterStatInst,rd ,station)
        branch_flag = True
        global_pc += 1
        break


  if inst == 'neg':
    for station in neg_stations:
      if globals()[station].busy == 'N':
        if getattr(RegisterStatInst, rs1) != '-': 
          globals()[station].qj = getattr(RegisterStatInst, rs1)
        else:
          globals()[station].vj = register_List[rs1]
          globals()[station].qj = '-'
          
        globals()[station].busy = 'Y'
        globals()[station].inst_name = inst
        globals()[station].pc = pc
        output_dict[pc]['issue'] = current_clock_cycle
        setattr(RegisterStatInst,rd ,station)
        global_pc += 1
        break
  
  
  
  if inst == 'load':
    for station in load_stations:
      if globals()[station].busy == 'N':
        if getattr(RegisterStatInst, rs1) != '-': 
          globals()[station].qj = getattr(RegisterStatInst, rs1)
        else:
          globals()[station].vj = register_List[rs1]
          globals()[station].qj = '-'
          
        globals()[station].a = imm
        globals()[station].busy = 'Y'
        globals()[station].inst_name = inst        
        globals()[station].pc = pc
        output_dict[pc]['issue'] = current_clock_cycle
        setattr(RegisterStatInst,rd ,station)
        load_store_dict[pc]['done'] = 'N'
        global_pc += 1
        break
  
  if inst == 'store':
    for station in store_stations:
      if globals()[station].busy == 'N':
        if getattr(RegisterStatInst, rs1) != '-': 
          globals()[station].qj = getattr(RegisterStatInst, rs1)
        else:
          globals()[station].vj = register_List[rs1]
          globals()[station].qj = '-'
        
        if getattr(RegisterStatInst,rd) != '-': 
          globals()[station].qj = getattr(RegisterStatInst,rd)
        else:
          globals()[station].vj = register_List[rd]
          globals()[station].qj = '-'
          
        globals()[station].a = imm
        globals()[station].busy = 'Y'
        globals()[station].pc = pc
        output_dict[pc]['issue'] = current_clock_cycle
        globals()[station].inst_name= inst        
        load_store_dict[pc]['done'] = 'N'
        global_pc += 1
        break


def load(rd, imm, rs1):
  temp_address = mem[(int(imm) + register_List[rs1])]
  return(temp_address) 

def store(rd, imm, rs1):
  mem[(int(imm) + register_List[rs1])] = rd 

def bitExtracted(number, k, p):
    return ( ((1 << k) - 1)  &  (number >> (p-1) ) );

def add(rd,rs1,rs2):
    register_List[rd] = register_List[rs1] + register_List[rs2]
    return register_List[rd]

    
def addi(rd,rs1,imm):
    register_List[rd] = register_List[rs1] + imm
    return register_List[rd]

def mul(rd,rs1,rs2):
    register_List[rd] = register_List[rs1] * register_List[rs2]
    return register_List[rd]  


def nand(rd,rs1,rs2):
    temp_r = (register_List[rs1] & register_List[rs2]);
    temp1 = list(bin(temp_r)[2:])
    
    while len(temp1) != 16:
        temp1 = ['0'] + temp1

    counter = 0
    for num in temp1:
      if int(num) == 1:
        temp1[counter] = '0'
      elif int(num) == 0:
        temp1[counter] = '1'
            
      counter+=1

    register_List[rd] = int(''.join(temp1),2)
    return int(''.join(temp1),2)

def neg(rd, rs1):
    rs1 = register_List[rs1]
    if rs1 != 0:
        register_List[rd] = (rs1 ^ 65535) + 1
    else:
        register_List[rd] = 0   

three_register_instructions = ["mul","nand","addi"]
two_register_instructions = ["load","store"]
branch_instructions = ["jal","beq"]
zero_register_instructions = ["ret"]

with open("instructions.txt", "r") as f:
    unparsed_instructions=f.read().splitlines()

pc_label_finder=0
for instruction in unparsed_instructions:
  if ":" in instruction:
    temp_label_finder = instruction.split(':')[0]
    label_dict[temp_label_finder] = pc_label_finder
  pc_label_finder += 1

delete_list = label_dict.keys()
with open('instructions.txt') as fin, open('instructions_without_labels.txt', "w+") as fout:
    for line in fin:
        for word in delete_list:
            line = line.replace(word+':', "")
        fout.write(line)

with open("instructions_without_labels.txt", "r") as f:
    unparsed_instructions=f.read().splitlines()

program_counter = 0
for line in unparsed_instructions:
  output_dict[program_counter]={}
  program_counter +=1
  
program_counter = 0
for line in unparsed_instructions:
  output_dict[program_counter]['instruction'] = line
  program_counter +=1 

print("\n")
program_counter= 0
for line in unparsed_instructions:
    temp_dict={}
    label = '-'
    imm = '-'
    rs1 = '-'
    rs2 = '-'
    rd = '-'  
    temp = line.split(' ', 1)
    instruction = temp[0].lower()
    
    if temp[0] != 'RET':
        temp[1]=temp[1].replace(" ", "")
        temp[1] = temp[1].split(",")
        temp_array_of_registers = temp[1]

    if instruction == 'add' or instruction =='nand' or instruction == 'mul':
        rd = temp[1][0] 
        rs1 =  temp[1][1]
        rs2 = temp[1][2]
                    
    if instruction == 'addi':
        rd = temp[1][0] 
        rs1 =  temp[1][1]
        imm = (bitExtracted(int(temp[1][2]),7,1))

    if instruction == 'neg':
        rd = temp[1][0] 
        rs1 =  temp[1][1]
    if instruction == 'load':
      load_store_dict[program_counter]={}
      rd = temp[1][0] 
      src_mem =  temp[1][1]
      rs1 = re.search('\(([^)]+)', src_mem).group(1) 
      imm = src_mem.split('(')[0]
      load_store_dict[program_counter]['l_or_s'] = 'L'
      for element in mem:
        if element != None:
          temp_dict[element]= mem[element] 
      load_store_dict[program_counter]['memory_state'] = temp_dict

      load_store_dict[program_counter]['effective_address'] = mem[(int(imm) + register_List[rs1])] 
    
    if instruction == 'store':
        load_store_dict[program_counter]={}
        rd = temp[1][0] 
        dest_mem =  temp[1][1]
        rs1 = re.search('\(([^)]+)', src_mem).group(1)
        imm = src_mem.split('(')[0]
        load_store_dict[program_counter]['l_or_s']= 'S'
          
        for element in mem:
          if element != None:
            temp_dict[element]= mem[element] 
        load_store_dict[program_counter]['memory_state'] = temp_dict
        
        load_store_dict[program_counter]['effective_address'] = mem[(int(imm) + register_List[rs1])] 
        rd = temp[1][0] 
      
    if instruction == 'beq':
        rs1 = temp[1][0]
        rs2 = temp[1][1]
        label = temp[1][2]
    if instruction == 'jal':
        label = temp[1][0]

    if rd == '-':
      output_dict[program_counter]['rd'] = 'R0'
    else:  
      output_dict[program_counter]['rd'] = rd

    if rs1 == '-':
      output_dict[program_counter]['rs1'] = '-'
    else:
      output_dict[program_counter]['rs1'] = rs1

    if rs2 == '-':
      output_dict[program_counter]['rs2'] = '-'
    else:
      output_dict[program_counter]['rs2'] = rs2

    if label == '-':
      output_dict[program_counter]['label'] = '-'
    else:
      output_dict[program_counter]['label'] = label

    if imm == '-':
      output_dict[program_counter]['imm'] = '-'
    else:
      output_dict[program_counter]['imm'] = imm

    output_dict[program_counter]['start_exec'] = '-'
    output_dict[program_counter]['end_exec'] = '-'
    output_dict[program_counter]['issue'] = '-'

    
    output_dict[program_counter]['name'] = instruction
    program_counter = program_counter+1

def empty_res_stations():
  for station in all_stations:
    if globals()[station].busy == 'Y':
      return True
  return False
      

global_pc = 0
while (global_pc < len(output_dict)) or  (empty_res_stations()):
  current_clock_cycle +=1
  if global_pc < len(output_dict):
      rd = output_dict[global_pc]['rd']
      rs1 = output_dict[global_pc]['rs1']
      rs2 = output_dict[global_pc]['rs2']
      name = output_dict[global_pc]['name']
      if output_dict[global_pc]['imm']:
        imm = output_dict[global_pc]['imm']
      issue(current_clock_cycle,name, rd, rs1,rs2,imm, global_pc)

  for key in output_dict:
    rd = output_dict[key]['rd']
    rs1 = output_dict[key]['rs1']
    rs2 = output_dict[key]['rs2']
    name = output_dict[key]['name']
    if output_dict[key]['imm']:
      imm = output_dict[key]['imm']
    

    if output_dict[key]['issue'] != '-'  and output_dict[key]['issue'] != current_clock_cycle:
      execute(current_clock_cycle)
    if output_dict[key]['end_exec'] != '-' :
        if wb(current_clock_cycle ) == True:
            instructions_encountered += 1
            break

pprint.pprint(output_dict)
print("IPC: " + str(instructions_encountered/current_clock_cycle) )
if branches_encountered != 0:
    print("Branch misprediction: "+ str(branches_mispredicted * 100 / branches_encountered) + "%")
else :
    print("Branch misprediction %: No branches encountered")
print('Execution Time : ' + str(current_clock_cycle))
