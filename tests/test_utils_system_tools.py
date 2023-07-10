from src.utilities import system_tools

@system_tools.exception_handler
def test_divide(x, y):
    result = x / y
    return result
test_divide(10, 0)  





