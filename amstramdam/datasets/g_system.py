import pandas
from .codes import read_codefile, read_region_file


countries = read_codefile("data/country_codes.txt")
continents, continent_composition = read_region_file("data/continents+countries.txt")


def generate_g_datasets():
    datasets = [
        dict(group="Test", maps=[
            dict(map_id="gIT", name=countries["IT"], gtype="gcountry", countries="IT", method="from_g"),
            dict(map_id="gEU", name=continents["EU"], gtype="gcountries", countries=continent_composition["EU"], method="from_g")
        ])
    ]
    return datasets[0]