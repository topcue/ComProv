from util import *

get_pc_thunk_list = ["<__x86.get_pc_thunk.ax>", "<__x86.get_pc_thunk.bx>", "<__x86.get_pc_thunk.cx>", "<__x86.get_pc_thunk.dx>", "<__x86.get_pc_thunk.si>", "<__x86.get_pc_thunk.di>", "<__x86.get_pc_thunk.bp>"]

##! w/0 `frame_dummy()`
startup_func_list = ["<_start>", "<__start>", "<__libc_csu_init>", "<__libc_csu_fini>", "<__do_global_ctors_aux>", "<__do_global_dtors_aux>", "<register_tm_clones>", "<deregister_tm_clones>"]

##! ============================================================================

def write_file_from_funcs(file_path, dct):
  file_data = []
  for func_name, func_insns in dct.items():
    file_data.append(func_name+'\n')
    file_data.extend(map(lambda x: x + '\n', func_insns))
    file_data.append('\n')

  write_file(file_path, file_data)

def get_opcode(insn: str):
  return insn.split(' ')[0]


##! ============================================================================

def parse_functions(file_path):
  ##! DEBUG
  data = read_file(file_path)
  if not data[0]: data = data[1:]
  funcs = {}
  max_len = len(data)
    
  for line in data:
    print("[DEBUG] ", line, len(line))

  ##! step1
  ## parse the instructions at the beginning of the .text section
  ## in particular, in the mips architecture, the main() function
  ## is inlined here by optimization
  start_ptr = -1
  if is_symbol(data[0]) or not data[0]:
    start_ptr = 0
  else:
    next_idx = 0
    for curr_idx in range(0, max_len):
      line = data[curr_idx]
      if not line:
        break
      next_idx += 1
    funcs["<!_dummy_func>"] = data[0:next_idx]
    start_ptr = next_idx + 1

  ##! step2: parse function by function
  curr_idx = start_ptr
  while(curr_idx < max_len):
    line = data[curr_idx]
    if is_symbol(line):
      curr_func_name = line
      next_idx = curr_idx + 1
      while data[next_idx]: next_idx += 1
      funcs[curr_func_name] = data[curr_idx+1:next_idx]
      ##! skip empty string after end of single function
      curr_idx = next_idx + 1
    else:
      eprint("parse error!")

  ##! TODO: Fix me
  # ##! trim
  # for symbol, insns in funcs.items():
  #   print("[!]", symbol)
  #   new_symbol = []
  #   for insn in insns:
  #     new_insn = insn.replace("i :: ", '')
  #     new_symbol.apppend(new_insn)
  #   funcs[new_symbol] = my_dict.pop(old_key)

  return funcs

def filter(binary, DEBUG=False):
  funcs = binary.funcs
  arch = binary.arch
  func_to_del = []
  
  ##! 1) pre-filter list
  if arch in ["arm_32"]:
    strong_filter = ["<_start>", "<call_weak_fn>", "<__libc_csu_init>", "<__libc_csu_fini>"]
    weak_filter = ["<__do_global_dtors_aux>", "<register_tm_clones>", "<deregister_tm_clones>", "<frame_dummy>"]
    prefilter = strong_filter + weak_filter
  elif arch in ["arm_64"]:
    ## TODO:
    prefilter = [""]
  elif arch in ["x86_32", "x86_64", "mips_32", "mips_64"]:
    strong_filter = get_pc_thunk_list
    weak_filter = startup_func_list
    prefilter = strong_filter + weak_filter
  else:
    eprint("Arch Error!")
  
  for intrinsic in prefilter:
    if intrinsic in funcs.keys():
      del funcs[intrinsic]

  if arch in ["x86_32", "x86_64"]:
    call_insn = ("call")
  elif arch in ["mips_32", "mips_64"]:
    call_insn = ("jal") ##! jal or jalr

  if arch in ["x86_32", "x86_64", "mips_32", "mips_64"]:
    for func_name, func_insns in funcs.items():
      if len(func_insns) > 30: continue
      is_contain_call = False
      for insn in func_insns:
        if insn.startswith(call_insn):
          is_contain_call = True
          break
      if not is_contain_call:
        func_to_del.append(func_name)
  # elif arch in ["arm_32"]:
  #   for func_name, func_insns in funcs.items():
  #     if len(func_insns) <= 30:
  #       func_to_del.append(func_name)
  # elif arch in ["arm_64"]:
  #   for func_name, func_insns in funcs.items():
  #     if len(func_insns) > 30: continue
  #     is_contain_call = False
  #     for insn in func_insns:
  #       if insn.startswith("b"):
  #         is_contain_call = True
  #         break
  #     if not is_contain_call:
  #       func_to_del.append(func_name)

  func_to_del = list(set(func_to_del))

  for func_name in func_to_del:
    del funcs[func_name]

  lst = funcs_to_list(funcs)
  binary.funcs = funcs
  binary.lst = lst
  binary.get_general_info()

  ##! DEBUG: write filtered file
  if DEBUG:
    write_file_from_funcs("dump/filt/{}".format(binary.name), binary.funcs)
  
  return binary



# EOF
