from opera.operas import Opera
from datetime import datetime, timedelta
from dba.dba import employeename, employeecode

class InDba(Opera):
    def __init__(self):
        self.iscreategoods = 0
        self.sCodeType = "ena13"  # ena13 itf14
        self.BaseBillNumber = ""
        self.contBillNumber = ""
        self.psjjBillNumber = ""
        self.contractBillNumber = []

    def isExecute(self, BillNumber, sqlsv_gbk):
        sql = f""" select 1 from [000].tb{BillNumber[3:9]}_PriceBill where ExecuteDate <> '' and BillNumber = '{BillNumber}' """
        result = sqlsv_gbk.execute(sql)
        if result:
            return True
        return False

    # 生成商品基本单
    def goodsBaseBill(self, result_set, sqlsv_gbk):
        today = datetime.today().strftime("%Y%m%d")
        gid = 0
        BillNumber = self.createBillno(sqlsv_gbk)
        self.BaseBillNumber = BillNumber
        # 插入tb202011_Goods
        issuc = self.insert_tbyyyymm_PriceBill(today, BillNumber, sqlsv_gbk, '0')
        if issuc:
            try:
                min_barcode = ""
                for key in result_set.keys():
                    good = result_set.get(key)[0]
                    good.goodscode = self.createGoodsCode(today, good, sqlsv_gbk)
                    good.basebarcode = self.createbarCode(today, good, 'ena13', sqlsv_gbk, min_barcode)
                    if good.mesureproperty != 0:
                        min_barcode = good.basebarcode
                    # 插入tbyyyymm_PriceBill
                    self.insert_tbyyyymm_Goods(today, good, BillNumber, gid, sqlsv_gbk)
                    good.billnumber = BillNumber
                    good.gid = gid
                    gid += 1
                    self.insert_tbyyyymm_PackBar(today, good, BillNumber, sqlsv_gbk)
            except Exception as e:
                print(e)
                sqlsv_gbk.reconn()
        sqlsv_gbk.reconn()
        print(f"""商品基本信息单：{BillNumber}，已经生成！""")

    # 进目录
    def jMl(self, result_set, sqlsv_gbk):
        # result_set = { row:(good, [node,...]),.. }
        today = datetime.today().strftime("%Y%m%d")
        BillNumber = self.createBillno(sqlsv_gbk)
        issuc = self.insert_tbyyyymm_PriceBill_execute(today, BillNumber, sqlsv_gbk, '9')
        self.contBillNumber = BillNumber
        if issuc:
            try:
                good_node_list = []
                good_list = [' ', ' ']
                for key in result_set.keys():
                    goodnode = result_set.get(key)
                    good = goodnode[0]
                    good_list.append(good.goodscode)
                    sql = f""" update a set CirculationModeCode = '{good.mdlztj}' 
                                                    from [000].tbgoods a where goodscode = '{good.goodscode}' """
                    sqlsv_gbk.executeNoSet(sql)
                    sql = f""" update a set WorkStateCode = '0' 
                                                    from [000].tbgoods a where goodscode = '{good.goodscode}' """
                    sqlsv_gbk.executeNoSet(sql)
                    for node in goodnode[1]:
                        good_node_list.append((good, node))
                        # 商品主档的改成在目录
                sql = f""" update [000].tbGoods set IsInCatalog = '1' where goodscode in {tuple(good_list)} """
                sqlsv_gbk.executeNoSet(sql)
                self.insert_tbyyyymm_goodscontrol(today, good_node_list, BillNumber, sqlsv_gbk)
                self.insert_tbDeptWorkState(good_node_list, sqlsv_gbk)
                self.insert_tbDeptCirculation(good_node_list, sqlsv_gbk)
                self.insert_tbGoodsCatalog(good_node_list, sqlsv_gbk)
            except Exception as e:
                print(e)
                sqlsv_gbk.reconn()
        sqlsv_gbk.reconn()
        print(f"""进目录单据：{BillNumber}，已经生成！""")

    # 配送价格单
    def pSJGD(self, result_set, sqlsv_gbk):
        # result_set = { row:(good, [node,...]),.. }
        today = datetime.today().strftime("%Y%m%d")
        BillNumber = self.createBillno(sqlsv_gbk)
        issuc = self.insert_tbyyyymm_PriceBill(today, BillNumber, sqlsv_gbk, '5')
        self.psjjBillNumber = BillNumber
        gid = 0
        if issuc:
            try:
                good_list = []
                for key in result_set.keys():
                    goodnode = result_set.get(key)
                    good = goodnode[0]
                    good_list.append(good)
                    self.insert_tbyyyymm_Goods(today, good, BillNumber, gid, sqlsv_gbk)
                sql = """ select CategoryCode from [000].tbDeptCategory where CategoryItemCode = '0000' """
                CategoryCodes = sqlsv_gbk.execute(sql)
                self.insert_tbyyyymm_DeptPrice(today, good_list, BillNumber, CategoryCodes, sqlsv_gbk)
                self.insert_tbyyyymm_DeptPriceLog(today, good_list, BillNumber, CategoryCodes, sqlsv_gbk)
                self.insert_tbyyyymm_DistPrice(today, good_list, BillNumber, CategoryCodes, sqlsv_gbk)
            except Exception as e:
                print(e)
                sqlsv_gbk.reconn()
        sqlsv_gbk.reconn()
        print(f"""配送价格单：{BillNumber}，已经生成！""")

    # 合同定义
    def htGoods(self, result_set, sqlsv):
        result_set_gd = []
        for key in result_set.keys():
            goodnode = result_set.get(key)
            good = goodnode[0]
            result_set_gd.append(good)
        try:
            today = datetime.today().strftime("%Y%m%d")
            # 合同对应的修改ID
            conRepid = {}
            # 记录合同和单据号的关系
            conBill = {}
            # 记录单据号没个单据号是否创建成功！
            result_ok_bill = {}
            # 记录单据中合同最后修改对应的编码
            issuc = False
            nodes = sqlsv.execute(f"""select distinct DeptType, '0004' categoryitemcode, deptcode  
                                        from [000].tbContractDepts a where  depttype = '0'
                                        union all
                                        select distinct DeptType, '' categoryitemcode, deptcode  from [000].tbContractDepts a 
                                        where DeptCode not in 
                                        (select NodeCode from [000].tbnode  where nodename like '%T%' or nodename like '%t%')
                                        and depttype <> '0' """)

            # 获取所有合同,和对应的修改ID：RepairSignID
            htcode_list = [good.cntcode for good in result_set_gd]
            htcode_list += [' ', ' ']
            sql = f"""select ContractNumber, max(RepairSignID) RepairSignID from [000].TBCONTRACT  
                                                where contractnumber in {tuple(htcode_list)} group by ContractNumber """
            result_con_repair = sqlsv.execute(sql)
            conRepid = {conr[0]: conr[1] for conr in result_con_repair}
            for good in result_set_gd:
                # 如果合同对应单据号出现过
                if good.cntcode in conBill.keys():
                    BillNumber = conBill.get(good.cntcode)
                else:
                    BillNumber = self.createContBillno(sqlsv)
                    conBill[good.cntcode] = BillNumber

                # 记录所有单据号
                if BillNumber not in self.contractBillNumber:
                    self.contractBillNumber.append(BillNumber)
                    issuc = self.insert_tbyyyymm_ConGoodsBill(today, BillNumber, conRepid.get(good.cntcode), good, sqlsv)
                    result_ok_bill[BillNumber] = issuc

            # # 判断合同和品牌品类的对照
            # # 判断合同在合同品牌对照中是否出现
            # sql = f"""select distinct ContractNumber, BrandCode from "000".tbContractBrands with(nolock)
            #         where ContractNumber in {tuple(htcode_list)} """
            # brand_con = sqlsv.execute(sql)
            # brand_con = self.hBList(brand_con)
            # sql_brand = ''
            # # 判断合同在合同品类对照中是否出现
            # sql = f"""select distinct ContractNumber, categorycode from "000".tbContractCates with(nolock)
            #                 where ContractNumber in {tuple(htcode_list)} """
            # cate_con = sqlsv.execute(sql)
            # cate_con = self.hBList(cate_con)
            # sql_cate = ''

            # for good in result_set_gd:
            #     # 如果没有品牌，就不插入
            #     if good.goodsbrand:
            #         if good.cntcode not in brand_con.keys():
            #             sql_brand += f"""insert into "000".tbContractBrands(ContractNumber,RepairSignID,BrandCode)
            #                                 values('{good.cntcode}',{conRepid.get(good.cntcode)},'{good.goodsbrand}')  """
            #         else:
            #             for each in brand_con.keys():
            #                 if good.cntcode == each and good.goodsbrand not in brand_con.get(each):
            #                     sql_brand += f"""insert into "000".tbContractBrands(ContractNumber,RepairSignID,BrandCode)
            #                                     values('{good.cntcode}',{conRepid.get(good.cntcode)},'{good.goodsbrand}')  """
            #                     if brand_con.get(good.cntcode):
            #                         brand_con.get(good.cntcode).append(good.goodsbrand)
            #                     else:
            #                         brand_con[good.cntcode] = [good.goodsbrand]
            #
            # for good in result_set_gd:
            #     if good.cntcode not in cate_con.keys():
            #         sql_cate += f"""insert into "000".tbContractCates(ContractNumber,RepairSignID,CategoryItemCode,
            #                                     CategoryCode)
            #                         values('{good.cntcode}',{conRepid.get(good.cntcode)},'0000','{good.categorycode}')  """
            #         if cate_con.get(good.cntcode):
            #             cate_con.get(good.cntcode).append(good.categorycode)
            #         else:
            #             cate_con[good.cntcode] = [good.categorycode]
            #     else:
            #         for each in cate_con.keys():
            #             if good.cntcode == each and good.categorycode not in cate_con.get(each):
            #                 sql_cate += f"""insert into "000".tbContractCates(ContractNumber,RepairSignID,CategoryItemCode,
            #                                     CategoryCode)
            #                         values('{good.cntcode}',{conRepid.get(good.cntcode)},'0000','{good.categorycode}')  """
            #                 if cate_con.get(good.cntcode):
            #                     cate_con.get(good.cntcode).append(good.categorycode)
            #                 else:
            #                     cate_con[good.cntcode] = [good.categorycode]
            #
            # if sql_brand:
            #     sqlsv.executeNoSet(sql_brand)
            # if sql_cate:
            #     sqlsv.executeNoSet(sql_cate)

            self.insert_tbyyyymm_ConGoodsDetail(today, conBill, conRepid, result_set_gd, sqlsv)
            self.insert_tbyyyymm_DeptConGoods(today, conBill, result_set_gd, nodes, sqlsv)
            print(f"""合同商品定义：{self.contractBillNumber}，已经生成！""")
            sqlsv.reconn()
        except Exception as e:
            print(e)
            sqlsv.reconn()

    # 单据号生成
    def createBillno(self, sqlsv_gbk):
        today = datetime.today().strftime("%Y%m%d")
        sql = f"""select max(billnumber) from [000].tb{today[0:6]}_PriceBill """
        BillNumber = sqlsv_gbk.execute(sql)
        # max查询结果如果没有的情况是[(None,)]
        if BillNumber[0][0]:
            BillNumber = BillNumber[0][0]
            if BillNumber[3:9] == today[0:6]:
                BillNumber = '000' + str(int(BillNumber) + 1)
            else:
                BillNumber = '000' + today + '000001'
        else:
            BillNumber = '000' + today + '000001'
        return BillNumber

    def hBList(self, ls):
        dt = {}
        for each in ls:
            if not dt:
                dt[each[0]] = [each[1]]
            elif each[0] in dt.keys():
                dt.get(each[0]).append(each[1])
            else:
                dt[each[0]] = [each[1]]
        return dt

    # 合同单据号生成
    def createContBillno(self, sqlsv):
        today = datetime.today().strftime("%Y%m%d")
        sql = f"""select max(billnumber) from [000].tb{today[0:6]}_ConGoodsBill """
        BillNumber = sqlsv.execute(sql)
        if BillNumber[0][0]:
            BillNumber = BillNumber[0][0]
            # 避免日期和单据不符
            if BillNumber[3:9] == today[0:6]:
                BillNumber = '000' + str(int(BillNumber) + 1)
            else:
                BillNumber = '000' + today + '000001'
        else:
            BillNumber = '000' + today + '000001'
        return BillNumber

    # 通过条码，判断商品是否存在
    def goodIsExists(self, BaseBarCode, sqlsv_gbk):
        if BaseBarCode == "" or BaseBarCode is None:
            return False
        sql = f""" select 1 from [000].tbGoods where BaseBarCode = '{BaseBarCode}' """
        result = sqlsv_gbk.execute(sql)
        if not result:
            return False
        else:
            return True

    # 做商品信息单
    # 插入tb202011_Goods, 做商品信息单
    def insert_tbyyyymm_Goods(self, today, good, BillNumber, gid, sqlsv_gbk):
        sql = f"""insert into [000].tb{today[0:6]}_Goods
                    (IsDetail,GoodsCode,BillNumber,GoodsId,GoodsNo,GoodsName,ProdArea,GoodsSpec,BaseMeasureUnit,
                    WholePackRate,WholeMeasureUnit,BaseBarCode,GoodsBrand,SupplierCode,PurchTaxRate,SaleTaxRate,PurchPrice,SalePrice,
                    MinSalePrice,MaxSalePrice,Durability,DaysBefCheckIn,IsDecimalControl,BuildDate,LastModifyDate,SeasonalCode,
                    IsCategoryCode,GrossMargin,MesureProperty,GoodsRemark,remark,DetailType,CategoryItemCode,CategoryCode,GoodsType,
                    ManagerMode,SubGroupCode1,SubGroupCode2,DurCondition,GoodsLevel,GoodsLength,GoodsWidth,GoodsHeight,SpecimenMoney,
                    SpecimenDays,MrProTypeCode,MrBillNumber,B2BBillNumber,MotherCode,SubCodeAttribute1,SubCodeAttribute2,SKUNameFormat,
                    LastModifyTime) values({1},'{good.goodscode}','{BillNumber}',{gid},'{good.goodsno}', '{good.goodsname}','{good.prodarea}',
                    '{good.goodsspec}','{good.basemeasureunit}',{good.wholepackrate},'{good.wholemeasureunit}','{good.basebarcode}',
                    '{good.goodsbrand}','{good.suppercode}',{good.purchtaxrate},{good.saletaxrate},{good.purchprice},{good.saleprice},
                    0,0,{good.durability},0,{good.isdecimalcontrol},'{today}','','',{good.iscategoryCode},0,{good.mesureproperty},
                    '','',0,'0000','{good.categorycode}',{good.goodstype},0,'','','','',{self.int_zero(good.goodslength)},{self.int_zero(good.goodswidth)},
                    {self.int_zero(good.goodsheight)},{good.specimenmoney},{good.specimendays},'','','','','','','','')"""
        try:
            sqlsv_gbk.executeNoSet(sql)
            return True
        except Exception as e:
            print(e)
            return False

        # 插入tb202011_PriceBill

    # 插入tb202011_PackBar, 做商品信息单
    def insert_tbyyyymm_PackBar(self, today, good, BillNumber, sqlsv_gbk):
        # 整件包装率为1的时候，包装单位和商品基本单位一样
        sql1 = f"""insert into [000].tb{today[0:6]}_PackBar
                       (BillNumber,GoodsCode,PackId,BarCode,MeasureUnit,PackRate,ProdArea,GoodsSpec,IsWholePack) 
                values('{BillNumber}','{good.goodscode}',0,'{good.basebarcode}','{good.basemeasureunit}',1,
                '{good.prodarea}','{good.goodsspec}',0)"""

        # 整件包装不为1时候第二条是整件包装单位
        sql2 = f"""insert into [000].tb{today[0:6]}_PackBar
                       (BillNumber,GoodsCode,PackId,BarCode,MeasureUnit,PackRate,ProdArea,GoodsSpec,IsWholePack) 
                values('{BillNumber}','{good.goodscode}',0,'{good.basebarcode}','{good.basemeasureunit}',1,
                '{good.prodarea}','{good.goodsspec}',0)"""
        sql3 = f"""insert into [000].tb{today[0:6]}_PackBar
                       (BillNumber,GoodsCode,PackId,BarCode,MeasureUnit,PackRate,ProdArea,GoodsSpec,IsWholePack) 
                values('{BillNumber}','{good.goodscode}',1,'','{good.wholemeasureunit}',{good.wholepackrate},
                '{good.prodarea}','',1)"""

        try:
            if good.wholepackrate > 1:
                sqlsv_gbk.executeNoSet(sql2)
                sqlsv_gbk.executeNoSet(sql3)
            else:
                sqlsv_gbk.executeNoSet(sql1)
            return True
        except Exception as e:
            print(e)
            return False

    # 插入tb202011_PriceBill, 做商品信息单
    def insert_tbyyyymm_PriceBill(self, today, BillNumber, sqlsv_gbk, pricebilltype):
        sql = f"""insert into [000].tb{today[0:6]}_PriceBill
                (BillNumber,PriceBillType,BuildDate,BuildManCode,BuildManName,IsExecute,ExecuteManCode,ExecuteManName,
                ExecuteDateTime,Remark,LastModManCode,LastModManName,LastModDate,ExecuteDate,BeginDate,EndDate,
                TransRuleCode,SupplierCode,ContractNumber,RepairSignID,IsJgSuppGoods,SubHQCode,IsSaleCardAgio,PriceType) 
            values('{BillNumber}',{pricebilltype},'{today}','{employeecode}','{employeename}',0,'','','','','','','','','','','','','',0,0,'', 0, 0)"""
        try:
            sqlsv_gbk.executeNoSet(sql)
            # print(sql)
            return True
        except Exception as e:
            print(e)
            return False

    # 插入tb202011_PriceBill，进目录
    def insert_tbyyyymm_PriceBill_execute(self, today, BillNumber, sqlsv_gbk, pricebilltype):
        exectime = datetime.today().strftime('%Y%m%d%H%M%S%f')[0: -3]
        sql = f"""insert into [000].tb{today[0:6]}_PriceBill
                (BillNumber,PriceBillType,BuildDate,BuildManCode,BuildManName,IsExecute,ExecuteManCode,ExecuteManName,
                ExecuteDateTime,Remark,LastModManCode,LastModManName,LastModDate,ExecuteDate,BeginDate,EndDate,
                TransRuleCode,SupplierCode,ContractNumber,RepairSignID,IsJgSuppGoods,SubHQCode,IsSaleCardAgio,PriceType) 
            values('{BillNumber}',{pricebilltype},'{today}','{employeecode}','{employeename}',1,
                '{employeecode}','{employeename}','{exectime}','','{employeecode}','{employeename}','{today}','{today}',
                '','','','','',0,0,'',0,0)"""
        try:
            sqlsv_gbk.executeNoSet(sql)
            # print(sql)
            return True
        except Exception as e:
            print(e)
            return False

    # 进目录
    def insert_tbyyyymm_goodscontrol(self, today, good_node_list, BillNumber, sqlsv_gbk):
        flag = 0
        sql = f"""insert into [000].tb{today[0:6]}_goodscontrol(BillNumber,GoodsCode,DeptType,CategoryItemCode,DeptCode,WorkStateCode,
                CirculationModeCode,YWorkStateCode,YCirculationModeCode,TempBeginDate,TempEndDate,TempWorkStateCode,DeptRemark)
                select BillNumber,GoodsCode,DeptType,CategoryItemCode,DeptCode,WorkStateCode,
                CirculationModeCode,YWorkStateCode,YCirculationModeCode,TempBeginDate,TempEndDate,TempWorkStateCode,DeptRemark
                from (values """
        for each in good_node_list:
            sql += f"""('{BillNumber}', '{each[0].goodscode}', 1, '', '{each[1].nodecode}','0', '{each[0].mdlztj}', 
                        '','','','','',''),"""
            flag = 1
        try:
            if flag == 1:
                sql = sql[:sql.rfind(',')] + """) as tl(BillNumber,GoodsCode,DeptType,CategoryItemCode,DeptCode,
                WorkStateCode, CirculationModeCode,YWorkStateCode,YCirculationModeCode,TempBeginDate,TempEndDate,
                TempWorkStateCode,DeptRemark)"""
                sqlsv_gbk.executeNoSet(sql)
                return True
            return False
        except Exception as e:
            print(sql)
            print(e)
            return False

    # 进目录
    # 目录表
    def insert_tbGoodsCatalog(self, good_node_list, sqlsv_gbk):
        flag = 0
        sql = f"""insert into [000].tbGoodsCatalog(GoodsCode,DeptType,CategoryItemCode,DeptCode)
                select GoodsCode,DeptType,CategoryItemCode,DeptCode from (values """
        for each in good_node_list:
            sql += f"""('{each[0].goodscode}', '1', '', '{each[1].nodecode}'),"""
            flag = 1
        try:
            if flag == 1:
                sql = sql[:sql.rfind(',')] + """) as tl(GoodsCode,DeptType,CategoryItemCode,DeptCode)"""
                sqlsv_gbk.executeNoSet(sql)
                return True
            return False
        except Exception as e:
            print(sql)
            print(e)
            return False

    # 进目录
    def insert_tbDeptWorkState(self, good_node_list, sqlsv_gbk):
        flag = 0
        sql = f""" insert into [000].tbDeptWorkState(GoodsCode,DeptType,CategoryItemCode,DeptCode,WorkStateCode,TempBeginDate,
        TempEndDate,TempWorkStateCode,DeptRemark) select GoodsCode,DeptType,CategoryItemCode,DeptCode,WorkStateCode,
        TempBeginDate,TempEndDate,TempWorkStateCode,DeptRemark from (values """
        for each in good_node_list:
            sql += f"""('{each[0].goodscode}', 1, '', '{each[1].nodecode}', '0', '', '', '', ''),"""
            flag = 1
        try:
            if flag == 1:
                sql = sql[:sql.rfind(',')] + """) as tl(GoodsCode,DeptType,CategoryItemCode,DeptCode,WorkStateCode,
                TempBeginDate,TempEndDate,TempWorkStateCode,DeptRemark)"""
                sqlsv_gbk.executeNoSet(sql)
                return True
            return False
        except Exception as e:
            print(sql)
            print(e)
            return False

    # 进目录
    def insert_tbDeptCirculation(self, good_node_list, sqlsv_gbk):
        flag = 0
        sql = f""" insert into [000].tbDeptCirculation(GoodsCode,DeptType,CategoryItemCode,DeptCode,CirculationModeCode)
                select GoodsCode,DeptType,CategoryItemCode,DeptCode,CirculationModeCode from (values"""
        try:
            for each in good_node_list:
                sql += f"""('{each[0].goodscode}', 1, '', '{each[1].nodecode}', '{each[0].mdlztj}'),"""
                flag = 1
            if flag == 1:
                sql = sql[:sql.rfind(',')] + """) as tl(GoodsCode,DeptType,CategoryItemCode,DeptCode,
                CirculationModeCode)"""
                sqlsv_gbk.executeNoSet(sql)
                return True
            return False
        except Exception as e:
            print(sql)
            print(e)
            return False

    # 配送价格单
    def insert_tbyyyymm_DeptPrice(self, today, good_list, BillNumber, CategoryCodes, sqlsv_gbk):
        flag = 0
        sql = f"""insert into [000].tb{today[0:6]}_DeptPrice(BillNumber,PriceId,GoodsCode,DeptType,CategoryItemCode,
                        DeptCode,PurchPrice,SalePrice,Points,MaxSalePrice,MinSalePrice,WholeSalePrice,AppSalePrice,
                        ContractNumbers,PriceCompensaType,FLimitPrice,SLimitPrice,TLimitPrice,MrProTypeCode,MrBillNumber,
                        EffectDate)
                select BillNumber,PriceId,GoodsCode,DeptType,CategoryItemCode,
                        DeptCode,PurchPrice,SalePrice,Points,MaxSalePrice,MinSalePrice,WholeSalePrice,AppSalePrice,
                        ContractNumbers,PriceCompensaType,FLimitPrice,SLimitPrice,TLimitPrice,MrProTypeCode,MrBillNumber,
                        EffectDate from(values"""
        try:
            for good in good_list:
                priceid = 0
                for CategoryCode in CategoryCodes:
                    sql += f"""('{BillNumber}', {priceid}, '{good.goodscode}', 0, '0000', '{CategoryCode[0]}',{good.purchprice},
                        {good.saleprice}, 0, 0, 0, 0, 0, '{good.cntcode}', 0, 0, 0, 0, '', '', ''),"""
                    flag = 1
                    priceid += 1
            if flag == 1:
                sql = sql[:sql.rfind(',')] + """) as tl(BillNumber,PriceId,GoodsCode,DeptType,CategoryItemCode,
                        DeptCode,PurchPrice,SalePrice,Points,MaxSalePrice,MinSalePrice,WholeSalePrice,AppSalePrice,
                        ContractNumbers,PriceCompensaType,FLimitPrice,SLimitPrice,TLimitPrice,MrProTypeCode,MrBillNumber,
                        EffectDate)"""
                sqlsv_gbk.executeNoSet(sql)
        except Exception as e:
            print(sql)
            print(e)

    # 配送价格单
    def insert_tbyyyymm_DeptPriceLog(self, today, good_list, BillNumber, CategoryCodes, sqlsv_gbk):
        flag = 0
        sql = f"""insert into [000].tb{today[0:6]}_DeptPriceLog(BillNumber,PriceId,CustomSign,GoodsCode,DeptType,
                    CategoryItemCode,DeptCode,PurchPrice,SalePrice,Points,MaxSalePrice,MinSalePrice,WholeSalePrice,
                            AppSalePrice,ContractNumbers,PriceCompensaType,FLimitPrice,SLimitPrice,TLimitPrice,EffectDate)
                select BillNumber,PriceId,CustomSign,GoodsCode,DeptType,
                    CategoryItemCode,DeptCode,PurchPrice,SalePrice,Points,MaxSalePrice,MinSalePrice,WholeSalePrice,
                            AppSalePrice,ContractNumbers,PriceCompensaType,FLimitPrice,SLimitPrice,TLimitPrice,EffectDate
                from (values"""
        try:
            for good in good_list:
                priceid = 0
                for CategoryCode in CategoryCodes:
                    sql += f"""('{BillNumber}', {priceid}, 0, '{good.goodscode}', '0', '0000', '{CategoryCode[0]}',
                            {self.int_zero(good.purchprice)}, {self.int_zero(good.saleprice)}, 0, 0, 0, 0, 0, 
                            '{good.cntcode}', 0, 0, 0, 0, ''), """
                    flag = 1
                    priceid += 1
            if flag == 1:
                sql = sql[:sql.rfind(',')] + """) as tl(BillNumber,PriceId,CustomSign,GoodsCode,DeptType,
                    CategoryItemCode,DeptCode,PurchPrice,SalePrice,Points,MaxSalePrice,MinSalePrice,WholeSalePrice,
                    AppSalePrice,ContractNumbers,PriceCompensaType,FLimitPrice,SLimitPrice,TLimitPrice,EffectDate)"""
                sqlsv_gbk.executeNoSet(sql)
                return True
            return False
        except Exception as e:
            print(sql)
            print(e)

    # 配送价格单
    def insert_tbyyyymm_DistPrice(self, today, good_list, BillNumber, CategoryCodes, sqlsv_gbk):
        flag = 0
        sql = f"""insert into [000].tb{today[0:6]}_DistPrice(BillNumber,GoodsCode,DeptType,CategoryItemCode,DeptCode,
                        PurchPrice,SalePrice,MaxSalePrice,MinSalePrice,PriceMode,DistPriceRate,DistPrice,IniPriceMode,
                        IniDistPriceRate,IniDistPrice,IsDetail)
                select BillNumber,GoodsCode,DeptType,CategoryItemCode,DeptCode,
                        PurchPrice,SalePrice,MaxSalePrice,MinSalePrice,PriceMode,DistPriceRate,DistPrice,IniPriceMode,
                        IniDistPriceRate,IniDistPrice,IsDetail from (values"""
        try:
            for good in good_list:
                for CategoryCode in CategoryCodes:
                    sql += f"""('{BillNumber}',  '{good.goodscode}', 0, '0000', '{CategoryCode[0]}', {good.purchprice},
                        {good.saleprice}, 0, 0, {good.psjjtype}, {self.int_zero(good.jdrate)}, {self.int_zero(good.psj)}, 
                        0, 0, 0, 1),"""
                    flag = 1
            if flag == 1:
                sql = sql[:sql.rfind(',')] + """) as tl(BillNumber,GoodsCode,DeptType,CategoryItemCode,DeptCode,
                            PurchPrice,SalePrice,MaxSalePrice,MinSalePrice,PriceMode,DistPriceRate,DistPrice,IniPriceMode,
                            IniDistPriceRate,IniDistPrice,IsDetail)"""
                sqlsv_gbk.executeNoSet(sql)
        except Exception as e:
            print(sql)
            print(e)

    # 合同定义
    def insert_tbyyyymm_ConGoodsBill(self, today, BillNumber, RepairSignID, good, sqlsv, pricebilltype=0, djtype=0):
        ManageMode = sqlsv.execute(f"""select ManageMode from [000].TBCONTRACT 
                                                where contractnumber = '{good.cntcode}'
                                                and  RepairSignID = '{RepairSignID}' """)[0][0]
        sql = f"""insert into [000].tb{today[0:6]}_ConGoodsBill
                (BillNumber,ContractGoodsType,ContractNumber,SupplierCode,RepairSignID,ChargeItemID,ContractGoodsBillCate,
                ManageMode,IsExcute,buildDate,BuildManCode,BuildManName,ModifyDate,ModifyManCode,ModifyManName) 
            values('{BillNumber}',{pricebilltype},'{good.cntcode}','{good.suppercode}','{RepairSignID}',0,'{djtype}',
                    '{ManageMode}',0,'{today}','{employeecode}','{employeename}','{today}','{employeecode}',
                    '{employeename}')"""
        try:
            sqlsv.executeNoSet(sql)
            return True
        except Exception as e:
            # 断开重连，释放资源
            sqlsv.reconn()
            print(e)
            return False

    # 合同商品
    def insert_tbyyyymm_ConGoodsDetail(self, today, conBill, conRepid, result_set_gd, sqlsv):
        InsideID = 1
        flag = 0
        sql = f"""insert into [000].tb{today[0:6]}_ConGoodsDetail
                        (BillNumber,InsideID,ContractNumber,RepairSignID,DetailType,GoodsCode,SpecimenSaleMoney,
                            PriceCompensaType,PriceCompDate) 
                    select BillNumber,InsideID,ContractNumber,RepairSignID,DetailType,GoodsCode,SpecimenSaleMoney,
                            PriceCompensaType,PriceCompDate from (values"""
        for good in result_set_gd:
            sql += f"""('{conBill.get(good.cntcode)}','{InsideID}','{good.cntcode}',{conRepid.get(good.cntcode)},
                        '0','{good.goodscode}',0,0,''),"""
            InsideID += 1
            flag = 1
        try:
            if flag == 1:
                sql = sql[:sql.rfind(',')] + """) as tl(BillNumber,InsideID,ContractNumber,RepairSignID,DetailType,GoodsCode,SpecimenSaleMoney,
                            PriceCompensaType,PriceCompDate)"""
                sqlsv.executeNoSet(sql)
                return True
            return False
        except Exception as e:
            # 断开重连，释放资源
            sqlsv.reconn()
            print(e)
            return False

    # 合同商品
    def insert_tbyyyymm_DeptConGoods(self, today, conBill, result_set_gd, nodes, sqlsv):
        MainGoodsID = 1
        InsideID = 1
        flag = 0
        sql = f"""insert into [000].tb{today[0:6]}_DeptConGoods
                (BillNumber,MainGoodsID,InsideID,DeptType,CategoryItemCode,DeptCode,PriceMode,PurchPrice,
                 WithHoldingRates,MaxPurchPrice,YPurchPrice,YHighPurchPrice) 
                select BillNumber,MainGoodsID,InsideID,DeptType,CategoryItemCode,DeptCode,PriceMode,PurchPrice,
                WithHoldingRates,MaxPurchPrice,YPurchPrice,YHighPurchPrice from (values"""
        for good in result_set_gd:
            for node in nodes:
                sql += f"""('{conBill.get(good.cntcode)}','{MainGoodsID}','{InsideID}','{node[0]}','{node[1]}','{node[2]}','0',
                        {good.purchprice}, 0, 0,{good.purchprice},0),"""
                flag = 1
                InsideID += 1
            MainGoodsID += 1

        try:
            if flag == 1:
                sql = sql[:sql.rfind(',')] + """) as tl(BillNumber,MainGoodsID,InsideID,DeptType,CategoryItemCode,DeptCode,PriceMode,PurchPrice,
                                    WithHoldingRates,MaxPurchPrice,YPurchPrice,YHighPurchPrice)"""
                sqlsv.executeNoSet(sql)
                return True
            return False
        except Exception as e:
            # 断开重连，释放资源
            sqlsv.reconn()
            print(e)
            return False

    def int_zero(self, value):
        if value == "" or value is None:
            return 0
        return value

    def createGoodsCode(self, today, good, sqlsv_gbk):
        GOODSCATELEN = 4
        GOODSLEN = 4
        ym = datetime.strptime(today[0:6], '%Y%m')
        day = timedelta(days=1)
        ym = (ym - day).strftime('%Y%m')
        sql = f"""select max(goodscode) from(
                                select ISNULL(max(CAST(goodscode as bigint) + 1), 
                                    '{good.categorycode[0:GOODSCATELEN] + '1'.rjust(GOODSLEN, '0')}') goodscode
                                from [000].tbGoods
                                where goodscode like '{good.categorycode[0:GOODSCATELEN]}%' 
                                and len(goodscode) = {GOODSCATELEN + GOODSLEN}
                                union all
                                    select max(CAST(goodscode as bigint) + 1) goodscode from "000".tb{today[0:6]}_Goods a
                                where goodscode like '{good.categorycode[0:GOODSCATELEN]}%' 
                                    and len(goodscode) = {GOODSCATELEN + GOODSLEN}
                                    and exists (select 1 from [000].tb{today[0:6]}_PRICEBILL b where a.billnumber = b.billnumber
                                                and b.IsExecute  = 0)
                                union all
                                select max(CAST(goodscode as bigint) + 1) goodscode from "000".tb{ym}_Goods a
                                    where goodscode like '{good.categorycode[0:GOODSCATELEN]}%' 
                                    and len(goodscode) = {GOODSCATELEN + GOODSLEN}
                                    and exists (select 1 from [000].tb{ym}_PRICEBILL b where a.billnumber = b.billnumber
                                                and b.IsExecute  = 0) ) a """
        result = sqlsv_gbk.execute(sql)
        # 避免品类下没有商品存在，生成空值，造成primary key duplicate
        if result[0][0]:
            return result[0][0]
        else:
            return good.categorycode[0:GOODSCATELEN] + '1'.rjust(GOODSLEN, '0')

    def createbarCode(self, today, good, sCodeType, sqlsv, min_barcode):
        CUSTBARCODEPRIX = '22'
        WEIGHTBARCOCEPREFIX = '7'
        ym = datetime.strptime(today[0:6], '%Y%m')
        day = timedelta(days=1)
        ym = (ym - day).strftime('%Y%m')
        tablename_last = ym
        # 条码类型
        self.sCodeType = sCodeType
        # Excel中条码没有填写
        if good.basebarcode == "":
            # 非散称商品
            if good.mesureproperty == "0":
                # 只要商品编码不重复，条码就不重复
                # 去除最后一位校验位，一共12位，头部2位
                temp_code = CUSTBARCODEPRIX + good.goodscode.rjust(10, '0')
                return self.sNewCode(temp_code, self.sCodeType)
            # 计量或散称商品
            else:
                # 条码开头
                barhead = WEIGHTBARCOCEPREFIX
                sql = f"""select barcode 
                        from [000].tbPackBarCode where barcode like '{barhead}%' and len(barcode) = 7
                        union 
                        select barcode from "000".tb{today[0:6]}_packbar  where barcode like '{barhead}%'
                        union
                        select barcode from "000".tb{tablename_last}_packbar 
                        where barcode like '{barhead}%' """
                barcode_list = sqlsv.execute(sql)
                barcode_list = [each[0] for each in barcode_list]
                if not min_barcode:
                    count = min(barcode_list)
                else:
                    count = min_barcode
                while True:
                    if count in barcode_list:
                        count = str(int(count) + 1)
                    else:
                        return count
        return good.basebarcode

    def sNewCode(self, sCode, sCodeType):
        iCodeLength = 8  # 需要生成编码长度
        sSubCode = ""  # 按需要生成的编码长度，将传入的sCode进行截取
        sNcode = ""  # 返回带校验位的编码
        iSsum = 0  # 单数位和
        iDsum = 0  # 偶数位的和
        iSum = 0  # 总和
        iX = 0  # 校验位
        if sCodeType == "ena13":
            iCodeLength = 12
            sSubCode = sCode[0:iCodeLength]
        if sCodeType == "itf14":
            iCodeLength = 13
            sSubCode = sCode[0:iCodeLength]
        # 将字符串倒序组合
        sSubCode = sSubCode[::-1]
        # 计算单位数 和偶数位的和
        for i in range(0, len(sSubCode)):
            if i % 2 == 0:
                iDsum += int(sSubCode[i])
            if i % 2 == 1:
                iSsum += int(sSubCode[i])
        # 编码计算 偶数位和 *3
        iSum = iDsum * 3
        # 偶数和*3 + 奇数位 和
        iSum += iSsum
        # 计算校验位,用10 减去 结果的ge位数字
        iX = 10 - (iSum % 10)
        # 为保证校验位的位数为一
        iX = iX if iX != 10 else 0
        # 将校验位和编码组合到一起，
        sNcode = sCode[0: iCodeLength] + str(iX)
        # 返回编码
        return sNcode

    def getSCcode(self, basebarcode, sqlsv_gbk):
        count = int(basebarcode)
        while True:
            sql = f""" select barcode from [000].tbPackBarCode where barcode like '7%' 
                    and BarCode = '{count}' """
            barcode = sqlsv_gbk.execute(sql)
            if not barcode:
                return str(count)
            count += 1

    def rellbackExcel(self, result_set):
        # result_set 为字典，行号:(商品,[门店])

        pass


# ie = InDba()
# sqlsv_gbk = Sqlserve('192.168.8.95', 'sa', '!QAZ2wsx', 'BZ_HQ')
# # print(ie.createBillno(sqlsv_gbk))
# # print(ie.goodIsExists("111111", sqlsv_gbk))
# print(ie.getSCcode(sqlsv_gbk))
# print(vars())
# print(globals())
