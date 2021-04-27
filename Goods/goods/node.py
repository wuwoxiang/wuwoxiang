from opera.operas import Opera
from config.config import NodeConfig


class Node(Opera, NodeConfig):
    # __node = {'海宁': '1007', '板4': '1041', '金宝': '1048', '华龙仓': '1052', '连云': '1014', '高公': '1016', '许庄': '1017',
    #           '华府': '1023', '板2': '1024', '宁海': '1025', '马山': '1029', '太平': '1030', '中正': '1038', '津华苑': '1042',
    #           '极美苑': '1044', '西大岭': '1049', '建设': '1002', '朝阳': '1010', '华阳': '1011', '花果山': '1015', '东一': '1031',
    #           '开3': '1036', '南城': '1037', '朐2': '1039', '中大街': '1043', '鹰游': '1045', '中云': '1054', '新桥': '1003',
    #           '南极': '1005', '市民': '1006', '杰瑞': '1012', '万润': '1013', '龙河': '1018', '朝中': '1028', '小村': '1046',
    #           '中学': '1047', '配中': '0000'
    #           }
    nodedir = NodeConfig()
    __node = nodedir.getNodes()
    __slots__ = {'__nodecode', "__isgood"}

    def __init__(self):
        self.__nodecode = ""
        self.__isgood = 1

    @property
    def nodecode(self):
        return self.__nodecode

    @nodecode.setter
    def nodecode(self, value):
        value = self.valtostring(value)
        self.__nodecode = self.__node.get(value)
        if self.__nodecode is None:
            self.__nodecode = ""

    @property
    def isgood(self):
        return self.__isgood

    @isgood.setter
    def isgood(self, value):
        if value in (0, 1):
            self.__isgood = value
        else:
            self.__isgood = 1



# nd = Node()
# nd.nodecode = '海dfd宁'
# nd.isgood = 0
# print(nd.nodecode, nd.isgood)
