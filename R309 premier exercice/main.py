# This is a sample Python script.

# Press Maj+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.

def divEntier(x: int, y: int) -> int:
        if x < y:
            return 0
        else:
            x = x - y
            return divEntier(x, y) + 1

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print (divEntier(50,4))

    try :
        a = int(input('a'))
        b = int(input('b'))
        print(divEntier(a,b))


    except RecursionError:
        if b < 0:
            print("B doit être positif")
        elif b ==0:
            print("B ne peut pas être égal à 0")
    except ValueError:
        print("Le nombre doit être un nombre entier")
    else:
        divEntier(a,b)



# See PyCharm help at https://www.jetbrains.com/help/pycharm/
