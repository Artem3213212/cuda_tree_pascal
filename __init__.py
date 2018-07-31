import re

BLOCKS = ['uses', 'var', 'const', 'type']
FUNCS = ['function', 'procedure', 'constructor', 'destructor']

UNARY_SYMS = ['(',')','[',']','/','|','\\','@','#','=','>','<',':',';',',','.','$','+','-','*']
NO_UNARY_SYMS = ['>=','<=','<>',':=','..']
SPACES = ['\f','\n','\r','\t','\v',' ']
NO_NAME_SYMS = UNARY_SYMS + SPACES

def init(s):
    global i0, i1, ended, gllines, lastline
    if 0 == len(s[0]):
        if i0+1 == len(s):
            ended = True
        else:
            i0+=1
            while len(s[i0]) == 0:
                if i0+1 == len(s):
                    ended = True
                    break
                i0+=1
    gllines = s
    lastline = (False, '')

def get_next_work(s):
    global i0, i1, ended
    ml = ''
    ss = ''
    f = True
    #print(i0,i1)
    while f:
        if ml=='':
            if s[i0][i1]=='/':
                if i1+1!=len(s[i0]):
                    if s[i0][i1+1]=='/':
                        i1=len(s[i0])-1
            elif s[i0][i1]=='{':
                ml='}'
            elif s[i0][i1]=='(':
                if i1+1!=len(s[i0]):
                    if s[i0][i1+1]=='*':
                        ml=')'
                        i1+=1
                    else:
                        ss='('
                        f=False
                else:
                    ss='('
                    f=False
            else:
                if s[i0][i1] in UNARY_SYMS:
                    if i1+1!=len(s[i0]):
                        if s[i0][i1]+s[i0][i1+1] in NO_UNARY_SYMS:
                            i1+=1
                            ss=s[i0][i1:i1+1]
                        else:
                            ss=s[i0][i1]
                    else:
                        ss=s[i0][i1]
                    f=False
                elif s[i0][i1]=="'":
                    ss="'"
                    if i1+1==len(s[i0]):
                        if i0+1==len(s):
                            ended=True
                        else:
                            i0+=1
                            i1=0
                            while len(s[i0])!=0:
                                if i0+1==len(s):
                                    ended=True
                                    break
                                i0+=1
                        break
                    else:
                        i1+=1
                    while s[i0][i1]!="'":
                        ss=ss+s[i0][i1]
                        if i1+1==len(s[i0]):
                            if i0+1==len(s):
                                ended = True
                            else:
                                i0+=1
                                i1=0
                                while len(s[i0])!=0:
                                    if i0+1==len(s):
                                        ended = True
                                        break
                                    i0+=1
                            return ss+"'"
                        else:
                            i1+=1
                    ss=ss+"'"
                    f=False
                elif re.match('\\S',s[i0][i1]):
                    while not(s[i0][i1] in NO_NAME_SYMS):
                        ss=ss+s[i0][i1]
                        if i1+1==len(s[i0]):
                            if i0+1==len(s):
                                ended = True
                            else:
                                i0+=1
                                i1=0
                                while len(s[i0])==0:
                                    if i0+1==len(s):
                                        ended = True
                                        break
                                    i0+=1
                            break
                        else:
                            i1+=1
                    return ss
        elif s[i0][i1]==ml:
            if ml=='}':
                ml=''
            elif i1!=0:
                if s[i0][i1-1]=='*':
                    ml=''
        if i1+1==len(s[i0]):
            if i0+1==len(s):
                ended = True
                return ss
            else:
                i0+=1
                i1=0
            while len(s[i0])==0:
                if i0+1==len(s):
                    ended = True
                    break
                i0+=1
        else:
            i1+=1
    return ss

def get_next():
    global lastline
    if lastline[0]:
        return lastline[1]
    return get_next_work(gllines)

def read_next():
    global lastline
    lastline=(True,get_next_work(gllines))
    return lastline[1]

def remove_last():
    global lastline
    lastline=(False,'')

def set_last(s):
    global lastline
    lastline=(True,s)

def get_last(s):
    global lastline
    return lastline[1]

def isname(s):
    if s[0]in '0123456789':
        return False
    for i in s.lower():
        if not(i in '&abcdefghijklmnopqrstuvwxyz0123456789_'):
            return False
    return True

def std_block_parse(level):
    while not ended:
        s=get_next().lower()
        if s=='type':
            pass#type_block_parse(level)
        if s=='uses':
            uses_block_parse(level)

def uses_block_parse(level):
    global uses
    while not ended:
        s=get_next()
        if s==';':
            break
        elif not(s in [',','in'] or s[0]=="'"):
            uses.append(tuple([s,i0]))

def type_block_parse(level):
    global out
    update_bp = True
    while not ended:
        if update_bp:
            begin_pos = i0
        else:
            update_bp = True
        s=get_next()
        if s==';':
            continue
        #elif s in BLOCKS
        elif isname(s):
            objname=s
            ss=get_next()
            if ss==';':
                continue
            elif ss=='=':
                s=get_next()
                if s=='packed':
                    s=get_next()
                if s==';':
                    continue
                elif s=='class':
                    ss=get_next()
                    if ss!=';':
                        out.append(tuple([begin_pos,level,objname,1]))
                        class_block_parse(level+1)
                    else:
                        continue
                    #if ss in class
                elif s=='record':
                    pass
            elif ss=='<':
                ss=get_next()
                i=1
                while True:
                    if ss=='>':
                        i-=1
                    elif ss=='<':
                        i+=1
                    if i==0:
                        break
                    if ended:
                        return
                    ss=get_next()
                set_last(s)
                update_bp = False
                continue
        elif s in ['procedure','function','begin']+BLOCKS:
            set_last(s)
            break
        elif s=='class':
            ss=get_next()
            if ss=='operator':
                continue
                
def class_block_parse(level):
    pass

def get_headers(filename, lines):
    global i0, i1, uses, out, ended, out
    i0, i1 = 0, 0
    init(lines)
    out = []
    uses = []
    ended = False
    std_block_parse(1)
    if len(uses)!=0:
        yield (uses[0][1],1,'uses',0)
        i=0
        while i!=len(uses):
            if i==0:
                s=uses[0]
            else:
                if uses[i][0]=='.' and i!=len(uses)-1:
                    i+=1
                    s=(s[0]+'.'+uses[i][0],s[1])
                else:
                    yield (s[1],2,s[0],4)
                    s=uses[i]
            i+=1
        yield (s[1],2,s[0],4)
    for i in out:
        yield i
    #for i in range(5):
    #while not ended:
    #    yield (i0,1,get_next(),0)
        #print(get_next(lines))
    #return []
