def adder(n):
    def inner(x):
        print(f" n {n}")
        print(f" x {x}")
        return x + n

    return inner


add_five = adder(5)
add_ten = adder(10)

print(add_five())  # Output: 8
print(add_five(3))  # Output: 8
print(add_ten(3))  # Output: 13
