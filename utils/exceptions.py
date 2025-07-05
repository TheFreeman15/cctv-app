class Error(Exception):
    '''
    Custom exception class to have a flexible control over exceptions raised by us
    '''
    def __init__(self,status_code,details,actualErrorMessage=None):
        self.status_code = status_code
        self.details = details
        self.actualErrorMessage = actualErrorMessage

        if self.actualErrorMessage == None:
            self.actualErrorMessage = self.details