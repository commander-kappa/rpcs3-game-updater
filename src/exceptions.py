class HashDoesNotMatch(Exception):
    def __init__(
            self,
            expected:str,
            calculated:str,
            file_type:str = 'File'
    ):
        self.file_type = file_type
        self.message = f"{file_type} hashes do not match!\nExpected:   {expected}\nCalculated: {calculated}"
        super().__init__(self.message)

class CertNotFound(FileNotFoundError):
    def __init__(
            self,
            fileName:str
    ):
        self.message = f"Certificate {fileName} not found."
        super().__init__(self.message)

class SerialNumberError(ValueError):
    def __init__(
            self,
            serial:str
    ):
        self.message = f"Serialnumber {serial} invalid."
        super().__init__(self.message)

