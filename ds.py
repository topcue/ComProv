from util import *
from ds_util import *

import sys
import copy
import time
import re 

from threading import Thread

dataset_header = ["file_name", "optmz", "x1", "x2", "x3", "x4", "x5", "x6",  "xi", \
                  "arch", "num_func", "compiler", "total_insn"]

##! ============================================================================

def get_bracket_operand(x):
  ## e.g.) "mov A, B, [C]" -> return "C"
  if '[' not in x:
    return ""
  else:
    return x.split('[', 1)[1].split(']')[0]

##! ============================================================================

class Binary:
  def __init__(self, name, path, arch):
    funcs = parse_functions(path)
    insns = get_insns(funcs)
    self.name, self.path, self.arch = name, path, arch
    self.funcs, self.insns = funcs, insns
    self.get_general_info()


  def get_general_info(self):
    name = self.name
    self.compiler = get_compiler(name) ## TODO: Remove me
    self.optmz = get_optmz(name)
    self.total_insn = len(self.insns)
    self.num_func = len(self.funcs.keys())
    

  # def get_reg(self, insn):
  #   if self.arch == "x86_64": reg_set = ()
  #   elif self.arch == "arm_64": reg_set = ("sp", "x", "w")
  #   elif self.arch == "arm_32": reg_set = ("sp", "fp", "lr", "pc", "ip", "r")
  #   else: eprint("Error!!")
    
  #   insn = re.split(' |, |{|}|\[|\]|!|-', insn)
  #   while('' in insn): insn.remove('')
  #   reg = []
  #   for i in range(1, len(insn)):
  #     ele = insn[i]
  #     ##! arm:
  #     if ele.startswith(reg_set): reg.append(ele)
  #     else: continue
  #     ##! x86_64:
  #     # reg.append(ele)

  #   return reg


  def get_xs(self):
    insns = self.insns
    funcs = self.funcs
    num_func = self.num_func
    arch = self.arch
    total_insn = self.total_insn
    x1, x2, x3, x4, x5, x6 = -1, -1, -1, -1, -1, -1

    if arch == "x86_32":
      ##! 1) frame pointer omitting
      cnt_save_fp = insns.count("mov ebp, esp")
      self.xi = round(cnt_save_fp / num_func, 4)
      
      
      ##! 2) callee-saved register
      eax, ebx, ecx, edx, esi, edi = 0, 0, 0, 0, 0, 0
      for insn in insns:
        eax += insn.count("eax")
        ebx += insn.count("ebx")
        ecx += insn.count("ecx")
        edx += insn.count("edx")
        esi += insn.count("esi")
        edi += insn.count("edi")
      caller_save = eax + ecx + edx
      callee_save = ebx + esi + edi
      x1 = round(callee_save / caller_save, 4)

      ##! 2.1) push
      cnt_total, cnt = 0, 0
      for insn in insns:
        if insn.startswith("push dword"):
          cnt_total += 1
          if insn == "push dword ptr [eax]":
            cnt += 1
          else:
            cnt -= 1
          
          # op = get_bracket_operand(insn)
          # cnt_total += 1
          # if op.startswith("ebp"):
          #   cnt += 1
      x2 = round(cnt / cnt_total, 4)
      print(x2)
    

      ##! 3) memory access
      # res = []
      # for func_name, insns in funcs.items():
      #   # print("\n[*]", func_name)
      #   op_list = []
      #   for insn in insns:
      #     if insn.startswith("nop"): continue
      #     if insn.startswith("push"): continue
      #     if not "[" in insn: continue
      #     op = get_bracket_operand(insn)
      #     if op == "esp": continue
      #     op_list.append(op)
        
      #   d = {i:op_list.count(i) for i in op_list}
      #   d = {k: v for k, v in sorted(d.items(), key=lambda item: item[1], reverse=True)}
      #   s = sum(d.values())
        
      #   f = 0
      #   for k, v in d.items():
      #     if k.startswith("ebp"):
      #       if v >= 2: f += v
      #       else: f -= v
      #     else:
      #       f -= v
        
      #   x = round(f / s, 2) if s else 0
      #   res.append(x)
    
      # x2 = round(sum(res) / len(res), 4)


      ##! 4)
      # cnt_cmp, cnt_else, cnt_ebp = 0, 0, 0
      # for insn in insns:
      #   if insn.startswith("cmp"):
      #     cnt_cmp += 1
      #     if "ebp" in insn:
      #       cnt_ebp += 1
      #     else:
      #       cnt_else += 1
      
      # x1 = round(cnt_ebp / cnt_cmp, 4)


        
    elif arch == "x86_64": ##! renew
      cnt = insns.count("mov RBP, RSP")
      x1 = round(cnt / num_func, 4)
    elif arch in ["mips_32"]: ##! renew
      cnt = insns.count("or fp, sp, r0")
      x1 = round(cnt / num_func, 4)
    elif arch == "mips_64": ##! renew
      cnt = insns.count("or sp, s8, r0")
      x1 = round(cnt / num_func, 4)
    elif arch == "arm_32": ##! renew
      cnt1, cnt2, cnt3, cnt4, cnt5, cnt6 = 0, 0, 0, 0, 0, 0
      
      # for insn in insns:
      #   ##! good
      #   ##! gcc??? clang?????? scale??? ??????. scale??? ???????????? dicision boundary??? ?????????
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
      for insn in insns:
        if insn.startswith("ldr"):
          cnt_ld += 1
          if insn.startswith("ldr r0, [fp"):
            cnt1 += 1


      x1 = round(cnt1 / total_insn, 3)
      x2 = round(cnt1 / cnt_ld, 3)
    elif arch == "arm_64": ##! renew!
      cnt1, cnt2, cnt3, cnt4, cnt5, cnt6 = 0, 0, 0, 0, 0, 0
      cnt_ld, cnt_ldp = 0, 0
      cnt_st, cnt_stp = 0, 0
      cnt_x29 = 0

      for insn in insns:
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

      # x4 = round(insns.count("ldr x0, [x0]")/num_func, 2) ##! gcc 85

      # x3 = round(cnt_x29 / self.total_insn, 2) ##! clang 99, gcc 94

      # # x4 = round(cnt_ld / self.total_insn, 2) ##! ??????
      # # x5 = round(cnt_stp / (self.total_insn), 2) ##! ??????
      # # x5 = round((cnt_stp + cnt_ldp) / total_insn, 2) ##! ??????
      # # x4 = round(cnt_stp / cnt_st, 2) ##! ??????
      
      
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
        #! return insn ??????
        for idx in range(len(insns)):
          insn = insns[idx]
          if insn.startswith("pop") and any(x in insn for x in ["fp", "sp", "lr"]):
            cnt_contain_ret += 1
            if idx + 1 == len(insns): last_pos = idx
            elif insns[idx+1] == "bx lr": last_pos = idx + 1
            break
        if last_pos == -1: continue

        #! return insn ?????? ?????????
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


  def get_rows(self):
    ##! init
    self.x1, self.x2, self.x3, self.x4, self.x5, self.x6 = -1, -1, -1, -1, -1, -1
    self.xi = -1
    
    self.get_xs()
    # self.get_xi()

    row = \
      [self.name, self.optmz, \
        self.x1, self.x2, self.x3, self.x4, self.x5, self.x6, \
        self.xi, \
        self.arch, self.num_func, self.compiler, self.total_insn]
    return row


##! ============================================================================


def foo(file_name, dump_path, arch, dataset_rows):
  pkl_path = os.path.join("pkl", arch)
  pkl_file_path = os.path.join(pkl_path, file_name.replace(".txt", ".pkl"))
  
  use_pickle = True
  if use_pickle:
    binary = read_pickle(pkl_file_path)
  else:
    file_path = os.path.join(dump_path, file_name)
    binary = Binary(file_name, file_path, arch)
    binary = filter(binary, False)
    ##! Comment out if not needed
    # write_pickle(pkl_file_path, binary)
    # with open("filt/" + file_name, "w") as f:
    #   for func_name, insns in binary.funcs.items():
    #     f.write(func_name + '\n')
    #     for insn in insns: f.write("%s\n" % (insn))
    #     f.write('\n')
    # return
  
  print("[+]", binary.name)
  
  row = binary.get_rows()
  dataset_rows.append(row)


def build_dataset(arch: str, debug: str):
  os.system("mkdir -p %s" % (os.path.join("pkl", arch)))
  
  dump_path = "storage/assembly/truncate/%s" % (arch)
  file_names = get_file_names(dump_path)

  dataset_rows = mp.Manager().list()
  p = get_pool()
  
  if debug == 'd':
    file_names = ["spell-1.1_spell_gcc-7.3.0_x86_32_O0.txt", "spell-1.1_spell_clang-7.0_x86_32_O0.txt", "spell-1.1_spell_gcc-7.3.0_x86_32_O1.txt", "spell-1.1_spell_clang-7.0_x86_32_O1.txt", "spell-1.1_spell_gcc-7.3.0_x86_32_O2.txt", "spell-1.1_spell_clang-7.0_x86_32_O2.txt", "spell-1.1_spell_gcc-7.3.0_x86_32_O3.txt", "spell-1.1_spell_clang-7.0_x86_32_O3.txt", "spell-1.1_spell_gcc-7.3.0_x86_32_Os.txt", "spell-1.1_spell_clang-7.0_x86_32_Os.txt", "spell-1.1_spell_gcc-7.3.0_x86_32_Of.txt", "spell-1.1_spell_clang-7.0_x86_32_Of.txt"]
    for file_name in file_names:
      foo(file_name, dump_path, arch, dataset_rows)
  else:
    for file_name in file_names:
      if file_name[0] <= 'c' or file_name[0] > 'i': continue
      p.apply_async(func=foo, args=(file_name, dump_path, arch, dataset_rows, ))
    end_pool(p)

  dataset_path = "dataset/dataset_{}.csv".format(arch)
  write_dataset(dataset_path, dataset_rows, dataset_header)
  os.system("cp %s %s" % (dataset_path, "/home/topcue/OneDrive/Sync/"))


if __name__ == "__main__":
  if len(sys.argv) < 2: eprint("Arg Err!")  
  arch = sys.argv[1]
  debug = sys.argv[2]
  build_dataset(arch, debug)


# EOF
