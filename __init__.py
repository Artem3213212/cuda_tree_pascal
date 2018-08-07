if __name__=="__main__":
    from pascal_tokenizer import *
else:
    from .pascal_tokenizer import *

BLOCKS=['uses','var','const','type']
FUNCS=['function','procedure','constructor','destructor','operator']
ACCESS_CONTROL=['private','protected','public','published']
FUNCTIONS_DIRECTIVES=['reintroduce','overload','virtual','override','abstract','dynamic','inline','assembler','forward','interface']

def get():
    global ended, line
    s = tokenizer.pop()
    ended = s[3]
    line = s[1][0]
    return s[0]

def restore(s):
    s = tokenizer.push([s,[line],[],ended])

def std_block_parse(var_at_begin=False):
    def clear_vars(v):
        for i in v:
            if i:
                yield i
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
            z+=begin_block_parse()
            if not ended:
                ii=len(vars)
                v=[]
                while ii!=0:
                    ii-=1
                    if not vars[ii]:
                        vars,v=vars[:ii],vars[ii+1:]
                        if v!=[]:
                            v=[(v[0][0],'var&const',2,v)]
                        break
                i=len(z)
                while i!=0:
                    i-=1
                    if len(z[i])==5:
                        z, z0, z1 = z[:i], z[i], z[i+1:]
                        z.append(tuple([z0[0],z0[1],z0[2],v+z0[3]+z1]))
                        break
        elif s.lower() == 'end':
            while ended and not get() in [';','.']:
                pass
            break
        elif s.lower() in ['initialization','finalization']:
            z+=begin_block_parse()
            break
    if vars:
        return [(vars[0][0],'var&const',2,clear_vars(vars))]+z#(current_begin,'block',0,z)#(current_begin,'name',icon,z)
    else:
        return z

def begin_block_parse():
    global ended
    i = 0
    s = 'begin'
    while not ended:
        if s.lower() in ['begin','case']:
            i+=1
        if s.lower() == 'end':
            i-=1
            if i == 0:
                s = get()
                break
        s = get()
    while not ended and not s in [';','.']:
        s = get()
    ended = ended or s=='.'
    return []

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
        if ss in ['(',':',';']:
            break
        s=s+ss
    if ss == '(':
        while not ended and not get()==')':
            pass
        ss = get()
    if ss == ':':
        while not ended and not get()==';':
            pass
    f = True
    for i in funcreg:
        if i==s:
            f = False
            break
    if f:
        funcreg.append(s)
    post_clear()
    return [(begin_pos,s,5,[],-1)]

def property_parse():
    begin_pos = line
    name = get()
    i = 0
    s = ''
    while i!=0 or s!=';':
        s = get()
        if s == '[':
            i+=1
        if s == ']':
            i-=1
    return [(begin_pos,name,6,[])]

def uses_block_parse():
    global uses
    while not ended:
        s = get()
        if s==';':
            break
        elif not (s.lower() in [',','in'] or is_string(s)):
            uses.append(tuple([s,line]))

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
            while not ended:
                ss=get()
                if ss.lower()=='packed':
                    ss=get()
                if ss.lower()=='specialize':
                    ss=get()
                if ss.lower()=='record':
                    temp = std_block_parse()
                    for ii in s:
                        z.append(tuple([current_begin,ii,7,temp]))
                if ss.lower()=='class':
                    ss=get()
                    if ss.lower()=='of':
                        while get()!=';':
                            pass
                        for ii in s:
                            z.append(tuple([current_begin,ii,1,[]]))
                    elif ss!=';':
                        restore(ss)
                        temp = class_block_parse()
                        for ii in s:
                            z.append(tuple([current_begin,ii,1,temp]))
                    else:
                        continue
                if ss=='(':
                    i+=1
                elif ss==')':
                    i-=1
                elif ss==';' and i<=0:
                    break
            for ii in s:
                z.append(tuple([current_begin,ii,7,[]]))
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
            z.append(tuple([current_begin,s,7,[]]))
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
            s = get()
        elif s.lower() in ['procedure','function','begin','implementation','interface','initialization','finalization','property']+BLOCKS:
            tokenizer.push([s,[line],[],ended])
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
                        while get()!=';':
                            pass
                        z.append(tuple([begin_pos,objname,1,[]]))
                    elif ss!=';':
                        #out.append(tuple([begin_pos,level,objname,1]))
                        restore(ss)
                        z.append(tuple([begin_pos,objname,1,class_block_parse()]))
                    else:
                        continue
                elif s.lower()=='record':
                    z.append(tuple([begin_pos,objname,1,std_block_parse()]))
                elif s.lower()=='interface':
                    z.append(tuple([begin_pos,objname,1,interface_block_parse()]))
                elif is_name(s):
                    z.append(tuple([begin_pos,objname,1,[]]))
                    i=0
                    while s!=';' or i!=0:
                        s = get()
                        if s=='(':
                            i+=1
                        elif s==')':
                            i-=1
                    continue
            elif ss=='<':
                ss=get()
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
                    ss=get()
                set_last(s)
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
    z=z+std_block_parse()
    return z

def table_print(level, data):
    for i in data:
        yield (i[0],level,i[1],i[2])
        yield from table_print(level+1,i[3])

def get_headers(filename, lines):
    global uses, out, tokenizer, ended, line
    out, uses = [], []
    ended, line = False, 0
    tokenizer = PasTokenizerStack(lines, False)
    main_data=std_block_parse()
    #tokenizer.stop()
    if uses:
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
    yield from table_print(1,main_data)
    for i in out:
        yield i

if __name__=="__main__":
    import os
    for file in ['mytest.pp']:#os.listdir("tests"):
        if file.endswith(".pp") or file.endswith(".pas"):
            print()
            print('test',file)
            ss=open(os.path.join("tests",file),encoding='utf-8').read().split('\n')
            for i in get_headers('',ss):
                print(i)
            break
