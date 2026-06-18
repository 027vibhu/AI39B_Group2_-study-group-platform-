import re
from pathlib import Path
path = Path(r'c:\Users\almir\Downloads\AI39B_Group2_-study-group-platform-\app\static\css\notes.css')
text = path.read_text(encoding='utf-8')
print('len', len(text))
stack=[]
in_comment=False
for i,(c,n) in enumerate(zip(text, text[1:]+" ")):
    if not in_comment and c=='/' and n=='*': in_comment=True
    elif in_comment and c=='*' and n=='/': in_comment=False
    elif not in_comment:
        if c=='{': stack.append(i)
        elif c=='}':
            if not stack: print('unmatched closing brace at', i)
            else: stack.pop()
if in_comment: print('comment not closed')
print('remaining braces', len(stack))
# find any comment opening that doesn't start with /*
for m in re.finditer(r'^[ \t]*\*', text, re.M):
    print('star comment start at', m.start(), repr(text[m.start():m.start()+20]))
