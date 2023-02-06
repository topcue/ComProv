## Dump BINKIT binaries

import os
import sys

def get_file_names(dir_path):
  file_names = []
  for path in os.listdir(dir_path):
    if os.path.isfile(os.path.join(dir_path, path)):
        file_names.append(path)
  return file_names

def dump(dir_path):
  file_names = get_file_names(dir_path)
  
  cmd = "dotnet run --project ~/B2R2/src/RearEnd/BinDump -- --section=.text {} > {}"
  cnt = 1
  for file_name in file_names:
    print("[{} / {}] {}".format(cnt, len(file_names), file_name))
    cnt += 1

    src = dir_path + '/' + file_name
    dst = "tmp/" + file_name + ".txt"
    print(cmd.format(src, dst))
    # os.system(cmd.format(src, dst))

def main():
  ## pass BINKIT path
  dump("../BINS" + "/" + sys.argv[1])

if __name__ == "__main__":
  main()

# EOF
