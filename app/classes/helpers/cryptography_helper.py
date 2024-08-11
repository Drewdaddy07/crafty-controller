import base64


class CryptoHelper:
    def __init__(self, helper):
        self.helper = helper
        self.test = "hello world"

    def say_hello_world(self):
        print(self.test)

    @staticmethod
    def bytes_to_b64(input_bytes: bytes) -> str:
        return base64.b64encode(input_bytes).decode("UTF-8").rstrip("\n")
