from opera.operas import Opera
from dba.dba import sqlsv_gbk
import re


class Good():
    sqlsv = sqlsv_gbk
    __slots__ = (
        '__goodscode', '__iscategoryCode', '__goodstype', '__goodstypename', '__categorycode', '__categoryname',
        '__goodsno',
        '__basebarcode', '__goodsname', '__prodarea', '__goodsspec', '__mesureproperty', '__mesurepropertyname',
        '__goodsbrand', '__goodsbrandname'
        , '__purchtaxrate', '__saletaxrate', '__basemeasureunit', '__suppercode', '__cntcode', '__durability',
        '__isdecimalcontrol', '__purchprice', '__saleprice', '__hzsaleprice', '__specimenmoney', '__specimendays',
        '__wholepackrate', '__wholemeasureunit', '__psjjtype', '__jdrate', '__psj'
        , '__mdlztj', '__goodslength', '__goodswidth', '__goodsheight', '__goodspropertycode', "__isth", "__isgood",
        "isbt", "dba","__dict__", "issu", "__billnumber", "_gid")

    __goodstype_dict = {'0': '经代', '1': '联营', '2': 'A进A出', '3': 'A进B出', '4': '原料', '5': '生鲜归集', '6': '租赁'}
    __goodspropertycode_dict = {"自营蚂蚁": "0007", "自营自采": "0005"}
    #统计产生的类的数量
    success_sum = 0
    fail_sum = 0

    @classmethod
    def reset(cls):
        cls.fail_sum = 0
        cls.success_sum = 0

    def __init__(self):
        self.__goodscode = ""
        self.__iscategoryCode = ""
        self.__goodstype = ""
        self.__goodstypename = ""
        self.__categorycode = ""
        self.__categoryname = ""
        self.__goodsno = ""
        self.__basebarcode = ""
        self.__goodsname = ""
        self.__prodarea = ""
        self.__goodsspec = ""
        self.__mesureproperty = ""
        self.__mesurepropertyname = ""
        self.__goodsbrand = ""
        self.__goodsbrandname = ""
        self.__purchtaxrate = ""
        self.__saletaxrate = ""
        self.__basemeasureunit = ""  # 基本计量单位
        self.__suppercode = ""
        self.__cntcode = ""
        self.__durability = ""  # 保质天数
        self.__isdecimalcontrol = ""  # 小数控制
        self.__purchprice = ""  # 进价
        self.__saleprice = ""  # 售价
        self.__hzsaleprice = ""  # 海中售价
        self.__specimenmoney = ""  # 试销期目标金额
        self.__specimendays = ""
        self.__wholepackrate = ""  # 整件包装率
        self.__wholemeasureunit = ""  # 整件包装单位
        self.__psjjtype = ""  # 配送加价方式
        self.__jdrate = ""  # 加点率
        self.__psj = ""  # 配送价
        self.__mdlztj = ""  # 门店流转途径
        self.__goodslength = ""
        self.__goodswidth = ""
        self.__goodsheight = ""
        self.__goodspropertycode = []   # 商品属性编码
        self.__isgood = 1
        self.__billnumber = ""
        self.__gid = 0



    def isSuccess(self, value):
        if value == "":
            return False
        return True

    @property
    def goodscode(self):
        return self.__goodscode

    @goodscode.setter
    def goodscode(self, value):
        self.__goodscode = self.valtostring(value)

    @property
    def iscategoryCode(self):
        return self.__iscategoryCode

    @iscategoryCode.setter
    def iscategoryCode(self, value):
        self.__iscategoryCode = self.valtostring(value)
        if self.__iscategoryCode not in ('0', '1'):
            self.__iscategoryCode = ""

    @property
    def goodstype(self):
        return self.__goodstype

    @goodstype.setter
    def goodstype(self, value):
        self.__goodstype = self.valtostring(value)
        if self.__goodstype not in ('0', '1', '2', '3', '4', '5', '6'):
            self.__goodstype = ""

    @property
    def goodstypename(self):
        return self.__goodstypename

    @goodstypename.setter
    def goodstypename(self, value):

        self.__goodstypename = self.valtostring(value)
        if self.__goodstype_dict.get(self.__goodstype) != self.__goodstypename:
            self.__goodstypename = ""

    @property
    def categorycode(self):
        return self.__categorycode

    @categorycode.setter
    def categorycode(self, value):
        self.__categorycode = self.valtostring(value)
        # 品类开头必须是1-4，长度为9
        if not re.match(r"^[1-4][0-9]{8}", self.__categorycode):
            self.__categorycode = ""

    @property
    def categoryname(self):
        return self.__categoryname

    @categoryname.setter
    def categoryname(self, value):
        self.__categoryname = self.valtostring(value)
        if self.__categorycode == "":
            self.__categoryname = ""
        else:
            # 必须要创建数据库对象
            sql = """select CategoryName from [000].tbGoodsCategory where CategoryCode = '{}' """
            result = Good.sqlsv.execute(sql.format(self.__categorycode))
            if result:
                catename = result[0][0]
                if catename != self.__categoryname:
                    self.__categoryname = catename

    @property
    def goodsno(self):
        return self.__goodsno

    @goodsno.setter
    def goodsno(self, value):
        self.__goodsno = self.valtostring(value)

    @property
    def basebarcode(self):
        return self.__basebarcode

    @basebarcode.setter
    def basebarcode(self, value):
        self.__basebarcode = self.valtostring(value)
        if self.__basebarcode != "":
            # self.__basebarcode = self.__basebarcode.replace(' ', '').replace('\n', '').replace('\t', '')
            sql = f""" select 1 from [000].tbPackBarCode where BarCode = '{self.__basebarcode}' """
            result = Good.sqlsv.execute(sql)
            if result:
                self.__basebarcode = "xx"   # 用于判断商品是否存在！

    @property
    def goodsname(self):
        return self.__goodsname

    @goodsname.setter
    def goodsname(self, value):
        self.__goodsname = self.valtostring(value)
        if Opera().countzj(self.__goodsname) > 120:
            self.__goodsname = ""

    @property
    def prodarea(self):
        return self.__prodarea

    @prodarea.setter
    def prodarea(self, value):
        self.__prodarea = self.valtostring(value)

    @property
    def goodsspec(self):
        return self.__goodsspec

    @goodsspec.setter
    def goodsspec(self, value):
        self.__goodsspec = self.valtostring(value)

    @property
    def mesureproperty(self):
        return self.__mesureproperty

    @mesureproperty.setter
    def mesureproperty(self, value):
        self.__mesureproperty = self.valtostring(value)
        if self.__mesureproperty not in ("0", "1", "2"):
            self.__mesureproperty = ""
        else:
            self.__mesureproperty = self.valtostring(value)

    __mesureproperty_dict = {'0': '标准', '1': '计量', '2': '称重'}

    @property
    def mesurepropertyname(self):
        return self.__mesurepropertyname

    @mesurepropertyname.setter
    def mesurepropertyname(self, value):
        self.__mesurepropertyname = self.valtostring(value)
        if self.__mesureproperty_dict.get(self.__mesureproperty) != self.__mesurepropertyname:
            self.__mesurepropertyname = ""

    @property
    def goodsbrand(self):
        return self.__goodsbrand

    @goodsbrand.setter
    def goodsbrand(self, value):
        self.__goodsbrand = self.valtostring(value)
        if not self.__goodsbrand.isdigit():
            self.__goodsbrand = ""

    @property
    def goodsbrandname(self):
        return self.__goodsbrandname

    @goodsbrandname.setter
    def goodsbrandname(self, value):
        self.__goodsbrandname = self.valtostring(value)
        if self.__goodsbrandname != "":
            sql = f""" select brandname from [000].tbGoodsBrand where brandcode = '{self.__goodsbrand}' """
            result = Good.sqlsv.execute(sql)
            if result:
                brandname = result[0][0]
                if self.__goodsbrandname != brandname:
                    self.__goodsbrandname = brandname

    @property
    def purchtaxrate(self):
        return self.__purchtaxrate

    @purchtaxrate.setter
    def purchtaxrate(self, value):
        self.__purchtaxrate = self.valtofloat(value)

    @property
    def saletaxrate(self):
        return self.__saletaxrate

    @saletaxrate.setter
    def saletaxrate(self, value):
        self.__saletaxrate = self.valtofloat(value)

    @property
    def basemeasureunit(self):
        return self.__basemeasureunit

    @basemeasureunit.setter
    def basemeasureunit(self, value):
        self.__basemeasureunit = self.valtostring(value)

    @property
    def suppercode(self):
        return self.__suppercode

    @suppercode.setter
    def suppercode(self, value):
        self.__suppercode = self.valtostring(value)
        if len(self.__suppercode) != 8:
            self.__suppercode = ""

    @property
    def cntcode(self):
        return self.__cntcode

    @cntcode.setter
    def cntcode(self, value):
        self.__cntcode = self.valtostring(value)

    @property
    def durability(self):
        return self.__durability

    @durability.setter
    def durability(self, value):
        self.__durability = self.valtofloat(value)

    @property
    def isdecimalcontrol(self):
        return self.__isdecimalcontrol

    @isdecimalcontrol.setter
    def isdecimalcontrol(self, value):
        self.__isdecimalcontrol = self.valtostring(value)
        if self.__isdecimalcontrol not in ('0', '1'):
            self.__isdecimalcontrol = ""

    @property
    def purchprice(self):
        return self.__purchprice

    @purchprice.setter
    def purchprice(self, value):
        self.__purchprice = self.valtofloat(value)

    @property
    def saleprice(self):
        return self.__saleprice

    @saleprice.setter
    def saleprice(self, value):
        self.__saleprice = self.valtofloat(value)

    @property
    def hzsaleprice(self):
        return self.__hzsaleprice

    @hzsaleprice.setter
    def hzsaleprice(self, value):
        self.__hzsaleprice = self.valtofloat(value)

    @property
    def specimenmoney(self):
        return self.__specimenmoney

    @specimenmoney.setter
    def specimenmoney(self, value):
        self.__specimenmoney = self.valtofloat(value)

    @property
    def specimendays(self):
        return self.__specimendays

    @specimendays.setter
    def specimendays(self, value):
        self.__specimendays = self.valtofloat(value)

    @property
    def wholepackrate(self):
        return self.__wholepackrate

    @wholepackrate.setter
    def wholepackrate(self, value):
        self.__wholepackrate = self.valtofloat(value)
        if self.__wholepackrate != "":
            if self.__wholepackrate < 1.0:
                self.__wholepackrate = ""

    @property
    def wholemeasureunit(self):
        return self.__wholemeasureunit

    @wholemeasureunit.setter
    def wholemeasureunit(self, value):
        self.__wholemeasureunit = self.valtostring(value)

    @property
    def psjjtype(self):
        return self.__psjjtype

    @psjjtype.setter
    def psjjtype(self, value):
        self.__psjjtype = self.valtostring(value)
        if self.__psjjtype not in ('0', '1'):
            self.__psjjtype = ""

    @property
    def jdrate(self):
        return self.__jdrate

    @jdrate.setter
    def jdrate(self, value):
        # 配送方式： 0-加点率
        if self.__psjjtype == '0':
            self.__jdrate = self.valtofloat(value)
        else:
            self.__jdrate = ""

    @property
    def psj(self):
        return self.__psj

    @psj.setter
    def psj(self, value):
        # 配送方式： 1-定价
        if self.__psjjtype == '1':
            self.__psj = self.valtostring(value)
        else:
            self.__psj = ""

    @property
    def mdlztj(self):
        return self.__mdlztj

    mdlztj_dict = {'配送': '01', '直配': '02', '不控制': '03'}
    @mdlztj.setter
    def mdlztj(self, value):
        self.__mdlztj = self.valtostring(value)
        self.__mdlztj = Good.mdlztj_dict.get(self.__mdlztj)
        if not self.__mdlztj:
            self.__mdlztj = ""

    @property
    def goodslength(self):
        return self.__goodslength

    @goodslength.setter
    def goodslength(self, value):
        self.__goodslength = self.valtofloat(value)

    @property
    def goodswidth(self):
        return self.__goodswidth

    @goodswidth.setter
    def goodswidth(self, value):
        self.__goodswidth = self.valtofloat(value)

    @property
    def goodsheight(self):
        return self.__goodsheight

    @goodsheight.setter
    def goodsheight(self, value):
        self.__goodsheight = self.valtofloat(value)

    @property
    def goodspropertycode(self):
        return self.__goodspropertycode
    @goodspropertycode.setter
    def goodspropertycode(self, value):
        value = self.valtostring(value)
        if value != "":
            self.__goodspropertycode.append(self.__goodspropertycode_dict.get(value))

    @property
    def isth(self):
        return self.__isth
    @isth.setter
    def isth(self, value):
        value = self.valtostring(value)
        if value != "":
            self.__isth = 1

    @property
    def isgood(self):
        return self.__isgood

    @isgood.setter
    def isgood(self, value):
        if value in (0, 1):
            if self.__isgood == 0:
                return
            else:
                self.__isgood = value
        else:
            self.__isgood = 1

    @property
    def billnumber(self):
        return self.__billnumber

    @billnumber.setter
    def billnumber(self,value):
        self.__billnumber = self.valtostring(value)

    @property
    def gid(self):
        return self.__gid

    @gid.setter
    def gid(self, value):
        self.__gid = self.valtofloat(value)
        if self.__gid != "":
            self.__gid = int(self.__gid)

    # 根据商品的配送加价方式，判断是加价还是加价率
    def check(self):
        self.isbt = [self.__iscategoryCode, self.__goodstype, self.__categorycode, self.__categoryname,
                     self.__goodsname, self.__mesureproperty, self.__purchtaxrate, self.__saletaxrate,
                     self.__suppercode, self.__cntcode, self.__durability, self.__isdecimalcontrol, self.__purchprice,
                     self.__saleprice, self.__specimenmoney, self.__specimendays, self.__wholepackrate,
                     self.__wholemeasureunit, self.__psjjtype, self.__mdlztj]
        if self.__psjjtype == '0':
            self.isbt.append(self.__jdrate)
        else:
            self.isbt.append(self.__psj)
        result = Opera().allTrue(self.isbt)
        if result is True and self.isgood != 0:
            Good.success_sum += 1
            return True
        else:
            Good.fail_sum += 1
            return False

    def valtostring(self, value):
        return Opera().valtostring(value)

    def valtofloat(self, value):
        return Opera().valtofloat(value)

# gd = Good()
# gd.billnumber = '111111111'
# gd.gid = 0
# print(gd.billnumber, gd.gid)