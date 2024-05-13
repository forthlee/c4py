import sys
import re
import struct

class MemoryManager:
    def __init__(self, size):
        self.memory = bytearray(size)
        self.next_free = 0
        self.size = size

    def malloc(self, size):
        if self.next_free + size <= self.size:
            ptr = self.next_free
            self.next_free += size
            return ptr
        else:
            return None

    def free(self, ptr):
        pass

    def __getitem__(self, key):
        return self.memory[key] 

    def __setitem__(self, key, value):
        if isinstance(key, slice):
            self.memory[key] = value
        elif isinstance(value, int):
            if sys.byteorder == 'little':
                format_str = '<q'
            else:
                format_str = '>q'
            self.memory[key:key+8] = struct.pack(format_str, value)
        elif isinstance(value, str):
            encoded_word = value.encode('utf-8')
            self.memory[key:key+len(encoded_word)] = encoded_word

def memcmp(addr1, addr2, size):
  for i in range(0, size):
   if mem[addr1+i] != mem[addr2+i]:
     return 1
  return 0

def memset(addr, val, size):
  for i in range(size):
    mem[addr+i] = chr(val)
  return 1

def memInt(ptr):
    return struct.unpack('q', mem[ptr:ptr+8])[0]

def memStr(ptr):
    size = 0
    while mem[ptr+size] !=0:
      size += 1
    x = mem[ptr:ptr+size]
    s = mem[ptr:ptr+size].decode('utf-8')
    return s

def fmtSplit(fmt):
    pattern = r'%(\d*\.*\d*)([dfds]+|c)'
    matches = re.findall(pattern, fmt.replace('%.*', '%d %'))
    return [match[1] for match in matches]

def fmtTrans(fmt, n , x):
    s = fmt[n]
    if s == 's':
        return memStr(memInt(x))
    elif s == 'd' or s == 'f':
        return memInt(x)
    else:
        return mem[x]

poolsz = 256*1024
mem = MemoryManager(poolsz*16)

p = lp = 0
e = le = 0 
data  = 0
id    = 0
sym   = 0 
tk    = 0
ival  = 0
ty    = 0 
loc   = 0
line  = 0
src   = 0
debug = 0

( Num, Fun, Sys, Glo, Loc, Id,
  Char, Else, Enum, If, Int, Return, Sizeof, While,
  Assign, Cond, Lor, Lan, Or, Xor, And, Eq, Ne, Lt, Gt, Le, Ge, Shl, Shr, Add, Sub, Mul, Div, Mod, Inc, Dec, Brak ) = range(128, 128+37)

( LEA ,IMM ,JMP ,JSR ,BZ  ,BNZ ,ENT ,ADJ ,LEV ,LI  ,LC  ,SI  ,SC  ,PSH ,
  OR  ,XOR ,AND ,EQ  ,NE  ,LT  ,GT  ,LE  ,GE  ,SHL ,SHR ,ADD ,SUB ,MUL ,DIV ,MOD ,
  OPEN,READ,CLOS,PRTF,MALC,FREE,MSET,MCMP,GETC,EXIT) = range(40)

( CHAR, INT, PTR ) = range(3)
( Tk, Hash, Name, Class, Type, Val, HClass, HType, HVal, Idsz ) = [i*8 for i in range(10)]

def next():
  global p, pp, lp, le, line, id, tk, data, ival

  while ((tk:=source[p]) != '\0'):
    p += 1
    if (tk == '\n'):
      if (src): 
        print(f"{line}: {source[lp:p]}", end="")
        lp = p
        while (le < e):          
          le += 8
          print("    {:8.4s}".format("LEA ,IMM ,JMP ,JSR ,BZ  ,BNZ ,ENT ,ADJ ,LEV ,LI  ,LC  ,SI  ,SC  ,PSH ,"
                                     "OR  ,XOR ,AND ,EQ  ,NE  ,LT  ,GT  ,LE  ,GE  ,SHL ,SHR ,ADD ,SUB ,MUL ,DIV ,MOD ,"
                                     "OPEN,READ,CLOS,PRTF,MALC,FREE,MSET,MCMP,GETC,EXIT,"[mem[le] * 5:mem[le] * 5+4]), end="")
          if (mem[le] <= ADJ): le += 8; print(memInt(le)) 
          else: print()
      line += 1 
    elif (tk == '#'):
      while (source[p] != '\0' and source[p] != '\n'): p += 1
    elif ((tk >= 'a' and tk <= 'z') or (tk >= 'A' and tk <= 'Z') or tk == '_'):
      pp = p - 1
      tk = ord(tk)
      while ((source[p] >= 'a' and source[p] <= 'z') or
             (source[p] >= 'A' and source[p] <= 'Z') or 
             (source[p] >= '0' and source[p] <= '9') or
              source[p] == '_'):
          tk = tk * 147 + ord(source[p]);  p += 1
      tk = (tk << 6) + (p - pp)
      id = sym

      while memInt(id+Tk) != 0: 
        if tk == memInt(id+Hash) and source[memInt(id+Name):memInt(id+Name)+p-pp]==source[pp:p]:
          tk = memInt(id+Tk)          
          return
        id = id + Idsz
      mem[id+Name] = pp 
      mem[id+Hash] = tk
      tk = mem[id+Tk] = Id
      return

    elif (tk >= '0' and tk <= '9'):
      if ((ival:=int(tk))):
        while (source[p] >= '0' and source[p] <= '9'): ival = ival * 10 + int(source[p]); p += 1
      elif (source[p] == 'x' or source[p] == 'X'):
        p += 1
        while ((tk:=source[p]) and 
               ((tk >= '0' and tk <= '9') or 
                (tk >= 'a' and tk <= 'f') or 
                (tk >= 'A' and tk <= 'F'))):
          ival = ival * 16 + (ord(tk) & 15) + (9 if tk >= 'A' else 0)
          p += 1
      else:
        while (source[p] >= '0' and source[p] <= '7'): ival = ival * 8 + int(source[p]); p += 1
      tk = Num
      return
    elif (tk == '/'):
      if (source[p] == '/'):
        p += 1
        while (source[p] != '\0' and source[p] != '\n'): p += 1
      else:
        tk = Div
        return
    elif (tk == '\'' or tk == '"'):
      pp = data
      while (source[p] != '\0' and source[p] != tk):
        if ((ival:=source[p]) == '\\'): 
          p += 1
          if ((ival:=source[p]) == 'n'): 
            p += 1
            ival = '\n'
          else: p += 1
        else: p += 1
        if (tk == '"'):        
          x = ival.encode('utf-8')   
          mem[data:data+len(x)] = x
          data += len(x)
      p += 1
      if (tk == '"'): 
        ival = pp
      else: tk = Num 
      return
    elif (tk == '='): 
      if (source[p] == '='): p += 1; tk = Eq  
      else: tk = Assign
      return
    elif (tk == '+'): 
      if (source[p] == '+'): p += 1; tk = Inc 
      else: tk = Add
      return
    elif (tk == '-'): 
      if (source[p] == '-'): p += 1; tk = Dec 
      else: tk = Sub
      return
    elif (tk == '!'): 
      if (source[p] == '='): p += 1; tk = Ne
      return
    elif (tk == '<'): 
      if   (source[p] == '='): p += 1; tk = Le
      elif (source[p] == '<'): p += 1; tk = Shl 
      else: tk = Lt
      return
    elif (tk == '>'): 
      if   (source[p] == '='): p += 1; tk = Ge
      elif (source[p] == '>'): p += 1; tk = Shr 
      else: tk = Gt
      return
    elif (tk == '|'): 
      if (source[p] == '|'): p += 1; tk = Lor
      else: tk = Or
      return
    elif (tk == '&'): 
      if (source[p] == '&'): p += 1; tk = Lan
      else: tk = And
      return
    elif (tk == '^'): tk = Xor;  return
    elif (tk == '%'): tk = Mod;  return
    elif (tk == '*'): tk = Mul;  return
    elif (tk == '['): tk = Brak; return
    elif (tk == '?'): tk = Cond; return
    elif (tk == '~' or tk == ';' or tk == '{' or tk == '}' or tk == '(' or tk == ')' or tk == ']' or tk == ',' or tk == ':'): return

def expr(lev):
  global e, data, ty
  t = d = 0

  if (tk == 0): print(f"{line}: unexpected eof in expression"); exit(-1)
  elif (tk == Num): mem[e:=e+8] = IMM; mem[e:=e+8] = ival; next(); ty = INT
  elif (tk == '"'):
    mem[e:=e+8] = IMM; mem[e:=e+8] = ival
    next()
    while (tk == '"'): next()
    data = (data + 8) & (-8); ty = PTR
  elif (tk == Sizeof):
    next()
    if (tk == '('): next()
    else: print(f"{line}: open paren expected in sizeof"); exit(-1)
    ty = INT
    if    (tk == Int):  next()
    elif  (tk == Char): next(); ty = CHAR
    while (tk == Mul):  next(); ty = ty + PTR
    if (tk == ')'): next()
    else: print(f"{line}: close paren expected in sizeof"); exit(-1)
    mem[e:=e+8] = IMM; mem[e:=e+8] = 1  if (ty == CHAR) else 8
    ty = INT
  elif (tk == Id):
    d = id; next()
    if (tk == '('):
      next()
      t = 0
      while (tk != ')'): 
        expr(Assign); mem[e:=e+8] = PSH; t += 1
        if (tk == ','): next()
      next()
      if (memInt(d+Class) == Sys):        
        mem[e:=e+8] = memInt(d+Val)
      elif (memInt(d+Class) == Fun):         
        mem[e:=e+8] = JSR; mem[e:=e+8] = memInt(d+Val)
      else: print(f"{line}: bad function call"); exit(-1)
      if (t):         
        mem[e:=e+8] = ADJ; mem[e:=e+8] = t
      ty = memInt(d+Type)
    elif (memInt(d+Class) == Num):
      mem[e:=e+8] = IMM; mem[e:=e+8] = memInt(d+Val); ty = INT
    else:
      if   (memInt(d+Class) == Loc): mem[e:=e+8] = LEA; mem[e:=e+8] = loc - memInt(d+Val)
      elif (memInt(d+Class) == Glo): mem[e:=e+8] = IMM; mem[e:=e+8] = memInt(d+Val)
      else: print(f"{line}: undefined variable"); exit(-1)
      mem[e:=e+8] = LC if ((ty:=memInt(d+Type)) == CHAR) else LI 
  elif (tk == '('):
    next()
    if (tk == Int or tk == Char):
      t = INT if tk == Int else CHAR; next()
      while (tk == Mul): next(); t += PTR
      if (tk == ')'): next() 
      else: print(f"{line}: bad cast"); exit(-1)
      expr(Inc)
      ty = t
    else:
      expr(Assign)
      if (tk == ')'): next() 
      else: print(f"{line}: close paren expected"); exit(-1)
  elif (tk == Mul):
    next(); expr(Inc)
    if (ty > INT): ty -= PTR 
    else: print(f"{line}: bad dereference"); exit(-1)
    mem[e:=e+8] = LC if (ty == CHAR) else LI
  elif (tk == And):
    next(); expr(Inc)
    if (mem[e] == LC or mem[e] == LI): e -= 8 
    else: print(f"{line}: bad address-of"); exit(-1)
    ty += PTR
  elif (tk == '!'): next(); expr(Inc); mem[e:=e+8] = PSH; mem[e:=e+8] = IMM; mem[e:=e+8] =  0; mem[e:=e+8] = EQ;  ty = INT
  elif (tk == '~'): next(); expr(Inc); mem[e:=e+8] = PSH; mem[e:=e+8] = IMM; mem[e:=e+8] = -1; mem[e:=e+8] = XOR; ty = INT
  elif (tk == Add): next(); expr(Inc); ty = INT
  elif (tk == Sub):
    next(); mem[e:=e+8] = IMM
    if (tk == Num): mem[e:=e+8] = -ival; next() 
    else: mem[e:=e+8] = -1; mem[e:=e+8] = PSH; expr(Inc); mem[e:=e+8] = MUL
    ty = INT
  elif (tk == Inc or tk == Dec):
    t = tk; next(); expr(Inc)
    if   (mem[e] == LC): mem[e] = PSH; mem[e:=e+8] = LC
    elif (mem[e] == LI): mem[e] = PSH; mem[e:=e+8] = LI
    else: print(f"{line}: bad lvalue in pre-increment"); exit(-1)
    mem[e:=e+8] = PSH
    mem[e:=e+8] = IMM; mem[e:=e+8] = 8 if (ty > PTR) else 1
    mem[e:=e+8] = ADD if (t == Inc)   else SUB
    mem[e:=e+8] = SC  if (ty == CHAR) else SI
  else: print(f"{line}: bad expression"); exit(-1)

  while (tk if isinstance(tk, int) else ord(tk))  >= lev:
    t = ty
    if (tk == Assign):
      next()
      if (mem[e] == LC or mem[e] == LI): mem[e] = PSH 
      else: print(f"{line}: bad lvalue in assignment"); exit(-1)
      expr(Assign); mem[e:=e+8] = SC if ((ty:=t) == CHAR) else SI
    elif (tk == Cond):
      next()
      mem[e:=e+8] = BZ; d = (e:=e+8)
      expr(Assign)
      if (tk == ':'): next() 
      else: print(f"{line}: conditional missing colon"); exit(-1)
      mem[d] = e + 24; mem[e:=e+8] = JMP; d = (e:=e+8)
      expr(Cond)
      mem[d] = e + 8
    elif (tk == Lor): next(); mem[e:=e+8] = BNZ; d = (e:=e+8); expr(Lan); mem[d] = e + 8; ty = INT
    elif (tk == Lan): next(); mem[e:=e+8] = BZ;  d = (e:=e+8); expr(Or);  mem[d] = e + 8; ty = INT
    elif (tk == Or) : next(); mem[e:=e+8] = PSH; expr(Xor); mem[e:=e+8] = OR;  ty = INT
    elif (tk == Xor): next(); mem[e:=e+8] = PSH; expr(And); mem[e:=e+8] = XOR; ty = INT
    elif (tk == And): next(); mem[e:=e+8] = PSH; expr(Eq);  mem[e:=e+8] = AND; ty = INT
    elif (tk == Eq):  next(); mem[e:=e+8] = PSH; expr(Lt);  mem[e:=e+8] = EQ;  ty = INT
    elif (tk == Ne):  next(); mem[e:=e+8] = PSH; expr(Lt);  mem[e:=e+8] = NE;  ty = INT
    elif (tk == Lt):  next(); mem[e:=e+8] = PSH; expr(Shl); mem[e:=e+8] = LT;  ty = INT
    elif (tk == Gt):  next(); mem[e:=e+8] = PSH; expr(Shl); mem[e:=e+8] = GT;  ty = INT
    elif (tk == Le):  next(); mem[e:=e+8] = PSH; expr(Shl); mem[e:=e+8] = LE;  ty = INT
    elif (tk == Ge):  next(); mem[e:=e+8] = PSH; expr(Shl); mem[e:=e+8] = GE;  ty = INT
    elif (tk == Shl): next(); mem[e:=e+8] = PSH; expr(Add); mem[e:=e+8] = SHL; ty = INT
    elif (tk == Shr): next(); mem[e:=e+8] = PSH; expr(Add); mem[e:=e+8] = SHR; ty = INT
    elif (tk == Add):
      next(); mem[e:=e+8] = PSH; expr(Mul)
      if ((ty := t) > PTR): mem[e:=e+8] = PSH; mem[e:=e+8] = IMM; mem[e:=e+8] = 8; mem[e:=e+8] = MUL
      mem[e:=e+8] = ADD
    elif (tk == Sub):
      next(); mem[e:=e+8] = PSH; expr(Mul)
      if (t > PTR and t == ty): mem[e:=e+8] = SUB; mem[e:=e+8] = PSH; mem[e:=e+8] = IMM; mem[e:=e+8] = 8;   mem[e:=e+8] = DIV; ty = INT
      elif ((ty := t) > PTR):   mem[e:=e+8] = PSH; mem[e:=e+8] = IMM; mem[e:=e+8] = 8;   mem[e:=e+8] = MUL; mem[e:=e+8] = SUB
      else: mem[e:=e+8] = SUB
    elif (tk == Mul): next(); mem[e:=e+8] = PSH; expr(Inc); mem[e:=e+8] = MUL; ty = INT
    elif (tk == Div): next(); mem[e:=e+8] = PSH; expr(Inc); mem[e:=e+8] = DIV; ty = INT
    elif (tk == Mod): next(); mem[e:=e+8] = PSH; expr(Inc); mem[e:=e+8] = MOD; ty = INT
    elif (tk == Inc or tk == Dec):
      if   (mem[e] == LC): mem[e] = PSH; mem[e:=e+8] = LC
      elif (mem[e] == LI): mem[e] = PSH; mem[e:=e+8] = LI
      else: print(f"{line}: bad lvalue in post-increment"); exit(-1)
      mem[e:=e+8] = PSH; mem[e:=e+8] = IMM; mem[e:=e+8] = 8 if (ty > PTR) else 1
      mem[e:=e+8] = ADD if(tk == Inc)  else SUB
      mem[e:=e+8] = SC  if(ty == CHAR) else SI
      mem[e:=e+8] = PSH; mem[e:=e+8] = IMM; mem[e:=e+8] = 8 if (ty > PTR) else 1
      mem[e:=e+8] = SUB if (tk == Inc) else ADD
      next()
    elif (tk == Brak):
      next(); mem[e:=e+8] = PSH; expr(Assign)
      if (tk == ']'): next()
      else: print(f"{line}: close bracket expected"); exit(-1)
      if (t > PTR): mem[e:=e+8] = PSH; mem[e:=e+8] = IMM; mem[e:=e+8] = 8; mem[e:=e+8] = MUL
      elif (t < PTR): print(f"{line}: pointer type expected"); exit(-1)
      mem[e:=e+8] = ADD
      mem[e:=e+8] = LC if ((ty:=t-PTR) == CHAR) else LI
    else: print(f"{line}: compiler error tk={tk}"); exit(-1)

def stmt():
  global tk,e
  a = b = 0

  if (tk == If):
    next()
    if (tk == '('): next() 
    else: print(f"{line}: open paren expected"); exit(-1)
    expr(Assign)
    if (tk == ')'): next() 
    else: print(f"{line}: close paren expected"); exit(-1)
    mem[e:=e+8] = BZ; b = (e:=e+8)
    stmt()
    if (tk == Else):
      mem[b] = (int)(e + 24); mem[e:=e+8] = JMP; b = (e:=e+8)
      next()
      stmt()
    mem[b] = (int)(e + 8)
  elif (tk == While):
    next()
    a = e + 8
    if (tk == '('): next() 
    else: print(f"{line}: open paren expected"); exit(-1)
    expr(Assign)
    if (tk == ')'): next() 
    else: print(f"{line}: close paren expected"); exit(-1)
    mem[e:=e+8] = BZ; b = (e:=e+8)
    stmt()
    mem[e:=e+8] = JMP; mem[e:=e+8] = a
    mem[b] = (int)(e + 8)
  elif (tk == Return):
    next()
    if (tk != ';'): expr(Assign)
    mem[e:=e+8] = LEV
    if (tk == ';'): next() 
    else: print(f"{line}: semicolon expected"); exit(-1)
  elif (tk == '{'):
    next()
    while (tk != '}'): stmt()
    next()
  elif (tk == ';'):
    next()
  else:
    expr(Assign)
    if (tk == ';'): 
      next()
    else: print(f"{line}: semicolon expected"); exit(-1)

if __name__=='__main__':
  fd = bt = ty = idmain = 0
  pc = sp = p = a = cycle = 0
  i = t = 0
  fd = 0
  keybuf = []
  
  args = sys.argv[1:]
  if len(args)> 0 and args[0] == '-s': 
   src = 1; args = args[1:]
  if len(args)> 0 and args[0] == '-d': 
    debug = 1; args = args[1:]
  if len(args) < 1:
    print(f"usage: python c4py.py [-s] [-d] file ...\n")
    sys.exit(1)

  sym = mem.malloc(poolsz)
  if ((e    := mem.malloc(poolsz)) == 0): print(f"could not malloc({poolsz}) text area\n");  exit(-1)
  if ((data := mem.malloc(poolsz)) == 0): print(f"could not malloc({poolsz}) data area\n");  exit(-1)
  if ((sp   := mem.malloc(poolsz)) == 0): print(f"could not malloc({poolsz}) stack area\n"); exit(-1)
  le = e
  
  source = "char else enum if int return sizeof while open read close printf malloc free memset memcmp getchar exit void main"
  source += '\0'
  p = 0
  i = Char
  while (i <= While): 
    next(); mem[id+Tk] = i; i += 1 

  i = OPEN
  while (i <= EXIT): 
    next(); mem[id+Class] = Sys; mem[id+Type] = INT; mem[id+Val] = i; i += 1
  next(); mem[id+Tk] = Char
  next(); idmain = id

  lp = p = len(source)

  with open(args[0], 'r') as f: 
    source2 = f.read()
  source = source + source2 + '\0'

  line = 1
  next()

  while (tk != '\0'):    
    bt = INT
    if tk == Int:
      next() 
    elif (tk == Char): next(); bt = CHAR
    elif (tk == Enum): 
      next()
      if (tk != '{'): next()
      if (tk == '{'):
        next()
        i = 0
        while (tk != '}'):
          if (tk != Id): print(f"{line}: bad enum identifier {tk}"); sys.exit(1)
          next()
          if (tk == Assign): 
            next()
            if (tk != Num): print(f"{line}: bad enum initializer"); sys.exit(1)
            i = ival
            next()
          mem[id+Class] = Num; mem[id+Type] = INT; mem[id+Val] = i; i += 1
          if (tk == ','): next()
        next()
    while (tk != ';' and tk != '}'):
      ty = bt
      while (tk == Mul): next(); ty = ty + PTR
      if (tk != Id): print(f"{line}: bad global declaration"); sys.exit(1)
      if (memInt(id+Class)): print(f"{line}: duplicate global definition"); sys.exit(1)
      next()
      mem[id+Type] = ty
      if (tk == '('):
        mem[id+Class] = Fun
        mem[id+Val] = e + 8
        next(); i = 0
        while (tk != ')'):          
          ty = INT
          if tk == Int: next()
          elif (tk == Char): next(); ty = CHAR
          while (tk == Mul): next(); ty = ty + PTR
          if (tk != Id): print(f"{line}: bad parameter declarationn"); sys.exit(1)
          if (memInt(id+Class) == Loc): print(f"{line}: duplicate parameter definition"); sys.exit(1)
          mem[id+HClass] = memInt(id+Class); mem[id+Class] = Loc
          mem[id+HType]  = memInt(id+Type);  mem[id+Type]  = ty
          mem[id+HVal]   = memInt(id+Val);   mem[id+Val]   = i; i += 1
          next()
          if (tk == ','): next()
        next()
     
        if (tk != '{'): print(f"{line}: bad function definition"); sys.exit(1)
        loc = (i:=i+1)
        next()
        while (tk == Int or tk == Char):
          bt = INT if tk == Int else CHAR
          next()
          while (tk != ';'):
            ty = bt
            while (tk == Mul): next(); ty += PTR
            if (tk != Id): print(f"{line}: bad local declaration"); sys.exit(1)
            if (memInt(id+Class) == Loc): print(f"{line}: duplicate local definition"); sys.exit(1)
            mem[id+HClass] = memInt(id+Class); mem[id+Class] = Loc
            mem[id+HType]  = memInt(id+Type);  mem[id+Type]  = ty
            mem[id+HVal]   = memInt(id+Val);   mem[id+Val]   = (i:=i+1)
            next()
            if (tk == ','): next()
          next()
        mem[e:=e+8] = ENT
        mem[e:=e+8] = i - loc
        while (tk != '}'): stmt()
        mem[e:=e+8] = LEV
        id = sym
        while (memInt(id+Tk)):
          if (memInt(id+Class) == Loc):
            mem[id+Class] = memInt(id+HClass)
            mem[id+Type]  = memInt(id+HType)
            mem[id+Val]   = memInt(id+HVal)
          id = id + Idsz
      else:
        mem[id+Class] = Glo
        mem[id+Val]   = data
        data += 8
      if (tk == ','): next()
    next()

  if ((pc := memInt(idmain + Val)) == 0): 
    print(f"main() not defined\n"); sys.exit(1)
  if (src==1 and debug==0): 
    sys.exit(0)

  bp = sp = sp + poolsz
  stack = sp - 8
  mem[sp:=sp-8] = EXIT
  mem[sp:=sp-8] = PSH; t = sp
  mem[sp:=sp-8] = len(args)
  mem[sp:=sp-8] = data
  tmp = data + 8*len(args)
  for i in range(len(args)):
    mem[data] = tmp
    mem[tmp] = args[i]+'\0'
    data += 8
    tmp  += len(args[i])+1
  mem[sp:=sp-8] = t 
  cycle = 0
  while True:
    i = memInt(pc);  pc += 8; cycle += 1
    if (debug):
      print("{}> {:8.4s}".format(cycle,
         "LEA ,IMM ,JMP ,JSR ,BZ  ,BNZ ,ENT ,ADJ ,LEV ,LI  ,LC  ,SI  ,SC  ,PSH ,"
         "OR  ,XOR ,AND ,EQ  ,NE  ,LT  ,GT  ,LE  ,GE  ,SHL ,SHR ,ADD ,SUB ,MUL ,DIV ,MOD ,"
         "OPEN,READ,CLOS,PRTF,MALC,FREE,MSET,MCMP,EXIT,"[i*5:i*5+4]), end="")
      if (i <= ADJ): print(f" {memInt(pc)}") 
      else: print()

    if   (i == LEA): 
      a = bp + 8*memInt(pc)
      pc += 8
    elif (i == IMM): a = memInt(pc);  pc += 8
    elif (i == JMP): pc = memInt(pc)
    elif (i == JSR): mem[sp:=sp-8] = pc + 8; pc = memInt(pc)
    elif (i == BZ):           
      if (a != 0): pc += 8
      else:        pc = memInt(pc)
    elif (i == BNZ):                      
      if (a != 0): pc = memInt(pc)
      else:        pc += 8
    elif (i == ENT): mem[sp:=sp-8] = bp; bp = sp; sp = sp - memInt(pc)*8; pc += 8 
    elif (i == ADJ): sp = sp + memInt(pc)*8; pc += 8
    elif (i == LEV): sp = bp; bp = memInt(sp); sp += 8; pc = memInt(sp); sp += 8
    elif (i == LI):  a = memInt(a)
    elif (i == LC):  a = mem[a] 
    elif (i == SI):  mem[memInt(sp)] = a; sp += 8
    elif (i == SC):  mem[memInt(sp)] = chr(a); sp += 8 
    elif (i == PSH): mem[sp:=sp-8] = a
    elif (i == OR):  a = memInt(sp) |  a; sp += 8
    elif (i == XOR): a = memInt(sp) ^  a; sp += 8
    elif (i == AND): a = memInt(sp) &  a; sp += 8
    elif (i == EQ):  a = memInt(sp) == a; sp += 8
    elif (i == NE):  a = memInt(sp) != a; sp += 8
    elif (i == LT):  a = memInt(sp) <  a; sp += 8
    elif (i == GT):  a = memInt(sp) >  a; sp += 8
    elif (i == LE):  a = memInt(sp) <= a; sp += 8
    elif (i == GE):  a = memInt(sp) >= a; sp += 8
    elif (i == SHL): a = memInt(sp) << a; sp += 8
    elif (i == SHR): a = memInt(sp) >> a; sp += 8
    elif (i == ADD): a = memInt(sp) +  a; sp += 8
    elif (i == SUB): a = memInt(sp) -  a; sp += 8
    elif (i == MUL): a = memInt(sp) *  a; sp += 8
    elif (i == DIV): a = memInt(sp) /  a; sp += 8
    elif (i == MOD): a = memInt(sp) %  a; sp += 8
    elif (i == OPEN): a = fd = open(memStr(memInt(sp+8)), 'rb')
    elif (i == READ):
      lst = fd.read()
      mem[memInt(sp+8):memInt(sp+8)+len(lst)] = lst
      a = len(lst)
    elif (i == CLOS): a = fd.close()
    elif (i == PRTF): 
      t = sp + memInt(pc+8)*8-8
      fmt  = memStr(memInt(t)).replace('\\n','\n')
      fmt2 = fmtSplit(fmt)    
      para = tuple([fmtTrans(fmt2, i, t-8*(i+1)) for i in range(len(fmt2))])
      print(fmt % para, end="")
    elif (i == MALC): a = mem.malloc(memInt(sp))
    elif (i == FREE): pass
    elif (i == MSET): a = memset(memInt(sp+16), memInt(sp+8), memInt(sp))
    elif (i == MCMP): a = memcmp(memInt(sp+16), memInt(sp+8), memInt(sp))
    elif (i == GETC): 
      if keybuf == []:
        keybuf = list(input() + "\n")
      a = ord(keybuf.pop(0))
    elif (i == EXIT): print(f"exit({memInt(sp)}) cycle = {cycle}"); sys.exit(memInt(sp))
    else: print(f"unknown instruction = {i}! cycle = {cycle}"); sys.exit(1)
