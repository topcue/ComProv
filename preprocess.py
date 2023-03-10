from util import *

import os

##! Suppose as mips eq mipseb
# ARCH_LIST = ["arm_32", "arm_64", "x86_32", "x86_64", "mips_32", "mips_64", "mipseb_32", "mipseb_64"]
ARCH_LIST = ["arm_32", "arm_64", "x86_32", "x86_64", "mips_32", "mips_64"]

##! Directories composed of package names are located in the src_path.
def flatten(src_dir_path, dst_dir_path):
  os.system("mkdir -p %s" % (dst_dir_path))
  
  for package_dir_name in os.listdir(src_dir_path):
    package_dir_path = os.path.join(src_dir_path, package_dir_name)
    ##! cp occurs 'Argument list too long error'
    cmd = "for i in %s/*; do cp \"$i\" %s; done" % (package_dir_path, dst_dir_path)
    print("[*]", package_dir_name)
    os.system(cmd)

def rename(src_dir_path, dst_dir_path):
  os.system("mkdir -p %s" % (dst_dir_path))
  
  file_names = os.listdir(src_dir_path)
  file_names.sort()
  
  for file_name in file_names:
    spl = file_name.split("_")
    pkg, comp, arch, opti = spl[0], spl[1], spl[2] + "_" + spl[3], spl[4]
    bin_name = '_'.join(spl[5:])
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
    os.system(cmd)


def dump(src_dir_path, dst_dir_path):
  p = get_pool()
  os.system("mkdir -p %s" % (dst_dir_path))
  for arch in ARCH_LIST:
    os.system("mkdir -p %s" % (os.path.join(dst_dir_path, arch)))
  
  objdump_path = "tools/llvm-objdump"
  opts = "-d --section=.text --no-show-raw-insn --no-print-imm-hex -M intel"
  cmd_base = "%s %s %s > %s" % (objdump_path, opts, "%s", "%s")
  
  for arch in ARCH_LIST:
    src_arch_dir_path = os.path.join(src_dir_path,  arch)
    file_names = os.listdir(src_arch_dir_path)
    file_names.sort()
    for file_name in file_names:
      print("[*] objdump:", file_name)
      file_path = os.path.join(src_dir_path, arch, file_name)
      target_path = os.path.join(dst_dir_path, arch, file_name.replace(".elf", ".txt"))
      cmd = cmd_base % (file_path, target_path)
      p.apply_async(func=exec_cmd, args=(cmd, ))
  end_pool(p)


def truncate_single(file_name, src_arch_path, dst_arch_path):
  file_path = os.path.join(src_arch_path, file_name)
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
  
  print("[*]", file_name)
  target_path = os.path.join(dst_arch_path, file_name)
  write_file(target_path, new_file_data)


def truncate(src_dir_path, dst_dir_path):
  os.system("mkdir -p %s" % (dst_dir_path))
  for arch in ARCH_LIST:
    os.system("mkdir -p %s" % (os.path.join(dst_dir_path, arch)))

  for arch in ARCH_LIST:
    print("[*] arch:", arch)
    src_arch_path = os.path.join(src_dir_path, arch)
    dst_arch_path = os.path.join(dst_dir_path, arch)
    
    file_names = os.listdir(src_arch_path)
    file_names.sort()
    p = get_pool()
    for file_name in file_names:
      args = (file_name, src_arch_path, dst_arch_path, )
      p.apply_async(func=truncate_single, args=args)
    end_pool(p)


def main():
  # flatten("storage/original", "storage/binary/flatten")
  # rename("storage/binary/flatten", "storage/binary/renamed")
  ##! remove dup here (renamed -> unique)
  # dump("storage/binary/unique", "storage/assembly/dump")
  # truncate("storage/assembly/dump", "storage/assembly/truncate")
  pass


if __name__ == "__main__":
  main()


# EOF
