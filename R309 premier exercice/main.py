# Ceci est un script Python d'exemple.

# Appuyez sur Maj+F10 pour l'exécuter ou remplacez-le par votre code.
# Appuyez deux fois sur Maj pour rechercher partout des classes, fichiers, fenêtres d'outils, actions et paramètres.

def print_hi(name):
    # Utilisez un point d'arrêt dans la ligne de code ci-dessous pour déboguer votre script.
    print(f'Salut, {name}')  # Appuyez sur Ctrl+F8 pour basculer le point d'arrêt.

def divEntier(x: int, y: int) -> int:
        if x < y:
            return 0
        else:
            x = x - y
            return divEntier(x, y) + 1

# Appuyez sur le bouton vert dans la marge pour exécuter le script.
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
