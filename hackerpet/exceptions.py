from typing import Any


class IllegalValue(ValueError):
    """Exception raised when an unexpected status value is received"""

    message: str

    def __init__(self, cls: type, value_provided: Any):
        """provide the enum and the illegal value"""

        self.message = f"illegal value provided for {cls.__name__}: {value_provided}"
        super().__init__(self.message)


class OutOfRange(IndexError):
    """Exception raised if a value is out of range from expected"""

    message: str

    def __init__(self, name: str, lower: int, upper: int, found: int):
        self.message = (
            f"expected value {name} to be "
            f"in range [{lower}, {upper}], but found {found}"
        )
        super().__init__(self.message)

    @staticmethod
    def test_range(name: str, lower: int, upper: int, found: int):
        """helper function for testing if a value is out of range"""
        if found < lower or found > upper:
            raise OutOfRange(name, lower, upper, found)
