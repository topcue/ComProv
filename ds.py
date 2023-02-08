from util import *
from ds_util import *

import sys
import copy
import csv
import time
import re 

dataset_header = ["file_name", "optmz", "x1", "x2", "x3", "x4", "x5", "x6",  "xi", \
                  "arch", "num_func", "compiler", "total_insn"]
dataset_rows = []

##! ============================================================================

def get_total_insn(funcs):
  return sum(len(insns) for insns in funcs.values())

def write_dataset(dataset_path):
  with open(dataset_path, 'w', encoding='utf-8', newline='') as f_write:
    wr = csv.writer(f_write)
    wr.writerow(dataset_header)
    wr.writerows(dataset_rows)

def get_bracket_operand(x):
  ## e.g.) "mov A, B, [C]" -> return "C"
  return x.split('[', 1)[1].split(']')[0]

##! ============================================================================

class Binary:
  def __init__(self, name, path, arch):
    funcs = parse_functions(path)
    # lst = funcs_to_list(funcs)

    self.name = path
    self.path = path
    # self.lst = lst
    # self.funcs = funcs
    # self.get_general_info()
    eprint("exit here")
    exit()
  
  def get_general_info(self):
    name = self.name
    funcs = self.funcs
    self.arch = get_arch(name)
    self.compiler = get_compiler(name) ## TODO: Remove me
    self.optmz = get_optmz(name)
    self.total_insn = get_total_insn(funcs)
    self.num_func = len(funcs.keys())
  
  def get_reg(self, insn):
    if self.arch == "x86_64": reg_set = ()
    elif self.arch == "arm_64": reg_set = ("sp", "x", "w")
    elif self.arch == "arm_32": reg_set = ("sp", "fp", "lr", "pc", "ip", "r")
    else: eprint("Error!!")
    
    insn = re.split(' |, |{|}|\[|\]|!|-', insn)
    while('' in insn): insn.remove('')
    reg = []
    for i in range(1, len(insn)):
      ele = insn[i]
      ##! arm:
      if ele.startswith(reg_set): reg.append(ele)
      else: continue
      ##! x86_64:
      # reg.append(ele)

    return reg

  def get_xs(self):
    lst = self.lst
    funcs = self.funcs
    num_func = self.num_func
    arch = self.arch
    total_insn = self.total_insn
    x1, x2, x3, x4, x5, x6 = -1, -1, -1, -1, -1, -1

    if arch == "x86_32":
      cnt = lst.count("mov EBP, ESP")
      x1 = round(cnt / num_func, 4)
    elif arch == "x86_64":
      cnt = lst.count("mov RBP, RSP")
      x1 = round(cnt / num_func, 4)
    elif arch in ["mips_32"]:
      cnt = lst.count("or fp, sp, r0")
      x1 = round(cnt / num_func, 4)
    elif arch == "mips_64":
      cnt = lst.count("or sp, s8, r0")
      x1 = round(cnt / num_func, 4)
    elif arch == "arm_32":
      cnt1, cnt2, cnt3, cnt4, cnt5, cnt6 = 0, 0, 0, 0, 0, 0
      
      # for insn in lst:
      #   ##! good
      #   ##! gcc랑 clang이랑 scale이 다름. scale만 해결하면 dicision boundary는 깔끔함
      #   if "r0, [fp" in insn:
      #     cnt1 += 1
      #   ##! good
      #   if insn.startswith(("ld", "st")):
      #     if "fp" in insn: cnt2 += 1
      #     # elif "sp" in insn: cnt2 += 1
      #     # if insn.startswith("ld"): cnt3 += 1
      #   if insn.startswith(("mov fp, sp", "mov sp, fp")): cnt4 += 1 ##! clang
      #   elif insn.startswith(("add fp, sp", "sub sp, fp")): cnt5 += 1 ##! gcc
      #   ##! work
      #   if insn.startswith("push"):
      #     cnt3 += insn.count("r")
      #     if "lr" in insn: cnt3 -= 1
      #     cnt6 += insn.count("r4")
      # x1 = round(cnt1 / self.total_insn, 3)
      # x2 = round(cnt2 / num_func, 3)
      # x3 = round(cnt3 / num_func, 3)
      # x4 = round(cnt4 / num_func, 3)
      # x5 = round(cnt5 / num_func, 3)
      # x6 = round(cnt6 / num_func, 3)


      ##! ===================================================
      cnt_ld = 0
      for insn in lst:
        if insn.startswith("ldr"):
          cnt_ld += 1
          if insn.startswith("ldr r0, [fp"):
            cnt1 += 1


      x1 = round(cnt1 / total_insn, 3)
      x2 = round(cnt1 / cnt_ld, 3)
    elif arch == "arm_64":
      cnt1, cnt2, cnt3, cnt4, cnt5, cnt6 = 0, 0, 0, 0, 0, 0
      cnt_ld, cnt_ldp = 0, 0
      cnt_st, cnt_stp = 0, 0
      cnt_x29 = 0

      for insn in lst:
        if insn.startswith("ld"):
          cnt_ld += 1
          if insn.startswith("ldp"):
            cnt_ldp += 1
            if "x29, x30" in insn or "x0, x1" in insn: cnt1 += 1
          if "[" in insn and "x29" in get_bracket_operand(insn): cnt_x29 += 1
        elif insn.startswith("st"):
          cnt_st += 1
          if insn.startswith("stp"):
            cnt_stp += 1
            if "x29, x30" in insn:
              cnt2 += 1
          if "[" in insn and "x29" in get_bracket_operand(insn): cnt_x29 += 1
          if "[x0" in insn: cnt3 += 1

      cnt_st -= cnt_stp
      if cnt_st == 0: cnt_st = 1
      cnt_ld -= cnt_ldp
      
      x1 = round(cnt1 / cnt_ldp, 2)
      x2 = round((cnt_stp + cnt_ldp) / (cnt_st + cnt_ld), 2)
      x3 = round((cnt_stp - cnt2) / cnt_st, 2) ##! clang 100

      # x4 = round(lst.count("ldr x0, [x0]")/num_func, 2) ##! gcc 85

      # x3 = round(cnt_x29 / self.total_insn, 2) ##! clang 99, gcc 94

      # # x4 = round(cnt_ld / self.total_insn, 2) ##! 별로
      # # x5 = round(cnt_stp / (self.total_insn), 2) ##! 별로
      # # x5 = round((cnt_stp + cnt_ldp) / total_insn, 2) ##! 별로
      # # x4 = round(cnt_stp / cnt_st, 2) ##! 별로
      
      
      # # x5 = round(cnt3 / total_insn, 2) ##! X
      # # x5 = round((cnt_stp - cnt2) / num_func, 2) ##! X
      
      ##! callee-saved reg
      for k, v in funcs.items():
        for insn in v:
          if "x19" in insn:
            if "x19" in self.get_reg(insn):
              cnt6 += 1
              break

      x6 = round(cnt6/num_func, 3)
    else: eprint("arch error!")

    self.x1, self.x2, self.x3, self.x4, self.x5, self.x6 = x1, x2, x3, x4, x5, x6
  
  def get_xi(self):
    funcs = self.funcs
    arch = self.arch
    
    xi = -1

    if arch in ["x86_32", "x86_64", "mips_64"]:
      cnt_contain_ret = 0
      cnt_inlined = 0

      if arch in ["x86_32", "x86_64"]: tp = ("call", "j", "ret")
      elif arch in "mips_64": tp = ("b", "ret")
      
      for func_name, insns in funcs.items():
        if not insns.count("ret"): continue
    
        cnt_contain_ret += 1
        max_len = len(insns)
        ret_pos = insns.index("ret")
        flag = False
        for idx in range(ret_pos+1, max_len):
          curr_insn = insns[idx]
          if curr_insn.startswith(tp):
            flag = True
            break
        if flag:
          cnt_inlined += 1
      xi = round(cnt_inlined / cnt_contain_ret, 4) if cnt_contain_ret != 0 else -1
    elif arch in ["mips_32", "mips_64"]:
      xi = -1
    elif arch in ["arm_32"]:
      cnt_contain_ret = 0
      cnt_inlined = 0
      for func_name, insns in funcs.items():
        last_pos = -1
        #! return insn 찾기
        for idx in range(len(insns)):
          insn = insns[idx]
          if insn.startswith("pop") and any(x in insn for x in ["fp", "sp", "lr"]):
            cnt_contain_ret += 1
            if idx + 1 == len(insns): last_pos = idx
            elif insns[idx+1] == "bx lr": last_pos = idx + 1
            break
        if last_pos == -1: continue

        #! return insn 이후 있는지
        for idx in range(last_pos+1, len(insns)):
          curr_insn = insns[idx]
          if curr_insn != "(illegal)" and "eq" not in curr_insn:
            cnt_inlined += 1
            break
          
      #! heuristic: only optimized binaries' cnt_contain_ret is 0
      xi = round(cnt_inlined / cnt_contain_ret, 4) if cnt_contain_ret != 0 else 1
    elif arch in ["arm_64"]:
      cnt_contain_ret = 0
      cnt_inlined = 0
      tp = ("b", "ret")
      for func_name, insns in funcs.items():
        if not insns.count("ret"): continue
    
        cnt_contain_ret += 1
        max_len = len(insns)
        ret_pos = insns.index("ret")
        flag = False
        for idx in range(ret_pos+1, max_len):
          curr_insn = insns[idx]
          if curr_insn.startswith(tp):
            flag = True
            break
        if flag:
          cnt_inlined += 1
      xi = round(cnt_inlined / cnt_contain_ret, 4) if cnt_contain_ret != 0 else -1

    self.xi = xi

  def get_row(self):
    self.get_xs()
    # x1, x2, x3, x4, x5, x6 = -1, -1, -1, -1, -1, -1
    # self.x1, self.x2, self.x3, self.x4, self.x5, self.x6 = x1, x2, x3, x4, x5, x6
    
    # self.get_xi()
    self.xi = -1

    row = \
      [self.name, self.optmz, \
        self.x1, self.x2, self.x3, self.x4, self.x5, self.x6, \
        self.xi, \
        self.arch, self.num_func, self.compiler, self.total_insn]
    return row

## =============================================================================

def build_dataset(arch: str):
  dump_path = "storage/assembly/truncate/%s" % (arch)
  file_names = get_file_names(dump_path)
  num_files = len(file_names)
  
  ##! DEBUG
  for file_idx in range(0, 1):
  # for file_idx in range(num_files):
    file_name = file_names[file_idx]
    print("[*] ({} / {}) {}".format(file_idx+1, num_files, file_name))
    
    ##! DEBUG
    use_pickle = False
    if use_pickle:
      pkl_path = "pkl/" + arch + "/" + file_name[:-3] + "pkl"
      binary = read_pickle(pkl_path)
    else:
      file_path = os.path.join(dump_path, file_name)
      binary = Binary(file_name, file_path, arch)
      # binary = filter(binary, False)
    
      # write_pickle(pkl_path, binary)

    # row = binary.get_row()
    # dataset_rows.append(row)

  # dataset_path = "dataset/dataset_{}.csv".format(arch) ##!
  # write_dataset(dataset_path)

if __name__ == "__main__":
  if len(sys.argv) < 2: eprint("Arg Err!")  
  arg = sys.argv[1]

  build_dataset(arg)



# EOF
