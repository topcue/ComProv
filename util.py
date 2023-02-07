import os
import pickle
import multiprocessing as mp

NUM_CORES = 12

def eprint(message):
  print("[-] {}".format(message))
  exit(0)

def get_pool():
  return mp.Pool(NUM_CORES)

def end_pool(p):
  p.close()
  p.join()

def exec_cmd(cmd: str):
  os.system(cmd)

def write_pickle(path: str, data):
  with open(path, "wb") as f:
    pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)
  
def read_pickle(path: str):
  with open(path, 'rb') as f:
    data = pickle.load(f)
  return data

def write_file(file_path, file_data):
  with open(file_path, "w") as f:
    f.writelines(file_data)

def read_file(file_path):
  with open(file_path, 'r') as f:
    file_data = f.readlines()
    file_data = list(map(lambda s: s.strip(), file_data))
    file_data.append('')

  return file_data

def get_file_names(dir_path):
  file_names = []
  for path in os.listdir(dir_path):
    if os.path.isfile(os.path.join(dir_path, path)):
      file_names.append(path)
  return sorted(file_names)

def print_dict(dct):
  for k in dct.keys():
    print(); print(k)
    for insn in dct[k]: print(insn)

# def dict_to_list(dct):
#   lst = []
#   for func_name, func_insns in dct.items():
#     lst.append(func_name)
#     lst.extend(func_insns)
#     lst.append('')
#   return lst

def funcs_to_list(dct):
  lst = []
  for func_insns in dct.values():
    lst.extend(func_insns)
  return lst

##! ============================================================================

def is_symbol(line):
  if not line: return False
  if line.startswith('s'): return True
  return False

def get_optmz(file_name):
  if "O0" in file_name: return 0
  elif "O1" in file_name: return 1
  elif "O2" in file_name: return 2
  elif "O3" in file_name: return 3
  elif "Os" in file_name: return 4
  elif "Of" in file_name: return 5
  else: eprint("get_optmz() error")

def get_arch(file_name):
  if "x86_32" in file_name: return "x86_32"
  elif "x86_64" in file_name: return "x86_64"
  elif "mips_32" in file_name: return "mips_32"
  elif "mips_64" in file_name: return "mips_64"
  elif "arm_32" in file_name: return "arm_32"
  elif "arm_64" in file_name: return "arm_64"
  else: eprint("get_optmz() arch")

def get_compiler(file_name):
  if "gcc" in file_name: return "gcc"
  elif "clang" in file_name: return "clang"
  else: eprint("get_compiler() error")

# EOF
