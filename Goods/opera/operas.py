

class Opera:
    def valtostring(self, value):
        if value is not None:
            if not isinstance(value, str):
                value = str(value)
            # 去掉制表符，和回车符
            value = value.replace('\t', '').replace('\n', ' ')
            return value
        return ""

    def valtofloat(self, value):
        if value is not None:
            if isinstance(value, str):
                if value.isnumeric():
                    return float(value)
                if value.count(".") == 1:
                    return float(value)
            elif isinstance(value, int) or isinstance(value, float):
                return value
        return ""

    def countzj(self, st):
        count = 0
        for ch in st:
            if not ('\x00' <= ch <= '\xff'):
                count += 2
            else:
                count += 1
        return count

    def allTrue(self, ls):
        for each in ls:
            each = Opera().valtostring(each)
            if each == '':
                return False
        return True
