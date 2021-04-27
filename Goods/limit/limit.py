from datetime import datetime, timedelta


class TimeLimit:
    def __init__(self, enddate):
        self.enddate = datetime.strptime(enddate, '%Y%m%d')
        self.today = datetime.today()

    def getdays(self):
        return (self.enddate - self.today).days

    def isOk(self):
        if self.getdays() < 0:
            return True
        else:
            return False


