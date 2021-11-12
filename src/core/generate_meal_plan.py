import random
import os
import requests
from requests.structures import CaseInsensitiveDict
from core.protein import Protein
from core.recipe import Recipe

# For program use
hard_recipes = []
medium_recipes = []
easy_recipes = []
randomize_results = []


def get_todays_meal():
    url = os.environ.get('MEALIE_API') + "/api/meal-plans/today"

    headers = CaseInsensitiveDict()
    headers["Accept"] = "application/json"
    headers["Authorization"] = "Bearer " + os.environ.get('MEALIE_API_TOKEN')
    resp = requests.get(url, headers=headers)
    return resp.json()


def check_protein_in_tags(tags):
    if "chicken" in (string.lower().strip() for string in tags):
        return Protein.CHICKEN
    elif "beef" in (string.lower().strip() for string in tags):
        return Protein.BEEF
    elif "pork" in (string.lower().strip() for string in tags):
        return Protein.PORK
    elif "fish" in (string.lower().strip() for string in tags):
        return Protein.FISH


def parse_meals_from_mealie_api():
    all_dinner_meals = requests.get(os.environ.get('MEALIE_API') + "/api/categories/dinner")
    for meal in all_dinner_meals.json()['recipes']:
        if "hard" in (string.lower() for string in meal['tags']):
            hard_recipes.append(Recipe(meal['name'].strip(), check_protein_in_tags(
                meal['tags']), os.environ.get('MEALIE_API') + "/recipe/" + meal['slug']))
        elif "medium" in (string.lower() for string in meal['tags']):
            medium_recipes.append(Recipe(meal['name'].strip(), check_protein_in_tags(
                meal['tags']), os.environ.get('MEALIE_API') + "/recipe/" + meal['slug']))
        elif "easy" in (string.lower() for string in meal['tags']):
            easy_recipes.append(Recipe(meal['name'].strip(), check_protein_in_tags(
                meal['tags']), os.environ.get('MEALIE_API') + "/recipe/" + meal['slug']))


def is_there_too_many_of_one_protein():
    pork_counter = 0
    fish_counter = 0
    chicken_counter = 0
    beef_counter = 0

    for recipe in randomize_results:
        if recipe.protein == Protein.CHICKEN:
            chicken_counter += 1
        elif recipe.protein == Protein.BEEF:
            beef_counter += 1
        elif recipe.protein == Protein.FISH:
            fish_counter += 1
        elif recipe.protein == Protein.PORK:
            pork_counter += 1

    if pork_counter > 3 or fish_counter > 3 or beef_counter > 3 or chicken_counter > 3:
        return True
    else:
        return False


def choose_recipes():
    randomize_results.append(random.choice(hard_recipes))
    for recipe in random.sample(medium_recipes, 3):
        randomize_results.append(recipe)
    for recipe in random.sample(easy_recipes, 2):
        randomize_results.append(recipe)
    if is_there_too_many_of_one_protein():
        randomize_results.clear()


def get_random_recipes():
    parse_meals_from_mealie_api()
    while randomize_results == []:
        choose_recipes()
    return randomize_results
