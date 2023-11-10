class Article:
    TVA = 0.20  # Taux de TVA (20%)

    def __init__(self, nom, code_barre, prix_ht):
        if not isinstance(nom, str) or not isinstance(code_barre, str) or not isinstance(prix_ht, (int, float)) or prix_ht <= 0:
            raise ValueError("Les attributs de l'article ne sont pas valides.")
