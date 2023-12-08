def fichier(f):
    # Fonction pour lire et afficher le contenu d'un fichier
    # Utilise le gestionnaire de contexte 'with' pour garantir la fermeture automatique du fichier
    with open(f, 'r') as file:
        # Parcourt chaque ligne du fichier
        for line in file:
            # Supprime les caractères de nouvelle ligne (\n ou \r) à la fin de chaque ligne
            line = line.rstrip("\n\r")
            # Affiche la ligne
            print(line)


def creation(f):
    # Fonction pour créer un nouveau fichier
    # Utilise le mode 'x' pour créer le fichier uniquement s'il n'existe pas déjà
    file = open(f, "x")
    # Écrit une ligne dans le fichier nouvellement créé
    file.write("Le fichier a bien été créé")


if __name__ == '__main__':
    try:
        # Nom du fichier à traiter
        f = "toto.txt"

        # Appelle la fonction pour lire et afficher le contenu du fichier
        fichier(f)

        # Appelle la fonction pour créer un nouveau fichier
        creation("titi.txt")

    except FileNotFoundError:
        print("Le fichier n'a pas été trouvé")

    except IOError:
        print("Le fichier ne peut pas être ouvert / lu")

    except FileExistsError:
        print("Le fichier existe déjà")

    except PermissionError:
        print("Vous n'avez pas la permission d'ouvrir le fichier")
