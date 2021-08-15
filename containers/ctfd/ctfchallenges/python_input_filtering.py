import re
import binascii
search1 = lambda inputa: bool(re.search(r'[a-z\s]', inputa ))
search2 = lambda inputa: bool(re.search(r'[^a-z\s]', inputa))
execinput1 = lambda input : exec(input) if not search1(input) else print('Input contained bad characters')
execinput2 = lambda input : exec(input) if not search2(input) else print('Input contained bad characters')
#bad = execinput(search())
string2hex = lambda string,encoding: [i for i in binascii.b2a_hex(bytes(string.encode(encoding)))]
#exit(bad)
out = []
test = ["","a","aa","x","\x","0","1","o\x","","",""]
for each in test:
    out.append(search1(string2hex(each)))
print(out)
#testsearch2 = lambda testarray: [i for i in search2(testarray)]

