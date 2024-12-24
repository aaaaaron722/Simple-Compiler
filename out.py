import sys
print("It's a simple language called HelloWorld")
print("Here is example")
x = 11
if x>10:
    if x<15:
        print("x greater than 10 but less than 15")
        if x>12:
            print("x larger than 12")
        else:
            print("x less than 12")
while x<10:
    print("x less than 10")
a = 5
y = 5
def add(a, y):
    c = a+y
    print("infunction")
    return c
print(add(a, y))
print(a)
