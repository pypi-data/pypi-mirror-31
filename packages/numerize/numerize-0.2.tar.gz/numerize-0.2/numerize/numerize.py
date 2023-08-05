import sys
from decimal import Decimal

def round_num(n):
    '''
    Round number to 2 decimal places
    For example:
    10.0 -> 10
    10.222 -> 10.22
    '''
    return n.to_integral() if n == n.to_integral() else round(n.normalize(), 2)

def drop_zero(n):
    '''
    Drop trailing 0s
    For example:
    10.100 -> 10.1
    '''
    n = str(n)
    return n.rstrip('0').rstrip('.') if '.' in n else n

def numerize(n):
    '''
    Converts numbers like:
    1,000 -> 1K
    1,000,000 -> 1M
    1,000,000,000 -> 1B
    1,000,000,000,000 -> 1T
    '''
    n = Decimal(n)
    if n < 1000:
        return str(drop_zero(round_num(n)))
    elif n >= 1000 and n < 1000000:
        if n % 1000 == 0:
            return str(int(n / 1000)) + "K"
        else:
            n = n / 1000
            return str(drop_zero(round_num(n))) + "K"
    elif n >= 1000000 and n < 1000000000:
        if n % 1000000 == 0:
            return str(int(n / 1000000)) + "M"
        else:
            n = n / 1000000
            return str(drop_zero(round_num(n))) + "M"
    elif n >= 1000000000 and n < 1000000000000:
        if n % 1000000000 == 0:
            return str(int(n / 1000000000)) + "B"
        else:
            n = n / 1000000000
            return str(drop_zero(round_num(n))) + "B"
    elif n >= 1000000000000 and n < 1000000000000000:
        if n % 1000000000000 == 0:
            return str(int(n / 1000000000000)) + "T"
        else:
            n = n / 1000000000000
            return str(drop_zero(round_num(n))) + "T"

if __name__ == '__main__':
    number = sys.argv[1]
    # number = 1234567.12
    numerize = numerize(number)
    print(type(numerize))
    print(numerize)
