if __name__=="__main__":
    from pascal_tokenizer import *
else:
    from .pascal_tokenizer import *

BLOCKS=['uses','var','const','type']
FUNCS=['function','procedure','constructor','destructor']
ACCESS_CONTROL=['private','protected','public','published']

def get():
    global ended, line
    s = tokenizer.pop()
    ended = s[3]
    line = s[1][0]
    return s[0]

def restore(s):
    s = tokenizer.push([s,[line],[],ended])

def std_block_parse():
    TO_SKIP = ['class']
    z=[]
    #current_begin=line
    while not ended:
        s = get().lower()
        begin_pos = line
        if s in TO_SKIP:
            continue
        if s=='[':
            while not ended and get()!=']':
                pass
        elif s=='uses':
            uses_block_parse()
        elif s=='type':
            z=z+type_block_parse()
            break
        elif s=='const':
            z=z+const_block_parse()
            break
        elif s in FUNCS:
            pass#metod
        elif s=='begin':
            pass
        elif s=='end':
            while get()!=';':
                pass
            break
    return z#(current_begin,'block',0,z)#(current_begin,'name',icon,z)

def uses_block_parse():
    global uses
    while not ended:
        s = get()
        if s==';':
            break
        elif not (s in [',','in'] or is_string(s)):
            uses.append(tuple([s,line]))

def const_block_parse():
    z=[]
    while not ended:
        s = get()
        current_begin = line
        if s in ['class','begin','end']+ACCESS_CONTROL+FUNCS+BLOCKS:
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
    global out
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
        elif s=='generic':
            s = get()
        elif s in ['procedure','function','begin']+BLOCKS:
            tokenizer.push([s,[line],[],ended])
            break
        elif s=='class':
            ss=get()
            if ss=='operator':
                continue
        elif is_name(s):
            objname=s
            ss=get()
            if ss==';':
                continue
            elif ss=='=':
                s=get()
                if s=='packed':
                    s=get()
                if s=='specialize':
                    s=get()
                if s==';':
                    continue
                elif s=='class':
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
                elif s=='record':
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
    if s in ['absract','sealed']:
        s=get()
    if s=='(':
        while not ended and get()!=')':
            pass
    else:
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
    ss=open('C:\\codetyphon\\fpcsrc\\tests\\test\\alglib\\u_ap.pp').read().split('\n')
    for i in get_headers('',ss):
        print(i)
    ss=open('C:\\codetyphon\\fpcsrc\\tests\\test\\jvm\\classlist.pp').read().split('\n')
    for i in get_headers('',ss):
        print(i)