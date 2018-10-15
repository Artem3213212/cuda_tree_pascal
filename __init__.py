if __name__=="__main__":
    from pascal_tokenizer import *
else:
    from .pascal_tokenizer import *

BLOCKS=['uses','var','const','type']
FUNCS=['function','procedure','constructor','destructor','operator']
ACCESS_CONTROL=['private','protected','public','published']
FUNCTIONS_DIRECTIVES=['reintroduce','overload','virtual','override','abstract','dynamic','inline','assembler','forward','interface']
ICON_USES = 0
ICON_USES_IN = 4
ICON_CLASS = 1
ICON_RECORD = 1
ICON_TYPE_IN = 1
ICON_PROPERTY = 6
ICON_INTERFACE = 1
ICON_VAR = 2
ICON_VAR_IN = 7
ICON_CONST_IN = 7
ICON_FUNC = 5
NODE_VARS = 'var/const'
NODE_ANON = 'anonym'

def get():
    global ended, line
    if not ended:
        s = tokenizer.pop()
    else:
        s = ('',(line[1],line[0]),(line[3],line[2]),ended)
    ended = s[3]
    if s[0]=='object':
        s = ('class',s[1],s[2],s[3])
    line = (s[1][1],s[1][0],s[2][1],s[2][0])
    return s[0]

def restore(s):
    s = tokenizer.push((s,(line[1],line[0]),(line[3],line[2]),ended))

def std_block_parse(var_at_begin=False,LowStop=False):
    if var_at_begin:
        vars = var_block_parse()
    else:
        vars = []
    TO_SKIP = ['class','implementation','interface']
    z=[]
    funcreg=[]
    while not ended:
        s = get().lower()
        begin_pos = line
        if s in TO_SKIP:
            continue
        if s == '[':
            while not ended and get()!=']':
                pass
        elif s.lower() == 'uses':
            uses_block_parse()
        elif s.lower() == 'type':
            z+=type_block_parse()
        elif s.lower() in ['const','resourcestring']:
            vars+=const_block_parse()
        elif s.lower() in ['var']+ACCESS_CONTROL:
            vars+=var_block_parse()
        elif s.lower() in FUNCS:
            vars.append(False)
            z+=function_parse(begin_pos,funcreg)
        elif s.lower() == 'property':
            z+=property_parse()
        elif s.lower() == 'begin':
            i=len(z)
            z+=begin_block_parse()
            if not ended:
                ii=len(vars)
                v=[]
                while not ended and ii!=0:
                    ii-=1
                    if not vars[ii]:
                        vars,v=vars[:ii],vars[ii+1:]
                        if v!=[]:
                            v=[(v[0][0],NODE_VARS,ICON_VAR,v)]
                        break
                while  not ended and i!=0:
                    i-=1
                    if len(z[i])==5:
                        z, z0, z1 = z[:i], z[i], z[i+1:]
                        z.append((z0[0],z0[1],z0[2],v+z0[3]+z1))
                        break
            if len(z)==1 and LowStop:
                break
        elif s.lower() == 'end':
            while not ended and not get() in [';','.']:
                pass
            break
        elif s.lower() in ['initialization','finalization']:
            z+=begin_block_parse()
            break
    v = []
    for i in vars:
        if i:
            v.append(i)
    if v:
        return [(v[0][0],NODE_VARS,ICON_VAR,v)]+z#(current_begin,'block',0,z)#(current_begin,'name',icon,z)
    else:
        return z

def begin_block_parse():
    global ended, line
    z = []
    i = 0
    s = 'begin'
    while not ended:
        if s.lower() in FUNCS:
            l = line
            ss = (get(), get())
            restore(ss[1])
            ended = False
            restore(ss[0])
            if '.' != ss[1]:
                restore(NODE_ANON)
            line = l
            restore(s)
            if '.' == ss[1]:
                break
            else:
                z+=std_block_parse(LowStop=True)
        if s.lower() in ['begin','case','try','asm']:
            i+=1
        if s.lower() == 'end':
            i-=1
            if i == 0:
                #s = get()
                break
        s = get()
    return z

def function_parse(begin_pos,funcreg):
    def post_clear():
        while not ended:
            s = get()
            if s.lower() in FUNCTIONS_DIRECTIVES:
                while not ended and get()!=';':
                    pass
            else:
                restore(s)
                break
    s=''
    ss=''
    while not ended:
        ss = get()
        if ss in ['(',':',';','begin']+FUNCS+BLOCKS:
            break
        s=s+ss
    if ss == '(':
        while not ended and not get()==')':
            pass
        ss = get()
    if ss == ':':
        while not ended and not get()==';':
            pass
    if ss in ['begin']+FUNCS+BLOCKS:
        restore(ss)
        post_clear()
        return [(begin_pos,s,ICON_FUNC,[],-1)]
    f = True
    for i in funcreg:
        if i==s:
            f = False
            break
    if f:
        funcreg.append(s)
    post_clear()
    return [(begin_pos,s,ICON_FUNC,[],-1)]

def property_parse():
    begin_pos = line
    name = get()
    i = 0
    s = ''
    while not ended and(i!=0 or s!=';'):
        s = get()
        if s == '[':
            i+=1
        if s == ']':
            i-=1
    return [(begin_pos,name,ICON_PROPERTY,[])]

def uses_block_parse():
    global uses
    while not ended:
        s = get()
        if s==';':
            break
        elif not (s.lower() in [',','in'] or is_string(s)):
            uses.append((s,line))

def var_block_parse():
    z=[]
    while not ended:
        s = get()
        current_begin = line
        if s.lower() in ['class','begin','end','implementation','interface','initialization','finalization','property']+ACCESS_CONTROL+FUNCS+BLOCKS:
            restore(s)
            break
        elif not ended:
            s=[s]
            ss=''
            while not ended and ss!=":":
                ss = get()
                if ss not in [',',':']:
                    s.append(ss)
            i=0
            f=True
            while not ended:
                ss=get()
                if ss.lower()=='packed':
                    ss=get()
                if ss.lower()=='specialize':
                    ss=get()
                if ss.lower()=='record':
                    temp = std_block_parse(var_at_begin=True)
                    for ii in s:
                        z.append((current_begin,ii,ICON_VAR_IN,temp))
                    f=False
                    break
                if ss.lower()=='class':
                    ss=get()
                    if ss.lower()=='of':
                        while not ended and get()!=';':
                            pass
                        for ii in s:
                            z.append((current_begin,ii,ICON_CLASS,[]))
                        f=False
                        break
                    elif ss!=';':
                        restore(ss)
                        temp = class_block_parse()
                        for ii in s:
                            z.append((current_begin,ii,ICON_CLASS,temp))
                        f=False
                        break
                    else:
                        continue
                if ss=='(':
                    i+=1
                elif ss==')':
                    i-=1
                elif ss==';' and i<=0:
                    break
            if f:
                for ii in s:
                    z.append((current_begin,ii,ICON_VAR_IN,[]))
    return z

def const_block_parse():
    z=[]
    while not ended:
        s = get()
        current_begin = line
        if s.lower() in ['class','begin','end','implementation','interface','initialization','finalization','property']+ACCESS_CONTROL+FUNCS+BLOCKS:
            restore(s)
            break
        elif not ended:
            i=0
            while not ended:
                ss=get()
                if ss=='(':
                    i+=1
                elif ss==')':
                    i-=1
                elif ss==';' and i<=0:
                    break
            z.append((current_begin,s,ICON_CONST_IN,[]))
    return z

def type_block_parse():
    z = []
    update_bp = True
    while not ended:
        s = get()
        if update_bp:
            begin_pos = line
        else:
            update_bp = True
        if s==';':
            continue
        elif s.lower()=='generic':
            update_bp = False
            continue
        elif s.lower() in ['procedure','function','begin','implementation','interface','initialization','finalization','property']+BLOCKS:
            tokenizer.push((s,(line[1],line[0]),(line[3],line[2]),ended))
            break
        elif s.lower()=='class':
            ss=get()
            if ss.lower()=='operator':
                continue
        elif is_name(s):
            objname=s
            ss=get()
            if ss==';':
                continue
            elif ss=='=':
                s=get()
                if s.lower()=='packed':
                    s=get()
                if s.lower()=='specialize':
                    s=get()
                if s==';':
                    continue
                elif s.lower()=='class':
                    ss=get()
                    if ss=='of':
                        while not ended and get()!=';':
                            pass
                        z.append((begin_pos,objname,ICON_CLASS,[]))
                    elif ss!=';':
                        restore(ss)
                        z.append((begin_pos,objname,ICON_CLASS,class_block_parse()))
                    else:
                        continue
                elif s.lower()=='record':
                    z.append((begin_pos,objname,ICON_RECORD,std_block_parse(var_at_begin=True)))
                elif s.lower()=='interface':
                    z.append((begin_pos,objname,ICON_INTERFACE,interface_block_parse()))
                else:
                    z.append((begin_pos,objname,ICON_TYPE_IN,[]))
                    if s=='(':
                        i=1
                    else:
                        i=0
                    while not ended and(s!=';' or i!=0):
                        s = get()
                        if s=='(':
                            i+=1
                        elif s==')':
                            i-=1
                    continue
            elif ss=='<':
                ss=get()
                i=1
                while not ended:
                    if ss=='>':
                        i-=1
                    if ss=='>=':
                        restore('=')
                        break
                    elif ss=='<':
                        i+=1
                    if i==0:
                        break
                    if ended:
                        return
                    ss=get()
                restore(s)
                update_bp=False
                continue
    return z

def interface_block_parse():
    z=[]
    s = get()
    if ended:
        return []
    if s=='(':
        while not ended and get()!=')':
            pass
        s = get()
        if ended:
            return []
    if s=='[':
        while not ended and get()!=']':
            pass
        s = get()
    if s == ';' or ended:
        return z
    restore(s)
    z=z+std_block_parse()
    return z

def class_block_parse():
    z=[]
    s = get()
    if ended:
        return []
    if s.lower() in ['absract','sealed']:
        s=get()
    if s=='(':
        while not ended and get()!=')':
            pass
        s = get()
    if s == ';':
        return z
    restore(s)
    z=z+std_block_parse(var_at_begin=True)
    return z

def main_table_print(data):
    global currpos, main_data
    main_data=data
    for currpos in range(len(data)):
        if len(data[currpos])==2:
            continue
        if len(data[currpos])==5:
            f=True
            for ii in range(len(main_data)-1,currpos,-1):
                if main_data[ii][1]==data[currpos][1]:
                    yield (main_data[ii][0],1,data[currpos][1],data[currpos][2])
                    yield from table_print(2,' ',main_data[ii][3])
                    main_data[ii]=[0,0]
                    f=False
                    break
            if f:
                yield (data[currpos][0],1,data[currpos][1],data[currpos][2])
                yield from table_print(2,data[currpos][1],data[currpos][3])
            continue
        yield (data[currpos][0],1,data[currpos][1],data[currpos][2])
        yield from table_print(2,data[currpos][1],data[currpos][3])

def table_print(level, name, data):
    for i in data:
        if len(i)==5:
            f=True
            for ii in range(len(main_data)-1,currpos,-1):
                if main_data[ii][1]==name+'.'+i[1]:
                    yield (main_data[ii][0],level,i[1],i[2])
                    yield from table_print(level+1,' ',main_data[ii][3])
                    main_data[ii]=[0,0]
                    f=False
                    break
            if f:
                yield (i[0],level,i[1],i[2])
                yield from table_print(level+1,i[1],i[3])
            continue
        yield (i[0],level,i[1],i[2])
        yield from table_print(level+1,name+'.'+i[1],i[3])

def get_headers(filename, lines):
    global uses, tokenizer, ended, line
    out, uses = [], []
    ended, line = False, 0
    tokenizer = PasTokenizerParallelStack(lines, False)
    main_data = std_block_parse()
    tokenizer.stop()
    if uses:
        yield (uses[0][1],1,'uses',ICON_USES)
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
        yield (s[1],2,s[0],ICON_USES_IN)
    yield from main_table_print(main_data)

if __name__=="__main__":
    import os
    for file in ['jsonscanner.pp']:#os.listdir("tests"):
        if file.endswith(".pp") or file.endswith(".pas"):
            print()
            print('test',file)
            #ss=open(os.path.join("tests",file),encoding='utf-8').read().split('\n')
            ss=open('W:\\AGEngineAplha0.1.4\\Sources\\lib\\AG.Graphic.pas').read().split('\n')[259:]
            for i in get_headers('',ss):
                print(i)
            break