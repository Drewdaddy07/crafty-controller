import base64


class CryptoHelper:
    def __init__(self, helper):
        self.helper = helper
        self.test = "hello world"

    def say_hello_world(self):
        print(self.test)

    @staticmethod
    def bytes_to_b64(input_bytes: bytes) -> str:
        """
        Converts input bytes to base64 encoded string.

        Args:
            input_bytes: Input bytes for conversion.

        Returns: String of base64 encoded bytes.

        """
        # base64.b64encode(input_bytes).decode("UTF-8") appends a trailing new line.
        # That newline is getting pulled off of the string before returning it.
        return base64.b64encode(input_bytes).decode("UTF-8").rstrip("\n")

    @staticmethod
    def b64_to_bytes(input_str: str) -> bytes:
        """
        Converts base64 encoded string to bytes.

        Args:
            input_str: Base64 bytes encodes as a string.

        Returns: Bytes from base64 encoded string.

        """
        return base64.b64decode(input_str)

    @staticmethod
    def bytes_to_hex(input_bytes: bytes) -> str:
        """
        Converts input bytes to hex encoded string.

        Args:
            input_bytes: Bytes to be encoded as hex string.

        Returns: Bytes encoded as hex string.

        """
        return input_bytes.hex()
