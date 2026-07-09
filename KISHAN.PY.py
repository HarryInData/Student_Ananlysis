a=int(input("enter a number to chek it is PRIME or NOT  = "))
if (a<=1):
    print("It is Not a prime")
else:
    for i in range (2,a):
        if (a%2==0):
            print("it is not a prime number ")
        else :
            print(" prime number")
