from dba.dba import Sqlserve

sql = """ insert into errorcardinnum5 values('{}', '{}') """
sqlsv = Sqlserve('106.15.201.166', 'sa', '!QAZ2wsx', 'BZ_CRM')
with open("1.txt", 'r') as f:
    while True:
        s = f.readline()
        if s and s != '':
            s = s.replace(';', '').replace('?', '')
            cardcode = s[0:10]
            cardinnum = s[0:18]
            temp = sql.format(cardcode, cardinnum)
            print(temp)
            sqlsv.executeNoSet(temp)
        else:
            break
sqlsv.close()


