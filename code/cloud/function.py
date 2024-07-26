def string_to_method(name):
    if "square" in name.lower() :
        retval = square
    elif "polynomial" in name.lower():
        retval = polynomial_3
    elif "division" in name.lower():
        retval = division
    elif "hyperbolic" in name.lower():
        retval = division_2
    else:
        retval = linear
    return retval

def square(x, a, b, c):
    return a * x ** 2 + b * x + c

def polynomial_3(x, a, b, c, d):
    return a * x ** 3 + b * x ** 2 + c * x + d

def division(x, a, b, c, d):
    return (a * x + b) / (c * x + d)

def linear(x, a, b):
    return a * x + b

def division_2(x, a, b, c, d, e, f, g):
    return (a * x ** 3 + b * x ** 2 + c * x + d) / (e * x ** 2 + f * x + g)