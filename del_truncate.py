from util import *
import sys

def split_insn(line):
  if ": " not in line: eprint("parse error")
  addr, insn = line.split(": ")

  return addr, insn

def truncate(file_data):
  new_file_data = []
  for line in file_data:
    ## TODO: fix me (arm32, arm64, mips32)
    if line == "(illegal)": continue

    if is_symbol(line) or not line:
      new_line = line + '\n'
    elif ": " in line:
      addr, insn = split_insn(line)
      new_line = insn + '\n'
    else:
      eprint("file format error")
    
    new_file_data.append(new_line)
  
  ##! dumped text file must start with a symbol or an instructoin and
  ##! end with a single empty string
  new_file_data = new_file_data[1:-1]

  return new_file_data

def main(arch):
  # src_dir_path = "/Users/topcue/ComProv/storage/dump/dump/" + arch
  # dst_dir_path = "/Users/topcue/ComProv/dump/" + arch
  src_dir_path = "/Users/topcue/ComProv/storage/assembly/new_dump/" + arch
  dst_dir_path = "/Users/topcue/ComProv/new_dump/" + arch
  file_names = get_file_names(src_dir_path)
  
  for file_idx in range(len(file_names)):
  # for file_idx in range(1):
    file_name = file_names[file_idx]
    print("[{} / {}] {}".format(file_idx+1, len(file_names), file_name))
    
    src_file_path = src_dir_path + '/' + file_name
    file_data = read_file(src_file_path)

    new_file_data = truncate(file_data)

    dst_file_path = dst_dir_path + '/' + file_name
    # write_file("tmp.txt", new_file_data)
    write_file(dst_file_path, new_file_data)


if __name__ == '__main__':
  if len(sys.argv) < 2:
    print("[-] Arg Err!")
    exit(0)

  arg = sys.argv[1]
  main(arg)

  ##! run all
  # main("x86_32")
  # main("x86_64")
  # main("mips_32")
  
  # main("mips_64") ##! error new binkit
  # main("arm_32") ##! error new binkit
  
  # main("arm_64")
  
  

  pass
  

# EOF
