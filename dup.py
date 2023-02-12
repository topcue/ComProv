from util import *
from ds_util import *

import random

from itertools import product
from os.path import exists
from collections import Counter

COMPILER_LIST = \
  ["gcc-4.9.4", "gcc-5.5.0", "gcc-6.5.0", "gcc-7.3.0", "gcc-8.2.0", \
   "gcc-9.4.0", "gcc-10.3.0", "gcc-11.2.0", "clang-4.0", "clang-5.0", \
   "clang-6.0", "clang-7.0", "clang-8.0", "clang-9.0", "clang-10.0", \
   "clang-11.0", "clang-12.0", "clang-13.0"]
ARCH_LIST = ["x86_32", "x86_64", "arm_32", "arm_64", \
             "mips_32", "mips_64", "mipseb_32", "mipseb_64"]
OPTI_LIST = ["O0", "O1", "O2", "O3", "Os", "Of"]
PKG_BIN_LIST = []

dataset_header = ["file_name", "O0", "O1", "O2", "O3", "Os", "Of"]

def get_pkg_bin_list(BASE_PATH):
  file_names = get_file_names(BASE_PATH)

  tmp_dict = dict()
  for file_name in file_names:
    file_info = get_file_info(file_name)
    pkg_bin = '_'.join([file_info["pkg"], file_info["bin_name"]])
    if pkg_bin not in tmp_dict.keys():
      tmp_dict[pkg_bin] = []
  
  global PKG_BIN_LIST
  PKG_BIN_LIST = list(tmp_dict.keys())


def get_hash(file_path):
  BASE_CMD = "{} -O binary --only-section=.text {} {}"
  if any(x in file_path for x in ["x86_32", "x86_64"]):
    objcopy = "x86_64-linux-gnu-objcopy"
  elif any(x in file_path for x in ["arm_32", "arm_64"]):
    objcopy = "aarch64-linux-gnu-objcopy"
  elif any(x in file_path for x in ["mips_32", "mips_64", "mipseb_32", "mipseb_64"]):
    objcopy = "mips-linux-gnu-objcopy"

  ##! Fix me: remove /tmp/tmp dir
  file_name = os.path.basename(file_path)
  cmd = BASE_CMD.format(objcopy, file_path, "/tmp/tmp/%s.txt" % file_name)
  os.system(cmd)
  output = os.popen("md5sum /tmp/tmp/%s.txt" % file_name).read()#[-33:-1]
  
  return output


def multiple_index(target, lst):
  # OPTIMZ_DICT = {0:"o0", 1:"o1", 2:"o2", 3:"o3", 4:"os", 5:"of"}
  # return [OPTIMZ_DICT[i] for i, ele in enumerate(lst) if ele == target]
  return [i for i, ele in enumerate(lst) if ele == target]


def find_dup(row, return_list):
  tags = row[1:]
  o0, o1, o2, o3, os, of = row[1], row[2], row[3], row[4], row[5], row[6]
  r0, r1, r2, r3, rs, rf = [], [], [], [], [], []
  
  r0 = multiple_index(o0, tags)
  r1 = multiple_index(o1, tags)
  r2 = multiple_index(o2, tags)
  r3 = multiple_index(o3, tags)
  rs = multiple_index(os, tags)
  rf = multiple_index(of, tags)

  new_row = [' ' for _ in range(6)]

  for idx, r in enumerate([r0, r1, r2, r3, rs, rf]):
    if len(r) == 1:
      continue
    for dup_idx in r:
      new_row[dup_idx] = 'd'
  
  result = [row[0]]
  result.extend(new_row)
  print(result)
  
  return_list.append(result)

def build_dup_list(BASE_PATH):
  p = get_pool()
  return_list = mp.Manager().list()
  
  for pkg_bin in PKG_BIN_LIST:
  # for pkg_bin in ["gawk-5.2.1_pwcat"]:
    for item in product(COMPILER_LIST, ARCH_LIST, repeat=1):
      pkg_bin_comp_arch = pkg_bin + '_' + item[0] + '_' + item[1]
      row = [pkg_bin_comp_arch]
      for opti in OPTI_LIST:
        comp_arch = '_'.join(list(item))
        file_name = pkg_bin + '_' + comp_arch +  '_' + opti + ".elf"
        file_path = os.path.join(BASE_PATH, file_name)
        is_file_exists = exists(file_path)
        if is_file_exists:
          hash_tag = get_hash(file_path)
          row.append(hash_tag[:8])
        else:
          ##! If dataset is incomplete, use random number.
          ##! But the current code assumes a complete dataset.
          eprint("not exist binary error: %s" % file_path)
          row.append(str(random.random()))
      p.apply_async(func=find_dup, args=(row, return_list, ))
  end_pool(p)

  write_dataset("dup.csv", return_list, dataset_header)


def gen_remove_list():
  remove_list = []
  dataset = load_dataset("dup.csv")
  
  for idx in dataset.index:
    flag_first = False
    file_name = dataset['file_name'][idx]
    for opti in OPTI_LIST:
      item = dataset[opti][idx]
      if item == ' ': continue
      if not flag_first:
        flag_first = True
      else:
        remove_file_name = file_name + '_' + opti
        remove_list.append(remove_file_name + '\n')
  
  write_file("remove_list.txt", remove_list)


def stat():
  dataset = load_dataset("dup.csv")
  dup_case = []
  file_names = []
  
  for idx in dataset.index:
    file_name = dataset['file_name'][idx]
    dup_list = []
    for opti in OPTI_LIST:
      item = dataset[opti][idx]
      if item == 'd':
        dup_list.append(opti)
    if dup_list:
      print("[*]", file_name, dup_list)
      file_names.append(file_name)
      dup_case.append('-'.join(dup_list))
  
  counter = Counter(dup_case)
  for item in counter.items():
    print("%s: %s" % (item[0], item[1]))


def main():
  ##! DEBUG: fix me
  BASE_PATH = "storage/binary/renamed"
  get_pkg_bin_list(BASE_PATH)
  build_dup_list(BASE_PATH)
  
  # gen_remove_list()
  # stat()


if __name__ == "__main__":
  main()


# EOF
