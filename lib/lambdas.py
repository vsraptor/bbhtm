import math

def mod(x,m) : return x % m

def is_prime(x) : return int( all([(x % j) for j in range(2, int(x**0.5)+1)]) and x > 1 )

def is_fibonacci(x):
    phi = 0.5 + 0.5 * math.sqrt(5.0)
    a = phi * x
    return int( x == 0 or abs(round(a) - a) < 1.0 / x )

