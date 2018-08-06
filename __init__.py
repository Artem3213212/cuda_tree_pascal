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
    if var_at_begin:
        vars = var_block_parse()
    else:
        vars = []
    TO_SKIP = ['class','implementation','interface']
    zz=[]
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
        elif s.lower() == 'const':
            vars+=const_block_parse()
        elif s.lower() in ['var']+ACCESS_CONTROL:
            vars+=var_block_parse()
        elif s.lower() in FUNCS:
            zz+=z
            z=function_parse(begin_pos,funcreg)
        elif s.lower() == 'begin':
            if z == []:
                begin_block_parse()
            else:
                zz+=[(z[0][0],z[0][1],5,z[1:]+begin_block_parse())]
            z=[]
        elif s.lower() == 'end':
            while ended and not get() in [';','.']:
                pass
            break
        elif s.lower() in ['initialization','finalization']:
            break
    if vars:
        return [(vars[0][0],'var&const',2,vars)]+zz+z#(current_begin,'block',0,z)#(current_begin,'name',icon,z)
    else:
        return zz+z

def begin_block_parse():
    i = 0
    s = 'begin'
    while ended:
        if s.lower() in ['begin','case']:
            i-=1
        if s.lower() == 'end':
            i-=1
            if i == 0:
                break
        s = get()
    while ended and not get() in [';','.']:
        pass
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
    f=True
    s=''
    ss=''
    while not ended:
        ss = get()
        if ss in ['(',':',';']:
            break
        elif ss=='.':
            f=False
        s=s+ss
    if ss == '(':
        while not ended and not get()==')':
            pass
        ss = get()
    if ss == ':':
        while not ended and not get()==';':
            pass
    if f:
        f = True
        for i in funcreg:
            if i==s:
                f = False
                break
        if f:
            funcreg.append(s)
            post_clear()
            return [(begin_pos,s,5,[])]
    post_clear()
    return []

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
        if s.lower() in ['class','begin','end','implementation','interface','initialization','finalization']+ACCESS_CONTROL+FUNCS+BLOCKS:
            restore(s)
            break
        elif not ended:
            i=0
            while not ended:
                ss=get()
                if ss.lower()=='packed':
                    ss=get()
                if s.lower()=='specialize':
                    s=get()
                if ss.lower()=='record':
                    z=(current_begin,s,7,std_block_parse())
                if ss.lower()=='class':
                    ss=get()
                    if ss.lower()=='of':
                        while get()!=';':
                            pass
                        z.append(tuple([begin_pos,objname,1,[]]))
                    elif ss!=';':
                        restore(ss)
                        z.append(tuple([begin_pos,objname,1,class_block_parse()]))
                    else:
                        continue
                if ss=='(':
                    i+=1
                elif ss==')':
                    i-=1
                elif ss==';' and i<=0:
                    break
            z.append(tuple([current_begin,s,7,[]]))
    return z

def const_block_parse():
    z=[]
    while not ended:
        s = get()
        current_begin = line
        if s.lower() in ['class','begin','end','implementation','interface','initialization','finalization']+ACCESS_CONTROL+FUNCS+BLOCKS:
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
        elif s.lower() in ['procedure','function','begin']+BLOCKS:
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
                elif is_name(s):
                    while get()!=';':
                        pass
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
    else:
        restore(s)
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
    for file in ['jsonconf.pp']:#os.listdir("tests"):
        if file.endswith(".pp") or file.endswith(".pas"):
            print()
            print('test',file)
            ss=open(os.path.join("tests",file),encoding='utf-8').read().split('\n')
            for i in get_headers('',ss):
                print(i)
            break
