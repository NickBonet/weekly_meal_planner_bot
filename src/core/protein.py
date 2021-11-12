"""Protein enum for recipe data"""
from enum import Enum


class Protein(Enum):
    """Represents the type of protein used in a recipe"""
    CHICKEN = 1
    BEEF = 2
    PORK = 3
    FISH = 4
