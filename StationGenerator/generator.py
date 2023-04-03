import math

MAX_LEVEL = int(input("MAX LEVEL: "))

def is_prime(n):
    if n <= 1:
        return False
    if n % 2 == 0:
        return n == 2

    max_div = math.floor(math.sqrt(n))
    for i in range(3, 1 + max_div, 2):
        if n % i == 0:
            return False
    return True

result = []
for i in range (1, MAX_LEVEL+1):
    if is_prime(i):
        result.append(
            {
                "number": i,
                "material": "",
                "count": 0
            }
        )
print(result)