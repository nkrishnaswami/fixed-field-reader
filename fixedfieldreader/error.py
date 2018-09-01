class Error(BaseException):
    def __init__(self, msg):
        super().__init__(msg)


class RowError(Error):
    def __init__(self, line_num, msg):
        super().__init__("Error at line {}: {}".format(line_num, msg))
        self.line_num = line_num
    
class RowLengthError(RowError):
    def __init__(self, line_num, msg, exp_len, act_len):
        super().__init__(line_num, msg)
        self.exp_len = exp_len
        self.act_len = act_len
    

class InitError(Error):
    def __init__(self, msg):
        super().__init__("Initialization Error: {}".format(msg))
