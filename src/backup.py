def parse_lst2(self):
  lst = self.lst
  lst2 = []
  
  for idx in range(len(lst)):
    insn = lst[idx]
    insn = re.split(' |, |{|}|\[|\]|!|-', insn)

    while('' in insn): insn.remove("")
    opcode = []
    reg = []
    num = []
    
    opcode.append(insn[0])
    for i in range(1, len(insn)):
      ele = insn[i]
      if ele.startswith(("0x", "#")):
        num.append(ele)
      ##! ARM 64
      # elif ele.startswith(("sp", "x", "w")): ##! register
      #   reg.append(ele)
      # elif ele.startswith(("v", "q", "d", "s", "h", "b")): ##! SIMD
      #   reg.append(ele)
      ##! ARM 32
      if ele.startswith(("0x", "#")):
        num.append(ele)
      elif ele.startswith(("sp", "fp", "lr", "pc", "ip", "r")): ##! register
        reg.append(ele)
      elif ele.startswith(("p", "q", "c", "d", "s")): ##! SIMD
        reg.append(ele)
      else:
        continue
    qqq = {}
    qqq["opcode"] = opcode
    qqq["reg"] = reg
    qqq["num"] = num
    lst2.append(qqq)
  self.lst2 = lst2

# EOF
