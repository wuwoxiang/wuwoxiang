from dba.dba import Sqlserve

sqlsv = Sqlserve('106.15.201.166','sa','!QAZ2wsx','BZ_CRM')

with open("./1.txt") as f:
    while True:
        s = f.readline()
        if s !='' and s:
            s = s.replace(';', '').replace('?', '')
            cardcode = s[0:10]
            cardinnum = s[0:18]
            print(cardcode, cardinnum)
        else:
            break


