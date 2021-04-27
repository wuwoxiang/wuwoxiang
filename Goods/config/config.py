class NodeConfig:
    def __init__(self, filepath="./node.ini"):
        self.filepath = filepath
        self.node_dir = {}

    def getNodes(self):
        with open(self.filepath, 'rb') as f:
            while True:
                s = f.readline().decode("UTF8")
                if s and s != "":
                    s = s.replace(',', '').replace(' ', '').replace(';', '').replace('；', '').replace('\t', '')
                    nodename, nodecode = s.split('=')
                    nodename = nodename.replace(',', '').replace(' ', '').replace(';', '').replace('；', '').replace('\t', '')
                    self.node_dir[nodename] = nodecode.replace('\n', '').replace('\r', '')
                else:
                    break
        return self.node_dir


class DataConfig:
    def __init__(self, filepath="./data.ini"):
        self.filepath = filepath
        self.data_dir = {}

    def getDatacf(self):
        with open(self.filepath, 'rb') as f:
            while True:
                s = f.readline().decode("UTF8")
                if s and s != "":
                    if '=' in s:
                        s = s.replace(',', '').replace(' ', '').replace(';', '').replace('；', '')
                        key, value = s.split('=')
                        self.data_dir[key] = value.replace('\n', '').replace('\r', '')
                    else:
                        continue
                else:
                    break
        return self.data_dir
