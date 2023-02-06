import os
import sys
import csv

def get_file_names(dir_path):
  file_names = []
  for path in os.listdir(dir_path):
    if os.path.isfile(os.path.join(dir_path, path)):
      file_names.append(path)
  return file_names

def get_file_data(file_path):
  f = open(file_path, "r")
  file_data = f.readlines()
  f.close()
  return file_data

def build_header(dataset_path, header):
  f = open(dataset_path, 'w', encoding='utf-8', newline='')
  wr = csv.writer(f)
  wr.writerow(header)
  f.close()

def get_optmz_level(file_name):
  if "O0" in file_name: return 0
  elif "O1" in file_name: return 1
  elif "O2" in file_name: return 2
  elif "O3" in file_name: return 3

def get_total_insn(file_data):
  cnt = 0
  for line in file_data:
    if line[0] == "<" and line[-2] == ">":
      continue
    cnt += 1
  return cnt

def get_func_num(file_data):
  cnt = 0
  for line in file_data:
    if line[0] == "<" and line[-2] == ">":
      cnt += 1
  return cnt

def main(arch):
  dump_path = "dump" + "/" + arch
  ## TODO: file name
  dataset_path = "dataset/dataset_{}.csv".format(arch)

  file_names = get_file_names(dump_path)
  file_names.sort()

  ## build header
  header = ["file_name", "optmz", "ft1", "func_num", "total_insn", "insn1", "insn2", "ft2"]
  build_header(dataset_path, header)
  
  f_dataset_csv = open(dataset_path, 'a', encoding='utf-8', newline='')
  wr = csv.writer(f_dataset_csv)
  
  cnt = 1
  max_len = len(file_names)
  for file_name in file_names:
    print("[*] ({} / {}) {}".format(cnt, max_len, file_name))
    cnt += 1
    
    file_data = get_file_data(dump_path + "/" + file_name)
    
    ## optmz level
    optmz_level = get_optmz_level(file_name)

    ## total_insn
    total_insn = get_total_insn(file_data)

    ## func_nums
    func_num = get_func_num(file_data)

    ## TODO: filter
    # if func_num <= 15: continue
    # if "gcc" not in file_name: continue

    insn1_cnt = 0
    insn2_cnt = 0
    for line in file_data:
      ## x86
      if "mov RBP, RSP" in line or "mov EBP, ESP" in line:
        insn1_cnt += 1

      ## mips
      # if "or fp, sp, r0" in line:
      #   insn1_cnt += 1

      ## arm_32
      ## clang
      # if "mov fp, sp" in line:
      #   insn1_cnt += 1
      ## gcc
      # if "add fp, sp" in line:
      #   insn2_cnt += 1

      ## arm_32
      # if "fp" in line:
      #   insn1_cnt += 1

      ## arm_64
      # if "x29" in line:
      #   insn1_cnt += 1
      # if "sp" in line:
      #   insn2_cnt += 1
      # if "stp" in line:
      #   insn1_cnt -= 1

    ## x86, mips
    ft1 = round(float(insn1_cnt)/float(func_num), 5)

    ## arm
    # ft1 = round( (float(insn1_cnt)+float(insn2_cnt))/float(total_insn), 5 )
    ft2 = 0
    
    ["file_name", "optmz", "ft1", "func_num", "total_insn", "insn1", "insn2", "ft2"]
    wr.writerow([file_name, optmz_level, ft1, func_num, total_insn, insn1_cnt, insn2_cnt, ft2])


if __name__ == "__main__":
  if len(sys.argv) != 2:
    print("[-] Arg Err!")
    exit(0)
  
  arch = sys.argv[1]
  main(arch)


# EOF
