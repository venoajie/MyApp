def adder(n):
    def inner(x):
        print(f" n {n}")
        print(f" x {x}")
        return x + n

    return inner


add_five = adder(5)
add_ten = adder(10)

print(add_five(5))  # Output: 8
print(add_five(3))  # Output: 8
print(add_ten(3))  # Output: 13

f=['a','b','c','d']
syarat=['a','b','d']
res= [o for o in f if o in syarat]
print(res)

from strategies import entries_exits

strategies = entries_exits.strategies

strategy_attr = [o['strategy'] for o in strategies if o["contribute_to_hedging"] == True]

print(strategy_attr)
