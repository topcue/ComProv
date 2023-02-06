from util import *
from ds_util import *

import sys
import copy
import csv
import time
import re 

import hashlib
import random

from itertools import product
from os.path import exists

dataset_header = ["file_name", "o0", "o1", "o2", "o3", "os", "of"]
dataset_rows = []

def write_dataset(dataset_path):
  with open(dataset_path, 'w', encoding='utf-8', newline='') as f_write:
    wr = csv.writer(f_write)
    wr.writerow(dataset_header)
    wr.writerows(dataset_rows)

##! Rename pkg_comp_arch_opti_bin -> pkg_bin_comp_arch_opti
def rename():
  SRC_PATH = "/Users/topcue/Desktop/renamed/"
  DST_PATH = "/Users/topcue/Desktop/renamed/"

  file_names = get_file_names(SRC_PATH)
  for file_name in file_names:
    spl = file_name.split("_")
    pkg, comp, arch, opti = spl[0], spl[1], spl[2] + "_" + spl[3], spl[4]
    bin_name = '_'.join(spl[5:])

    ##! Rename Ofast -> Of
    if opti == "Ofast": opti = "Of"

    new_name = '_'.join([pkg, bin_name, comp, arch, opti]) + ".elf"
    print("new_name:", new_name)

    src_path = SRC_PATH + file_name
    dst_path = DST_PATH + new_name
    cmd = "cp {} {}".format(src_path, dst_path)
    # print(cmd)
    # os.system(cmd)

def split_name(file_name):
  spl = file_name.split("_")

  opti = spl[-1].replace(".elf", '')
  arch = spl[-3] + '_' + spl[-2]
  comp = spl[-4]
  bin_name = '_'.join(spl[1:-4]) ##! bin_name can contain '_'
  pkg = spl[0]

  return pkg, bin_name, comp, arch, opti

##! ============================================================================

COMPILER_LIST = ["gcc-4.9.4", "gcc-5.5.0", "gcc-6.4.0", "gcc-7.3.0", "gcc-8.2.0", "gcc-9.4.0", "gcc-10.3.0", "gcc-11.2.0", "clang-4.0", "clang-5.0", "clang-6.0", "clang-7.0", "clang-8.0", "clang-9.0", "clang-10.0", "clang-11.0", "clang-12.0", "clang-13.0"]
ARCH_LIST = ["x86_32", "x86_64", "arm_32", "arm_64", "mips_32", "mips_64", "mipseb_32", "mipseb_64"]
OPTI_LIST = ["O0", "O1", "O2", "O3", "Os", "Of"]
PKG_BIN_LIST = []

def get_pkg_bin_list():
  BASE_PATH = "/Users/topcue/Desktop/renamed_incom/"
  file_names = get_file_names(BASE_PATH)

  tmp_dict = dict()
  for file_name in file_names:
    pkg, bin_name, _, _, _ = split_name(file_name)
    pkg_bin = '_'.join([pkg, bin_name])
    if pkg_bin not in tmp_dict.keys():
      tmp_dict[pkg_bin] = []
  
  global PKG_BIN_LIST
  PKG_BIN_LIST = list(tmp_dict.keys())

  # for i in PKG_BIN_LIST:
  #   print(i)

def get_hash(file_path):
  BASE_CMD = "{} -O binary --only-section=.text {} {}"
  if any(x in file_path for x in ["x86_32", "x86_64"]):
    objcopy = "x86_64-elf-objcopy"
  elif any(x in file_path for x in ["arm_32", "arm_64"]):
    objcopy = "aarch64-elf-objcopy"
  elif any(x in file_path for x in ["mips_32", "mips_64", "mipseb_32", "mipseb_64"]):
    objcopy = "mips-elf-objcopy"

  cmd = BASE_CMD.format(objcopy, file_path, "tmp.txt")
  os.system(cmd)
  output = os.popen("md5 tmp.txt").read()[-33:-1]
  
  return output

OPTIMZ_DICT = {0:"o0", 1:"o1", 2:"o2", 3:"o3", 4:"os", 5:"of"}

def multiple_index(target, lst):
  return [OPTIMZ_DICT[i] for i, ele in enumerate(lst) if ele == target]

cnt1 = 0
cnt2 = 0

def find_dup(row):
  tags = row[1:]
  o0, o1, o2, o3, os, of = row[1], row[2], row[3], row[4], row[5], row[6]
  r0, r1, r2, r3, rs, rf = [], [], [], [], [], []
  
  r0 = multiple_index(o0, tags)
  r1 = multiple_index(o1, tags)
  r2 = multiple_index(o2, tags)
  r3 = multiple_index(o3, tags)
  rs = multiple_index(os, tags)
  rf = multiple_index(of, tags)
  
  for idx, r in enumerate([r0, r1, r2, r3, rs, rf]):
    r.remove(OPTIMZ_DICT[idx])
  print(r0, r1, r2, r3, rs, rf)

  if len(r3) > 0 and len(rf) > 0:
    global cnt1
    cnt1 += 1 ## o3 of
  if len(r2) > 0 and len(r3) > 0:
    global cnt2
    cnt2 += 1 ## o2 o3




  
  # tp = (o1, o2, o3, os, of)
  # if o0 in res:
  #   print(tp.index(o0))
  
  
  pass

def main():
  BASE_PATH = "/Users/topcue/Desktop/renamed_incom/"
  # file_names = get_file_names(BASE_PATH)
  print(PKG_BIN_LIST)

  # for pkg_bin in PKG_BIN_LIST:
  for pkg_bin in ["gawk-5.2.1_pwcat"]:
    for item in product(COMPILER_LIST, ARCH_LIST, repeat=1):
      pkh_bin_comp_arch = pkg_bin + '_' + item[0] + '_' + item[1]
      row = [pkh_bin_comp_arch]
      for opti in OPTI_LIST:
        comp_arch = '_'.join(list(item))

        file_name = pkg_bin + '_' + comp_arch +  '_' + opti + ".elf"
        file_path = BASE_PATH + file_name
        # print(file_name)

        is_file_exists = exists(file_path)
        if is_file_exists:
          hash_tag = get_hash(file_path)
          row.append(hash_tag[:8])
        else:
          # row.append('x')
          row.append(str(random.random()))
      
      print(row)
      print(file_name)
      new_row = find_dup(row)
      
      dataset_rows.append(row)
  
  # for i in dataset_rows:
  #   print(i)
      
  write_dataset("tmp.csv")

  # for idx in range(0, len(file_names), 4):
  #   f1, f2, f3, f4 = file_names[idx], file_names[idx+1], file_names[idx+2], file_names[idx+3]
        
  #   common_name = f1[:-7]
  #   print(common_name)

  #   row = [common_name]
  #   for f in (f1, f2, f3, f4):
      
  #     local_cmd = cmd.format(BASE_PATH + f)

  #     ##! objdump
  #     stream = os.popen(local_cmd)
  #     output = stream.read()
  #     hash_object = hashlib.md5(output.encode('utf-8'))
  #     tag = hash_object.hexdigest()
      
  #     row.append(tag)

  #   dataset_rows.append(row)
    
  # write_dataset("ccdu_file.csv")

if __name__ == "__main__":
  get_pkg_bin_list()

  # rename()
  main()
  print(cnt1, cnt2)
  
  

# EOF
