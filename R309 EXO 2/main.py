def fichier(f):
    #file = open(f, "r")
    #print(file.read())
    with open('toto.txt', 'r') as f:
        for l in f:
            l = l.rstrip("\n\r")
            print(l)
def creation(f):
    file = open(f, "x")
    file.write("Le fichier a bien été crée")


if __name__ == '__main__':
    try:
        f = "toto.txt"
        fichier(f)
        creation("titi.txt")

    except FileNotFoundError:
        print("Le fichier n'a pas été trouvé")

    except IOError:
        print("Le fichier ne peut pas être ouvert / lu")

    except FileExistsError:
        print("Le fichier existe déjà")

    except PermissionError:
        print("Vous n'avez pas la permission d'ouvrir le fichier")