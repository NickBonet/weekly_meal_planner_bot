"""Baic representation of a recipe from mealie JSON"""


class Recipe:
    """Represents the fields from Mealie recipes that we want"""

    def __init__(self, name, protein, recipe_url):
        self.name = name
        self.protein = protein
        self.recipe_url = recipe_url

    def __repr__(self):
        return self.name
