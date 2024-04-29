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
    s =  mem[ptr:ptr+size].decode('utf-8')
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
  OPEN,READ,CLOS,PRTF,MALC,FREE,MSET,MCMP,EXIT ) = range(39)

( CHAR, INT, PTR ) = range(3)
( Tk, Hash, Name, Class, Type, Val, HClass, HType, HVal, Idsz ) = [i*8 for i in range(10)]

def next():
  global p, pp, lp, le, line, id, tk, data, ival

  while ((tk := source[p]) != '\0'):
    p += 1
    if (tk == '\n'):
      if (src): 
        print(f"{line}: {source[lp:p]}", end="")
        lp = p
        while (le < e):          
          le += 8
          print("    {:8.4s}".format("LEA ,IMM ,JMP ,JSR ,BZ  ,BNZ ,ENT ,ADJ ,LEV ,LI  ,LC  ,SI  ,SC  ,PSH ,"
                                 "OR  ,XOR ,AND ,EQ  ,NE  ,LT  ,GT  ,LE  ,GE  ,SHL ,SHR ,ADD ,SUB ,MUL ,DIV ,MOD ,"
                                 "OPEN,READ,CLOS,PRTF,MALC,FREE,MSET,MCMP,EXIT,"[mem[le] * 5:mem[le] * 5+4]), end="")
          if (mem[le] <= ADJ): le += 8; print(memInt(le)) 
          else: print()
      line += 1 
    elif (tk == '#'):
      while (source[p] != '\0' and source[p] != '\n'): p += 1
    elif ((tk >= 'a' and tk <= 'z') or (tk >= 'A' and tk <= 'Z') or tk == '_'):
      pp = p - 1
      tk = 0
      M = int(1e9 + 7)
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
      if ((ival := int(tk))):
        while (source[p] >= '0' and source[p] <= '9'): ival = ival * 10 + int(source[p]); p += 1
      elif (source[p] == 'x' or source[p] == 'X'):
        p += 1
        while ((tk := source[p]) and 
               ((tk >= '0' and tk <= '9') or 
                (tk >= 'a' and tk <= 'f') or 
                (tk >= 'A' and tk <= 'F'))):
          ival = ival * 16 + (tk & 15) + (9 if tk >= 'A' else 0)
          p += 1
      else:
        while (source[p] >= '0' and source[p] <= '7'): ival = ival * 8 + source[p] - '0'; p += 1
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
        if ((ival := source[p]) == '\\'): 
          p += 1
          if ((ival := source[p]) == 'n'): 
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
      if (source[p] == '='):   p += 1; tk = Ge
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
  elif (tk == Num): e += 8*1; mem[e] = IMM; e += 8*1; mem[e] = ival; next(); ty = INT
  elif (tk == '"'):
    e += 8*1; mem[e] = IMM; e += 8*1; mem[e] = ival
    next()
    while (tk == '"'): next()
    data = (data + 8*1) & (-8*1); ty = PTR
  elif (tk == Sizeof):
    next()
    if (tk == '('): next()
    else: print(f"{line}: open paren expected in sizeof"); exit(-1)
    ty = INT
    if (tk == Int): next()
    elif (tk == Char): next(); ty = CHAR
    while (tk == Mul): next(); ty = ty + PTR
    if (tk == ')'): next()
    else: print(f"{line}: close paren expected in sizeof"); exit(-1)
    e += 8*1; mem[e] = IMM; e += 8*1; mem[e] = 1  if (ty == CHAR) else 8
    ty = INT
  elif (tk == Id):
    d = id; next()
    if (tk == '('):
      next()
      t = 0
      while (tk != ')'): 
        expr(Assign); e += 8*1; mem[e] = PSH; t += 1
        if (tk == ','): next()
      next()
      if (memInt(d+Class) == Sys):        
        e += 8*1; mem[e] = memInt(d+Val)
      elif (memInt(d+Class) == Fun):         
        e += 8*1; mem[e] = JSR; e += 8*1; mem[e] = memInt(d+Val)
      else: print(f"{line}: bad function call"); exit(-1)
      if (t):         
        e += 8*1; mem[e] = ADJ; e += 8*1; mem[e] = t
      ty = memInt(d+Type)
    elif (memInt(d+Class) == Num):
      e += 8*1; mem[e] = IMM; e += 8*1; mem[e] = memInt(d+Val); ty = INT
    else:
      if (memInt(d+Class) == Loc):e += 8*1; mem[e] = LEA; e += 8*1; mem[e] = loc - memInt(d+Val)
      elif (memInt(d+Class) == Glo): e += 8*1; mem[e] = IMM; e += 8*1; mem[e] = memInt(d+Val)
      else: print(f"{line}: undefined variable"); exit(-1)
      e += 8*1; mem[e] = LC if ((ty := memInt(d+Type)) == CHAR) else LI 
  elif (tk == '('):
    next()
    if (tk == Int or tk == Char):
      t = INT if tk == Int else CHAR; next()
      while (tk == Mul): next(); t = t + PTR
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
    if (ty > INT): ty = ty - PTR 
    else: print(f"{line}: bad dereference"); exit(-1)
    e += 8*1; mem[e] = LC if (ty == CHAR) else LI
  elif (tk == And):
    next(); expr(Inc)
    if (mem[e] == LC or mem[e] == LI): e -= 8 
    else: print(f"{line}: bad address-of"); exit(-1)
    ty = ty + PTR
  elif (tk == '!'): next(); expr(Inc); e += 8*1; mem[e] = PSH; e += 8*1; mem[e] = IMM; e += 8*1; mem[e] = 0; e += 8*1; mem[e] = EQ; ty = INT
  elif (tk == '~'): next(); expr(Inc); e += 8*1; mem[e] = PSH; e += 8*1; mem[e] = IMM; e += 8*1; mem[e] = -1; e += 8*1; mem[e] = XOR; ty = INT
  elif (tk == Add): next(); expr(Inc); ty = INT
  elif (tk == Sub):
    next(); e += 8*1; mem[e] = IMM
    if (tk == Num): e += 8*1; mem[e] = -ival; next() 
    else: e += 8*1; mem[e] = -1; e += 8*1; mem[e] = PSH; expr(Inc); e += 8*1; mem[e] = MUL
    ty = INT
  elif (tk == Inc or tk == Dec):
    t = tk; next(); expr(Inc)
    if (mem[e] == LC): mem[e] = PSH; e += 8*1; mem[e] = LC
    elif (mem[e] == LI): mem[e] = PSH; e += 8*1; mem[e] = LI
    else: print(f"{line}: bad lvalue in pre-increment"); exit(-1)
    e += 8*1; mem[e] = PSH
    e += 8*1; mem[e] = IMM; e += 8*1; mem[e] = 8 if (ty > PTR) else 1
    e += 8*1; mem[e] = ADD if (t == Inc)   else SUB
    e += 8*1; mem[e] = SC  if (ty == CHAR) else SI
  else: print(f"{line}: bad expression"); exit(-1)

  while (tk if isinstance(tk, int) else ord(tk))  >= lev:
    t = ty
    if (tk == Assign):
      next()
      if (mem[e] == LC or mem[e] == LI): mem[e] = PSH 
      else: print(f"{line}: bad lvalue in assignment"); exit(-1)
      expr(Assign); e += 8*1; mem[e] = SC if ((ty := t) == CHAR) else SI
    elif (tk == Cond):
      next()
      e += 8*1; mem[e] = BZ; e += 8*1; d = e
      expr(Assign)
      if (tk == ':'): next() 
      else: print(f"{line}: conditional missing colon"); exit(-1)
      mem[d] = e + 8*3; e += 8*1; mem[e] = JMP; e += 8*1; d = e
      expr(Cond)
      mem[d] = e + 8*1
    elif (tk == Lor): next(); e += 8*1; mem[e] = BNZ; e += 8*1; d = e; expr(Lan); mem[d] = e + 8*1; ty = INT
    elif (tk == Lan): next(); e += 8*1; mem[e] = BZ;  e += 8*1; d = e; expr(Or);  mem[d] = e + 8*1; ty = INT
    elif (tk == Or) : next(); e += 8*1; mem[e] = PSH; expr(Xor); e += 8*1; mem[e] = OR;  ty = INT
    elif (tk == Xor): next(); e += 8*1; mem[e] = PSH; expr(And); e += 8*1; mem[e] = XOR; ty = INT
    elif (tk == And): next(); e += 8*1; mem[e] = PSH; expr(Eq);  e += 8*1; mem[e] = AND; ty = INT
    elif (tk == Eq):  next(); e += 8*1; mem[e] = PSH; expr(Lt);  e += 8*1; mem[e] = EQ;  ty = INT
    elif (tk == Ne):  next(); e += 8*1; mem[e] = PSH; expr(Lt);  e += 8*1; mem[e] = NE;  ty = INT
    elif (tk == Lt):  next(); e += 8*1; mem[e] = PSH; expr(Shl); e += 8*1; mem[e] = LT;  ty = INT
    elif (tk == Gt):  next(); e += 8*1; mem[e] = PSH; expr(Shl); e += 8*1; mem[e] = GT;  ty = INT
    elif (tk == Le):  next(); e += 8*1; mem[e] = PSH; expr(Shl); e += 8*1; mem[e] = LE;  ty = INT
    elif (tk == Ge):  next(); e += 8*1; mem[e] = PSH; expr(Shl); e += 8*1; mem[e] = GE;  ty = INT
    elif (tk == Shl): next(); e += 8*1; mem[e] = PSH; expr(Add); e += 8*1; mem[e] = SHL; ty = INT
    elif (tk == Shr): next(); e += 8*1; mem[e] = PSH; expr(Add); e += 8*1; mem[e] = SHR; ty = INT
    elif (tk == Add):
      next(); e += 8*1; mem[e] = PSH; expr(Mul)
      if ((ty := t) > PTR): e += 8*1; mem[e] = PSH; e += 8*1; mem[e] = IMM; e += 8*1; mem[e] = 8; e += 8*1; mem[e] = MUL
      e += 8*1; mem[e] = ADD
    elif (tk == Sub):
      next(); e += 8*1; mem[e] = PSH; expr(Mul)
      if (t > PTR and t == ty): e += 8*1; mem[e] = SUB; e += 8*1; mem[e] = PSH; e += 8*1; mem[e] = IMM; e += 8*1; mem[e] = 8; e += 8*1; mem[e] = DIV; ty = INT
      elif ((ty := t) > PTR): e += 8*1; mem[e] = PSH; e += 8*1; mem[e] = IMM; e += 8*1; mem[e] = 8; e += 8*1; mem[e] = MUL; e += 8*1; mem[e] = SUB
      else: e += 8*1; mem[e] = SUB
    elif (tk == Mul): next(); e += 8*1; mem[e] = PSH; expr(Inc); e += 8*1; mem[e] = MUL; ty = INT
    elif (tk == Div): next(); e += 8*1; mem[e] = PSH; expr(Inc); e += 8*1; mem[e] = DIV; ty = INT
    elif (tk == Mod): next(); e += 8*1; mem[e] = PSH; expr(Inc); e += 8*1; mem[e] = MOD; ty = INT
    elif (tk == Inc or tk == Dec):
      if (mem[e] == LC): mem[e] = PSH; e += 8*1; mem[e] = LC
      elif (mem[e] == LI): mem[e] = PSH; e += 8*1; mem[e] = LI
      else: print(f"{line}: bad lvalue in post-increment"); exit(-1)
      e += 8*1; mem[e] = PSH; e += 8*1; mem[e] = IMM; e += 8*1; mem[e] = 8 if (ty > PTR) else 1
      e += 8*1; mem[e] = ADD if(tk == Inc) else SUB
      e += 8*1; mem[e] = SC if (ty == CHAR) else SI
      e += 8*1; mem[e] = PSH; e += 8*1; mem[e] = IMM; e += 8*1; mem[e] = 8 if (ty > PTR) else 1
      e += 8*1; mem[e] = SUB if (tk == Inc) else ADD
      next()
    elif (tk == Brak):
      next(); e += 8*1; mem[e] = PSH; expr(Assign)
      if (tk == ']'): next()
      else: print(f"{line}: close bracket expected"); exit(-1)
      if (t > PTR): e += 8*1; mem[e] = PSH; e += 8*1; mem[e] = IMM; e += 8*1; mem[e] = 8; e += 8*1; mem[e] = MUL
      elif (t < PTR): print(f"{line}: pointer type expected"); exit(-1)
      e += 8*1; mem[e] = ADD
      e += 8*1; mem[e] = LC if ((ty := t - PTR) == CHAR) else LI
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
    e += 8*1; mem[e] = BZ;  e += 8*1; b = e
    stmt()
    if (tk == Else):
      mem[b] = (int)(e + 8*3); e += 8*1; mem[e] = JMP;  e += 8*1; b = e
      next()
      stmt()
    mem[b] = (int)(e + 8*1)
  elif (tk == While):
    next()
    a = e + 8*1
    if (tk == '('): next() 
    else: print(f"{line}: open paren expected"); exit(-1)
    expr(Assign)
    if (tk == ')'): next() 
    else: print(f"{line}: close paren expected"); exit(-1)
    e += 8*1; mem[e] = BZ;  e += 8*1; b = e
    stmt()
    e += 8*1; mem[e] = JMP; e += 8*1; mem[e] = a
    mem[b] = (int)(e + 8*1)
  elif (tk == Return):
    next()
    if (tk != ';'): expr(Assign)
    e += 8*1; mem[e] = LEV
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
  fd = fd2 = 0
  
  args = sys.argv[1:]
  if len(args)> 0 and args[0] == '-s': 
   src = 1; args = args[1:]
  if len(args)> 0 and args[0] == '-d': 
    debug = 1; args = args[1:]
  if len(args) < 1:
    print(f"usage: python c4py.py [-s] [-d] file ...\n")
    sys.exit(1)

  sym = mem.malloc(poolsz)
  if ((e    := mem.malloc(poolsz)) == 0): print(f"could not malloc({poolsz}) text area\n"); exit(-1)
  if ((data := mem.malloc(poolsz)) == 0): print(f"could not malloc({poolsz}) data area\n"); exit(-1)
  if ((sp   := mem.malloc(poolsz)) == 0): print(f"could not malloc({poolsz}) stack area\n"); exit(-1)
  le = e
  
  source = "char else enum if int return sizeof while open read close printf malloc free memset memcmp exit void main"
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
        mem[id+Val] = e + 8*1
        next(); i = 0
        while (tk != ')'):          
          ty = INT
          if tk == Int: next()
          elif (tk == Char): next(); ty = CHAR
          while (tk == Mul): next(); ty = ty + PTR
          if (tk != Id): print(f"{line}: bad parameter declarationn"); sys.exit(1)
          if (memInt(id+Class) == Loc): print(f"{line}: duplicate parameter definition"); sys.exit(1)
          mem[id+HClass] = memInt(id+Class); mem[id+Class] = Loc
          mem[id+HType]  = memInt(id+Type);  mem[id+Type] = ty
          mem[id+HVal]   = memInt(id+Val);   mem[id+Val] = i; i += 1
          next()
          if (tk == ','): next()
        next()
     
        if (tk != '{'): print(f"{line}: bad function definition"); sys.exit(1)
        i += 1
        loc = i
        next()
        while (tk == Int or tk == Char):
          bt = INT if tk == Int else CHAR
          next()
          while (tk != ';'):
            ty = bt
            while (tk == Mul): next(); ty = ty + PTR
            if (tk != Id): print(f"{line}: bad local declaration tk={tk}!=Id{Id}"); sys.exit(1)
            if (memInt(id+Class) == Loc): print(f"{line}: duplicate local definition"); sys.exit(1)
            mem[id+HClass] = memInt(id+Class); mem[id+Class] = Loc
            mem[id+HType]  = memInt(id+Type);  mem[id+Type] = ty
            mem[id+HVal]   = memInt(id+Val);   i += 1; mem[id+Val] = i
            next()
            if (tk == ','): next()
          next()
        e += 8*1
        mem[e] = ENT
        e += 8*1
        mem[e] = i - loc
        while (tk != '}'): stmt()
        e += 8*1
        mem[e] = LEV
        id = sym
        while (memInt(id+Tk)):
          if (memInt(id+Class) == Loc):
            mem[id+Class] = memInt(id+HClass)
            mem[id+Type] = memInt(id+HType)
            mem[id+Val] = memInt(id+HVal)
          id = id + Idsz
      else:
        mem[id+Class] = Glo
        mem[id+Val] = data
        data = data + 8
      if (tk == ','): next()
    next()

  if ((pc := memInt(idmain + Val)) == 0): 
    print(f"main() not defined\n"); sys.exit(1)
  if (src==1 and debug==0): 
    sys.exit(0)

  bp = sp = sp + poolsz
  stack = sp - 8
  sp -= 8*1; mem[sp] = EXIT
  sp -= 8*1; mem[sp] = PSH; t = sp
  sp -= 8*1; mem[sp] = len(args)
  sp -= 8*1; mem[sp] = data
  tmp = data + 8*len(args)
  for ii in range(len(args)):
    mem[data] = tmp
    mem[tmp] = args[ii]+'\0'
    data += 8*1
    tmp  += len(args[ii])+1
  sp -= 8*1; mem[sp] = t 
  cycle = 0
  while True:
    i = memInt(pc);  pc += 8*1; cycle += 1
    if (debug):
      print("{}> {:8.4s}".format(cycle,
         "LEA ,IMM ,JMP ,JSR ,BZ  ,BNZ ,ENT ,ADJ ,LEV ,LI  ,LC  ,SI  ,SC  ,PSH ,"
         "OR  ,XOR ,AND ,EQ  ,NE  ,LT  ,GT  ,LE  ,GE  ,SHL ,SHR ,ADD ,SUB ,MUL ,DIV ,MOD ,"
         "OPEN,READ,CLOS,PRTF,MALC,FREE,MSET,MCMP,EXIT,"[i*5:i*5+4]), end="")
      if (i <= ADJ): print(f" {memInt(pc)}") 
      else: print()

    if   (i == LEA): 
      a = bp + 8*memInt(pc)
      pc += 8*1
    elif (i == IMM): a = memInt(pc);  pc += 8*1
    elif (i == JMP): pc = memInt(pc)
    elif (i == JSR): sp -= 8*1; mem[sp] = pc + 8*1; pc = memInt(pc)
    elif (i == BZ):           
      if (a != 0): pc += 8*1
      else:        pc = memInt(pc)
    elif (i == BNZ):                      
      if (a != 0): pc = memInt(pc)
      else:        pc += 8*1
    elif (i == ENT): sp -= 8*1; mem[sp] = bp; bp = sp; sp = sp - memInt(pc)*8*1; pc += 8*1 
    elif (i == ADJ): sp = sp + memInt(pc)*8*1;  pc += 8*1
    elif (i == LEV): sp = bp; bp = memInt(sp); sp += 8*1; pc = memInt(sp); sp += 8*1
    elif (i == LI):
      tmp = a
      a = memInt(a)
    elif (i == LC):
      tmp = a
      a = mem[a] 
    elif (i == SI):
      mem[memInt(sp)] = a   
      sp += 8*1
    elif (i == SC):
       mem[memInt(sp)] = chr(a)
       sp += 8*1 
    elif (i == PSH): 
      sp -= 8*1; mem[sp] = a

    elif (i == OR):  a = memInt(sp) |  a; sp += 8*1
    elif (i == XOR): a = memInt(sp) ^  a; sp += 8*1
    elif (i == AND): a = memInt(sp) &  a; sp += 8*1
    elif (i == EQ):  a = memInt(sp) == a; sp += 8*1
    elif (i == NE):  a = memInt(sp) != a; sp += 8*1
    elif (i == LT):  a = memInt(sp) <  a; sp += 8*1
    elif (i == GT):  a = memInt(sp) >  a; sp += 8*1
    elif (i == LE):  a = memInt(sp) <= a; sp += 8*1
    elif (i == GE):  a = memInt(sp) >= a; sp += 8*1
    elif (i == SHL): a = memInt(sp) << a; sp += 8*1
    elif (i == SHR): a = memInt(sp) >> a; sp += 8*1
    elif (i == ADD): 
      tmp = a
      a = memInt(sp) + a
      sp += 8*1
    elif (i == SUB): a = memInt(sp) -  a; sp += 8*1
    elif (i == MUL): a = memInt(sp) *  a; sp += 8*1
    elif (i == DIV): a = memInt(sp) /  a; sp += 8*1
    elif (i == MOD): a = memInt(sp) %  a; sp += 8*1

    elif (i == OPEN): 
      fd = open(memStr(memInt(sp+8*1)), 'rb')
      a = fd
    elif (i == READ):
      lst = fd.read()
      mem[memInt(sp+8*1):memInt(sp+8*1)+len(lst)] = lst
      a = len(lst)
    elif (i == CLOS): 
      fd.close()
      a = 1
    elif (i == PRTF): 
      t = sp + memInt(pc+8*1)*8*1-8
      fmt  = memStr(memInt(t)).replace('\\n','\n')
      fmt2 = fmtSplit(fmt)    
      para = tuple([fmtTrans(fmt2, i, t-8*(i+1)) for i in range(len(fmt2))])
      print(fmt % para, end="")
    elif (i == MALC): a = mem.malloc(memInt(sp))
    elif (i == FREE): pass
    elif (i == MSET): a = memset(memInt(sp+8*2), memInt(sp+8*1), memInt(sp))
    elif (i == MCMP): a = memcmp(memInt(sp+8*2), memInt(sp+8*1), memInt(sp))
    elif (i == EXIT): print(f"exit({memInt(sp)}) cycle = {cycle}"); sys.exit(memInt(sp))
    else: print(f"unknown instruction = {i}! cycle = {cycle}"); sys.exit(1)
