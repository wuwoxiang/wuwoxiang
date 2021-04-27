import pymssql
from config.config import DataConfig
from tkinter import messagebox as mg
import os


class Sqlserve:
    cursor_w = ""

    def __init__(self, servername, username, password, dbaname, charset="utf8"):
        self.servername = servername
        self.username = username
        self.password = password
        self.dbaname = dbaname
        self.charset = charset
        self.con = ""
        self.con = pymssql.connect(self.servername, self.username, self.password, self.dbaname, charset=self.charset)
        self.cursor = self.con.cursor()
        Sqlserve.cursor_w = self.cursor

    def execute(self, sql):
        self.sql = sql.encode(self.charset)
        self.cursor.execute(self.sql)
        return self.cursor.fetchall()

    def executeNoSet(self, sql):
        self.sql = sql.encode(self.charset)
        self.cursor.execute(self.sql)
        self.commit()

    def executeManyNoSet(self, sql, data):
        self.sql = sql.encode(self.charset)
        self.cursor.executemany(self.sql, data)
        self.commit()

    def commit(self):
        self.con.commit()

    def close(self):
        self.con.close()

    def reconn(self):
        self.close()
        self.__init__(self.servername, self.username, self.password, self.dbaname, self.charset)

    def __del__(self):
        if self.con != '':
            self.con.close()
            del self.con


datacf = DataConfig()
data_dir = datacf.getDatacf()
employeecode= data_dir.get("employeecode")
try:
    sqlsv_gbk = Sqlserve(data_dir.get("server"), 'sa', data_dir.get("password"), data_dir.get("dbaname"), charset="GBK")
    sqlsv_utf = Sqlserve(data_dir.get("server"), 'sa', data_dir.get("password"), data_dir.get("dbaname"), charset="utf8")
except Exception as e:
    print(e)
    file_path = os.path.join(os.getcwd(), datacf.filepath.split('/')[1])
    mg.showwarning(title='提示', message=f'数据链接异常!\n您现在链接的服务器是：{data_dir.get("server")}'
                                       f'\n请检查数据库配置文件:{file_path}')


employeename = sqlsv_gbk.execute(f""" select EmployeeName from [000].TBEMPLOYEE with(nolock)
                                        where EmployeeCode='{employeecode}'""")
if employeename:
    employeename = employeename[0][0]
else:
    employeename = ''

