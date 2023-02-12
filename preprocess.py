from util import *

import os

##! Suppose as mips eq mipseb
ARCH_LIST = ["arm_32", "arm_64", "x86_32", "x86_64", "mips_32", "mips_64"]

##! Directories composed of package names are located in the src_path.
def flatten(src_dir_path, dst_dir_path):
  p = get_pool()
  os.system("mkdir -p %s" % (dst_dir_path))
  
  for package_dir_name in os.listdir(src_dir_path):
    package_dir_path = os.path.join(src_dir_path, package_dir_name)
    ##! cp occurs 'Argument list too long error'
    cmd = "for i in %s/*; do cp \"$i\" %s; done" % (package_dir_path, dst_dir_path)
    print("[*]", package_dir_name)

    p.apply_async(func=exec_cmd, args=(cmd, ))
  end_pool(p)


def rename(src_dir_path, dst_dir_path):
  p = get_pool()
  os.system("mkdir -p %s" % (dst_dir_path))
  
  file_names = os.listdir(src_dir_path)
  file_names.sort()
  
  for file_name in file_names:
    spl = file_name.split("_")
    pkg, comp, arch, opti = spl[0], spl[1], spl[2] + "_" + spl[3], spl[4]
    bin_name = '_'.join(spl[5:])
    
    ##! filtering mipseb_32/64 here
    if arch in ("mipseb_32", "mipseb_64"): continue

    bin_name = bin_name.replace('_', '-')

    ##! Rename Ofast to Of
    if opti == "Ofast": opti = "Of"

    if file_name.endswith(".elf"):
      eprint("Check file name")
    else:
      new_name = '_'.join([pkg, bin_name, comp, arch, opti]) + ".elf"

    src_file_path = os.path.join(src_dir_path, file_name)
    dst_file_path = os.path.join(dst_dir_path, new_name)
    cmd = "mv %s %s" % (src_file_path, dst_file_path)
    
    p.apply_async(func=exec_cmd, args=(cmd, ))
  end_pool(p)


def dump(src_dir_path, dst_dir_path):
  p = get_pool()
  os.system("mkdir -p %s" % (dst_dir_path))

  file_names = os.listdir(src_dir_path)
  file_names.sort()
  
  objdump_path = "tools/llvm-objdump"
  objdump_options = "--disassemble --section=.text --no-show-raw-insn --no-print-imm-hex"
  cmd_base = "%s %s %s > %s" % (objdump_path, objdump_options, "%s", "%s")

  for file_name in file_names:
    print("[*] objdump:", file_name)
    file_path = os.path.join(src_dir_path, file_name)
    if file_name.endswith(".elf"): file_name = file_name[:-4]
    target_path = os.path.join(dst_dir_path, file_name + ".txt")
    cmd = cmd_base % (file_path, target_path)
    
    p.apply_async(func=exec_cmd, args=(cmd, ))
  end_pool(p)

def truncate_single(file_name, src_dir_path, dst_dir_path):
  file_path = os.path.join(src_dir_path, file_name)
  file_data = read_file(file_path)
  new_file_data = []
  file_data = file_data[5:]
  for line in file_data:
    if not line or "..." in line: continue ##! "..." means skipped zeros
    elif line.endswith(':'): ##! symbol
      addr, symbol = line.split(' ')
      if '$' in symbol: continue ##! data symbol
      symbol = symbol[:-1] ##! <func>: => <func>
      new_line = "\n%s :: %s :: %s" % ('s', addr, symbol)
    else: ##! insn or data
      if ".word" in line: continue ##! data
      spl = line.split(':')
      addr = spl[0]
      insn = ''.join(spl[1:]).strip()
      if insn.find("@ ") > 0:
        idx = insn.find("@ ")
        insn = insn[:idx].strip()
      if insn.rfind("# ") > 0:
        idx = insn.rfind("# ")
        insn = insn[:idx].strip()
      if insn.endswith('>'):
        idx = insn.rfind('<')
        insn = insn[:idx].strip()
        if not insn: continue ##! <unknown>
      new_line = "%s :: %s :: %s" % ('i', addr, insn)
    new_file_data.append(new_line + '\n')
  
  file_info = get_file_info(file_name)
  arch = file_info["arch"]
  dst_file_path = os.path.join(dst_dir_path, arch, file_name)
  
  print("[*]", file_name)
  write_file(dst_file_path, new_file_data)

def truncate(src_dir_path, dst_dir_path):
  p = get_pool()
  
  os.system("mkdir -p %s" % (dst_dir_path))
  for arch in ARCH_LIST:
    os.system("mkdir -p %s" % (os.path.join(dst_dir_path, arch)))

  file_names = os.listdir(src_dir_path)
  file_names.sort()

  for file_name in file_names:
    p.apply_async(func=truncate_single, args=(file_name, src_dir_path, dst_dir_path, ))
  end_pool(p)


def main():
  # flatten("storage/original", "storage/binary/flatten")
  # rename("storage/binary/flatten", "storage/binary/renamed")
  ##! dup here: renamed -> unique
  dump("storage/binary/unique", "storage/assembly/dump")
  truncate("storage/assembly/dump", "storage/assembly/truncate")
  pass

if __name__ == "__main__":
  main()
  
  

# EOF
