import os, sys

bins = ["addr2line", "ar", "as", "c++filt", "elfedit", "ld", "nm", "objcopy", "objdump", "ranlib", "readelf", "size", "strings", "strip"]

def ratio(a, b):
  a = int(a)
  b = int(b)
  result = round((a - b) / a * 100, 1)
  return result

# o1-explicit-flags  o1-fno-inline
def foo(bin):
  c0 = "dotnet run -- --diff --section=.text ~/benchmark/my/o0/{bin} omit/{bin} 2>/dev/null | tail -n2"
  c1 = "grep -r 'mov RBP, RSP' ./tmp/1_{bin}.txt | wc | awk '{{print $1}}'"
  c2 = "grep -r 'mov RBP, RSP' ./tmp2/x_{bin}.txt | wc | awk '{{print $1}}'"

  # c0 = "dotnet run -- --diff --section=.text ~/benchmark/my/o1-fno-inline/{bin} ~/benchmark/my/o1/{bin} 2>/dev/null | tail -n2"
  # c1 = "grep -r 'mov RBP, RSP' ./tmp/3_{bin}.txt | wc | awk '{{print $1}}'"
  # c2 = "grep -r 'mov RBP, RSP' ./tmp/4_{bin}.txt | wc | awk '{{print $1}}'"


  # c3 = "grep -r 'leave' ./dump/{bin}-o0.txt | wc | awk '{{print $1}}'"
  # c4 = "grep -r 'leave' ./dump/{bin}-o1.txt | wc | awk '{{print $1}}'"
  # c5 = "grep -r 'pop RBP' ./dump/{bin}-o0.txt | wc | awk '{{print $1}}'"
  # c6 = "grep -r 'pop RBP' ./dump/{bin}-o1.txt | wc | awk '{{print $1}}'"

  # c1 = "grep -r 'R13' ./dump/{bin}-o0.txt | wc | awk '{{print $1}}'"
  # c2 = "grep -r 'R13' ./dump/{bin}-o1.txt | wc | awk '{{print $1}}'"
  # c3 = "grep -r 'R14' ./dump/{bin}-o0.txt | wc | awk '{{print $1}}'"
  # c4 = "grep -r 'R14' ./dump/{bin}-o1.txt | wc | awk '{{print $1}}'"
  # c5 = "grep -r 'R15' ./dump/{bin}-o0.txt | wc | awk '{{print $1}}'"
  # c6 = "grep -r 'R15' ./dump/{bin}-o1.txt | wc | awk '{{print $1}}'"

  c0 = c0.format(bin=bin)
  c1 = c1.format(bin=bin)
  c2 = c2.format(bin=bin)
  # c3 = c3.format(bin=bin)
  # c4 = c4.format(bin=bin)
  # c5 = c5.format(bin=bin)
  # c6 = c6.format(bin=bin)

  ret0 = os.popen(c0).read()[:-1]
  ret1 = os.popen(c1).read()[:-1]
  ret2 = os.popen(c2).read()[:-1]
  # ret3 = os.popen(c3).read()[:-1]
  # ret4 = os.popen(c4).read()[:-1]
  # ret5 = os.popen(c5).read()[:-1]
  # ret6 = os.popen(c6).read()[:-1]

  symsA, symsB = ret0.split("\n")

  # print("\n[{0}]".format(bin))
  # print ("{:<18} {:<16} {:<16}".format("", "o0", "o1"))
  print ("{:<18} {:<16} {:<16}".format("symbols", symsA, symsB))
  # print ("{:<18} {:<16} {:<16}".format("mov RBP, RSP", round(100 * int(ret1) / int(symsA), 3),  round(100 * int(ret2) / int(symsB), 3)))
  print ("{:<18} {:<6} ({:<6}%) {:<6} ({:<6}%)".format("mov RBP, RSP", ret1, round(100 * int(ret1) / int(symsA), 3), ret2, round(100 * int(ret2) / int(symsB), 3)))
  # print ("{:<18} {:<6} ({:<6}%) {:<6} ({:<6}%)".format("mov RBP, RSP", ret1, 0, ret2, 0))
  # print ("{:<18} {:<6} ({:<6}%) {:<6} ({:<6}%)".format("leave", ret3, round(100 * int(ret3) / int(symsA), 3), ret4, round(100 * int(ret4) / int(symsA), 3)))
  # print ("{:<18} {:<6} ({:<6}%) {:<6} ({:<6}%)".format("ret", ret5, ratio(symsA, ret5), ret6, ratio(symsB, ret6)))

  # num_insns = os.popen("wc ./dump/{bin}-o0.txt | awk '{{print $1}}'".format(bin=bin)).read()[:-1]
  # print ("{:<8} {:<6} {:<16}".format("", "o0", "o1"))
  # print ("{:<8} {:<6} {:<6} ({:<6}%)".format("R13", ret1, ret2, round(int(ret1) / int(num_insns), 6)))
  # print ("{:<8} {:<6} {:<6} ({:<6}%)".format("R14", ret3, ret4, round(int(ret3) / int(num_insns), 6)))
  # print ("{:<8} {:<6} {:<6} ({:<6}%)".format("R15", ret5, ret6, round(int(ret5) / int(num_insns), 6)))


# for bin in bins:
#   foo(bin)

foo("as")

# EOF
