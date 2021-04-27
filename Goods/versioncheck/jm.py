from datetime import datetime
from hashlib import md5
import random


def fu(s):
    def inf(i):
        rint = random.randint(0, len(s) - 2)
        a = s[rint: rint + 2]
        return i+a
    return inf


m = md5()

sq = '*/sdsdsdsdsdtl5740' + str(random.randint(0, 10000))
m.update(sq.encode('UTF8'))
str_q = m.hexdigest()
ts = str(datetime.today().timestamp())
m.update(ts.encode("UTF8"))
str_h = m.hexdigest()
m.update((str_q+str_h).encode())
s = m.hexdigest()
mp = map(fu(s), str_h)
s = [i for i in mp]
s.reverse()
# print(s)
s = str(s).replace('[', '').replace(']', '').replace("'", '').replace(",", '').replace(" ", '')
s = s[0:len(str_h)].upper() + str_h[0:round((len(str_h)/2))+random.randint(0, 5)] + str_q[0:round(len(str_q)/2)+random.randint(0, 5)].upper() + str_h[0:round((len(str_h)/2))+random.randint(0, 5)]
print(s)