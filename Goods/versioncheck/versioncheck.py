
class Checker:
    def __init__(self, sqlsv, COMPANYNAME, UNIFIEDPAYMCHID):
        self.sqlsv = sqlsv
        self.COMPANYNAME = COMPANYNAME
        self.UNIFIEDPAYMCHID = UNIFIEDPAYMCHID
        self.UNIFIEDPAYMCHID_lc = ''
        self.COMPANYNAME_lc = ''

    def cheackVersion(self):
        try:
            sql_COMPANYNAME = """select ParameterValue from "000".tbSystemParameter where parametercode = 'COMPANYNAME'"""
            self.COMPANYNAME_lc = self.sqlsv.execute(sql_COMPANYNAME)[0][0]
            sql_UNIFIEDPAYMCHID = """select ParameterValue from "000".tbSystemParameter where parametercode = 'UNIFIEDPAYMCHID'"""
            self.UNIFIEDPAYMCHID_lc = self.sqlsv.execute(sql_UNIFIEDPAYMCHID)[0][0]
        except Exception as e:
            return False
        else:
            if self.UNIFIEDPAYMCHID_lc == self.UNIFIEDPAYMCHID and self.COMPANYNAME_lc == self.COMPANYNAME:
                return True
            return False

