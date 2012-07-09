class MalformedStructure(Exception):
    def __init__(self,value):
        super(MalformedStructure, self).__init__()
        self.value = value
    def __str__(self):
        return repr(self.value)
