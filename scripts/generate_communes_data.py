#!/usr/bin/env python3
"""
generate_communes_data.py — Générateur des 196 communes de l'Essonne
=====================================================================
Produit data/communes_input.json pour injection via sync_knowledge.py.
NE lit JAMAIS COMPILATION_AVEC_DATES.txt.
"""

import json
import re
import sys
from pathlib import Path
from unicodedata import normalize, category

ROOT = Path(__file__).parent.parent


def slugify(name: str) -> str:
    """Transforme un nom de commune en slug URL-safe."""
    # Normaliser les accents
    nfkd = normalize("NFKD", name)
    ascii_str = "".join(c for c in nfkd if category(c) != "Mn")
    ascii_str = ascii_str.lower()
    # Remplacer apostrophes et tirets
    ascii_str = re.sub(r"['’]", "-", ascii_str)
    ascii_str = re.sub(r"[\s\-]+", "-", ascii_str)
    # Supprimer les caractères non alphanumériques sauf tirets
    ascii_str = re.sub(r"[^a-z0-9\-]", "", ascii_str)
    return ascii_str.strip("-")


def priorite(pop: int) -> str:
    if pop >= 20000: return "haute"
    if pop >= 3000:  return "moyenne"
    return "basse"


def volume(pop: int) -> int:
    if pop >= 50000: return 400
    if pop >= 30000: return 250
    if pop >= 20000: return 180
    if pop >= 10000: return 120
    if pop >= 5000:  return 70
    if pop >= 2000:  return 35
    if pop >= 1000:  return 20
    return 10


def make_commune(name, insee_suffix, cp, zone, pop, lat, lng, assainissement, spanc_key, adjacentes):
    slug = slugify(name)
    cp_list = [cp] if isinstance(cp, str) else cp
    cp_display = cp_list[0]
    pr = priorite(pop)
    svc_label = "Débouchage" if zone == "nord" else "Vidange fosse septique"

    return {
        "slug": slug,
        "name": name,
        "insee": f"91{insee_suffix}",
        "cp": cp_list,
        "zone": zone,
        "population": pop,
        "geo": {"lat": lat, "lng": lng},
        "assainissement": assainissement,
        "spanc": spanc_key,
        "adjacentes": adjacentes,
        "seo": {
            "priorite": pr,
            "volumeEstimeMensuel": volume(pop),
            "titleDebouchage": f"{svc_label} {name} ({cp_display}) - Artisans Agréés | Guide 91",
            "metaDescription": (
                f"Trouvez un artisan agréé pour votre assainissement à {name} ({cp_display}). "
                f"Intervention rapide 24h/7j. Devis gratuit. Professionnels certifiés en Essonne."
            )
        },
        "artisans": []
    }


# ── Données sources ──────────────────────────────────────────────────────────
# Format: (name, insee_suffix, cp, zone, pop, lat, lng, assainissement, spanc, [adjacentes])

RAW_COMMUNES = [
    # ── NORD ESSONNE ── (réseau collectif — services: débouchage, curage, inspection)
    ("Arpajon",               "026", "91290", "nord", 10500, 48.5932, 2.2478, "collectif",     None, ["saint-germain-les-arpajon","egly","la-norville","breuillet","marolles-en-hurepoix"]),
    ("Athis-Mons",            "027", "91200", "nord", 33500, 48.7062, 2.3869, "collectif",     None, ["juvisy-sur-orge","viry-chatillon","morangis","savigny-sur-orge"]),
    ("Ballainvilliers",       "042", "91160", "nord",  5000, 48.6567, 2.2844, "collectif",     None, ["longjumeau","massy","chilly-mazarin","saulx-les-chartreux"]),
    ("Ballancourt-sur-Essonne","037","91610", "nord",  9000, 48.5389, 2.3900, "collectif",     None, ["itteville","mennecy","vert-le-petit"]),
    ("Bondoufle",             "076", "91070", "nord", 11000, 48.6100, 2.4736, "collectif",     None, ["evry-courcouronnes","lisses","ris-orangis"]),
    ("Boissy-sous-Saint-Yon", "062", "91790", "nord",  4000, 48.5692, 2.2264, "collectif",     None, ["arpajon","saint-yon","breuillet"]),
    ("Brétigny-sur-Orge",     "087", "91220", "nord", 27000, 48.6045, 2.3048, "collectif",     None, ["saint-germain-les-arpajon","le-plessis-pate","egly","saint-michel-sur-orge"]),
    ("Breuillet",             "093", "91650", "nord",  9000, 48.5680, 2.2150, "collectif",     None, ["arpajon","boissy-sous-saint-yon","la-norville","saint-yon"]),
    ("Brunoy",                "099", "91800", "nord", 27000, 48.6975, 2.5092, "collectif",     None, ["yerres","quincy-sous-senat","varennes-jarcy","montgeron"]),
    ("Bures-sur-Yvette",      "102", "91440", "nord", 10200, 48.6997, 2.1617, "collectif",     None, ["gif-sur-yvette","orsay","les-ulis"]),
    ("Champlan",              "107", "91160", "nord",  4000, 48.6819, 2.2975, "collectif",     None, ["longjumeau","massy","chilly-mazarin"]),
    ("Chilly-Mazarin",        "129", "91380", "nord", 22000, 48.6900, 2.3186, "collectif",     None, ["longjumeau","ballainvilliers","massy","wissous","champlan"]),
    ("Corbeil-Essonnes",      "174", "91100", "nord", 50000, 48.6153, 2.4806, "collectif",     None, ["evry-courcouronnes","ris-orangis","lisses","villabe","saint-germain-les-corbeil"]),
    ("Crosne",                "185", "91560", "nord", 10000, 48.7175, 2.4636, "collectif",     None, ["yerres","montgeron","epinay-sous-senat"]),
    ("Draveil",               "210", "91210", "nord", 30000, 48.6847, 2.4164, "collectif",     None, ["vigneux-sur-seine","soisy-sur-seine","ris-orangis"]),
    ("Égly",                  "197", "91520", "nord",  5000, 48.5761, 2.2544, "collectif",     None, ["arpajon","bretigny-sur-orge","la-norville","saint-germain-les-arpajon"]),
    ("Épinay-sous-Sénart",    "206", "91860", "nord", 14000, 48.6908, 2.5283, "collectif",     None, ["crosne","quincy-sous-senat","yerres"]),
    ("Épinay-sur-Orge",       "207", "91360", "nord",  9500, 48.6547, 2.3117, "collectif",     None, ["savigny-sur-orge","villemoisson-sur-orge","morsang-sur-orge"]),
    ("Étiolles",              "224", "91450", "nord",  3000, 48.6264, 2.4636, "collectif",     None, ["soisy-sur-seine","corbeil-essonnes","saint-germain-les-corbeil"]),
    ("Fleury-Mérogis",        "240", "91700", "nord", 10500, 48.6397, 2.3697, "collectif",     None, ["sainte-genevieve-des-bois","lisses","ris-orangis"]),
    ("Gif-sur-Yvette",        "272", "91190", "nord", 22000, 48.7036, 2.1361, "collectif",     None, ["bures-sur-yvette","orsay","saclay","saint-jean-de-beauregard"]),
    ("Grigny",                "286", "91350", "nord", 30000, 48.6542, 2.3906, "collectif",     None, ["viry-chatillon","ris-orangis","evry-courcouronnes"]),
    ("Igny",                  "307", "91430", "nord", 10000, 48.7378, 2.2272, "collectif",     None, ["gif-sur-yvette","verrieres-le-buisson","palaiseau","bures-sur-yvette"]),
    ("Juvisy-sur-Orge",       "326", "91260", "nord", 14000, 48.6914, 2.3797, "collectif",     None, ["athis-mons","savigny-sur-orge","morsang-sur-orge","viry-chatillon"]),
    ("La Norville",           "339", "91290", "nord",  3000, 48.5764, 2.2208, "collectif",     None, ["arpajon","breuillet","saint-germain-les-arpajon","egly"]),
    ("La Ville-du-Bois",      "654", "91620", "nord",  8000, 48.6292, 2.2658, "collectif",     None, ["nozay","marcoussis","montlhery","linas"]),
    ("Le Coudray-Montceaux",  "144", "91830", "nord",  4000, 48.5731, 2.4875, "collectif",     None, ["corbeil-essonnes","soisy-sur-seine","saint-pierre-du-perray"]),
    ("Le Plessis-Pâté",       "489", "91220", "nord",  4000, 48.5881, 2.2919, "collectif",     None, ["bretigny-sur-orge","egly","marolles-en-hurepoix"]),
    ("Les Ulis",              "692", "91940", "nord", 26000, 48.6834, 2.1650, "collectif",     None, ["palaiseau","bures-sur-yvette","gif-sur-yvette","orsay"]),
    ("Leuville-sur-Orge",     "350", "91310", "nord",  5000, 48.6175, 2.2803, "collectif",     None, ["montlhery","linas","longpont-sur-orge"]),
    ("Linas",                 "353", "91310", "nord",  6500, 48.6317, 2.2528, "collectif",     None, ["montlhery","leuville-sur-orge","marcoussis","la-ville-du-bois"]),
    ("Lisses",                "355", "91090", "nord",  7000, 48.6003, 2.4369, "collectif",     None, ["evry-courcouronnes","corbeil-essonnes","fleury-merogis","bondoufle"]),
    ("Longjumeau",            "356", "91160", "nord", 22000, 48.6942, 2.2981, "collectif",     None, ["massy","chilly-mazarin","ballainvilliers","saulx-les-chartreux","champlan"]),
    ("Longpont-sur-Orge",     "357", "91310", "nord",  6000, 48.6453, 2.2764, "collectif",     None, ["leuville-sur-orge","montlhery","linas"]),
    ("Marcoussis",            "368", "91460", "nord",  7000, 48.6458, 2.2231, "collectif",     None, ["nozay","la-ville-du-bois","linas"]),
    ("Marolles-en-Hurepoix",  "369", "91630", "nord",  6000, 48.5717, 2.2889, "collectif",     None, ["arpajon","le-plessis-pate","cheptainville","leudeville"]),
    ("Mennecy",               "395", "91540", "nord", 12000, 48.5814, 2.4381, "collectif",     None, ["corbeil-essonnes","ballancourt-sur-essonne","vert-le-petit"]),
    ("Montgeron",             "401", "91230", "nord", 24000, 48.7061, 2.4675, "collectif",     None, ["yerres","crosne","vigneux-sur-seine","draveil"]),
    ("Montlhéry",             "402", "91310", "nord",  7000, 48.6228, 2.2736, "collectif",     None, ["linas","leuville-sur-orge","la-ville-du-bois","longpont-sur-orge"]),
    ("Morangis",              "403", "91420", "nord", 13000, 48.7069, 2.3431, "collectif",     None, ["athis-mons","savigny-sur-orge","juvisy-sur-orge","wissous"]),
    ("Morsang-sur-Orge",      "404", "91390", "nord", 22000, 48.6614, 2.3442, "collectif",     None, ["sainte-genevieve-des-bois","saint-michel-sur-orge","savigny-sur-orge","epinay-sur-orge"]),
    ("Morsang-sur-Seine",     "405", "91250", "nord",  5000, 48.6314, 2.4897, "collectif",     None, ["saintry-sur-seine","soisy-sur-seine","saint-germain-les-corbeil"]),
    ("Nozay",                 "459", "91620", "nord",  7000, 48.6578, 2.2158, "collectif",     None, ["marcoussis","la-ville-du-bois","gif-sur-yvette"]),
    ("Ollainville",           "464", "91520", "nord",  5500, 48.5633, 2.2256, "collectif",     None, ["breuillet","arpajon","saint-cheron","boissy-sous-saint-yon"]),
    ("Orsay",                 "471", "91400", "nord", 17000, 48.6994, 2.1875, "collectif",     None, ["gif-sur-yvette","palaiseau","bures-sur-yvette","les-ulis"]),
    ("Quincy-sous-Sénart",    "508", "91480", "nord",  7000, 48.6858, 2.5428, "collectif",     None, ["brunoy","epinay-sous-senat","varennes-jarcy"]),
    ("Ris-Orangis",           "520", "91130", "nord", 26000, 48.6489, 2.4194, "collectif",     None, ["evry-courcouronnes","corbeil-essonnes","grigny","draveil","bondoufle"]),
    ("Saclay",                "534", "91400", "nord",  3500, 48.7236, 2.1678, "collectif",     None, ["gif-sur-yvette","orsay","palaiseau"]),
    ("Sainte-Geneviève-des-Bois","540","91700","nord",38000, 48.6403, 2.3247, "collectif",     None, ["morsang-sur-orge","saint-michel-sur-orge","fleury-merogis","villiers-sur-orge"]),
    ("Saint-Germain-lès-Arpajon","545","91180","nord", 9000, 48.5883, 2.2653, "collectif",     None, ["arpajon","bretigny-sur-orge","la-norville","egly"]),
    ("Saint-Germain-lès-Corbeil","547","91250","nord",10000, 48.6361, 2.5100, "collectif",     None, ["corbeil-essonnes","saintry-sur-seine","morsang-sur-seine"]),
    ("Saint-Michel-sur-Orge", "553", "91240", "nord", 22000, 48.6347, 2.3136, "collectif",     None, ["sainte-genevieve-des-bois","morsang-sur-orge","savigny-sur-orge","bretigny-sur-orge"]),
    ("Saint-Pierre-du-Perray","558", "91280", "nord",  9000, 48.5961, 2.5058, "collectif",     None, ["corbeil-essonnes","le-coudray-montceaux"]),
    ("Saintry-sur-Seine",     "533", "91250", "nord",  3000, 48.6275, 2.5072, "collectif",     None, ["morsang-sur-seine","saint-germain-les-corbeil","corbeil-essonnes"]),
    ("Saulx-les-Chartreux",   "572", "91160", "nord",  8000, 48.6694, 2.2711, "collectif",     None, ["longjumeau","massy","chilly-mazarin","ballainvilliers"]),
    ("Savigny-sur-Orge",      "573", "91600", "nord", 36000, 48.6803, 2.3400, "collectif",     None, ["juvisy-sur-orge","morangis","morsang-sur-orge","saint-michel-sur-orge","epinay-sur-orge"]),
    ("Soisy-sur-Seine",       "596", "91450", "nord",  7000, 48.6403, 2.4728, "collectif",     None, ["draveil","corbeil-essonnes","morsang-sur-seine","saint-germain-les-corbeil"]),
    ("Tigery",                "619", "91250", "nord",  3000, 48.6247, 2.5200, "collectif",     None, ["corbeil-essonnes","saint-germain-les-corbeil"]),
    ("Varennes-Jarcy",        "631", "91480", "nord",  3000, 48.6908, 2.5608, "collectif",     None, ["brunoy","quincy-sous-senat"]),
    ("Vert-le-Grand",         "640", "91810", "nord",  4000, 48.5550, 2.3736, "collectif",     None, ["vert-le-petit","fontenay-le-vicomte","mennecy"]),
    ("Vert-le-Petit",         "641", "91710", "nord",  4000, 48.5650, 2.3614, "collectif",     None, ["vert-le-grand","fontenay-le-vicomte","ballancourt-sur-essonne"]),
    ("Verrières-le-Buisson",  "643", "91370", "nord", 14000, 48.7394, 2.2542, "collectif",     None, ["massy","igny","palaiseau"]),
    ("Vigneux-sur-Seine",     "651", "91270", "nord", 27000, 48.6706, 2.4444, "collectif",     None, ["draveil","montgeron","ris-orangis"]),
    ("Villabé",               "652", "91100", "nord",  5000, 48.5850, 2.4578, "collectif",     None, ["corbeil-essonnes","lisses"]),
    ("Villebon-sur-Yvette",   "656", "91140", "nord", 11000, 48.7039, 2.2189, "collectif",     None, ["massy","chilly-mazarin","nozay"]),
    ("Villemoisson-sur-Orge", "657", "91360", "nord",  8000, 48.6578, 2.3289, "collectif",     None, ["savigny-sur-orge","epinay-sur-orge","morsang-sur-orge"]),
    ("Villiers-sur-Orge",     "663", "91700", "nord",  4000, 48.6250, 2.3183, "collectif",     None, ["sainte-genevieve-des-bois","saint-michel-sur-orge"]),
    ("Viry-Châtillon",        "669", "91170", "nord", 32000, 48.6672, 2.3814, "collectif",     None, ["grigny","juvisy-sur-orge","athis-mons"]),
    ("Wissous",               "689", "91320", "nord",  6000, 48.7167, 2.3369, "collectif",     None, ["massy","morangis","chilly-mazarin"]),
    ("Yerres",                "691", "91330", "nord", 29000, 48.7197, 2.4900, "collectif",     None, ["brunoy","montgeron","crosne","epinay-sous-senat"]),

    # ── SUD ESSONNE ── (non-collectif / fosse septique — services: vidange, SPANC)
    ("Abbéville-la-Rivière",  "001", "91150", "sud",    450, 48.3836, 2.1381, "non-collectif", "cc-etampois-sud-essonne",       ["etampes","morigny-champigny","ormoy-la-riviere"]),
    ("Angerville",            "017", "91670", "sud",   4000, 48.3200, 2.0000, "non-collectif", "cc-coeur-de-beauce-et-du-gatinais",["monnerville","mereville","pussay"]),
    ("Arrancourt",            "022", "91580", "sud",    300, 48.3700, 2.0800, "non-collectif", "cc-etampois-sud-essonne",       ["etampes","etrechy"]),
    ("Auvers-Saint-Georges",  "032", "91580", "sud",   3000, 48.4700, 2.1500, "non-collectif", "cc-etampois-sud-essonne",       ["etrechy","etampes","villeneuve-sur-auvers"]),
    ("Authon-la-Plaine",      "033", "91410", "sud",   1000, 48.5072, 1.9539, "non-collectif", "cc-dourdannais-en-hurepoix",    ["dourdan","saint-escobille","plessis-saint-benoist"]),
    ("Avrainville",           "035", "91630", "sud",   2000, 48.5350, 2.2781, "non-collectif", "cc-bievre-essonne",             ["marolles-en-hurepoix","cheptainville","guibeville"]),
    ("Baulne",                "039", "91590", "sud",    700, 48.4900, 2.4000, "non-collectif", "cc-coeur-essonne-juine-renarde", ["cerny","la-ferte-alais","d-huison-longueville"]),
    ("Boissy-la-Rivière",     "057", "91690", "sud",    800, 48.4050, 2.0950, "non-collectif", "cc-etampois-sud-essonne",       ["saclas","guillerval","etampes"]),
    ("Boissy-le-Cutté",       "059", "91750", "sud",    500, 48.4100, 2.3500, "non-collectif", "cc-coeur-essonne-juine-renarde", ["champcueil","nainville-les-roches","milly-la-foret"]),
    ("Boissy-le-Sec",         "060", "91870", "sud",   1500, 48.4600, 2.1200, "non-collectif", "cc-etampois-sud-essonne",       ["etampes","etrechy","arrancourt"]),
    ("Bouray-sur-Juine",      "070", "91850", "sud",   2000, 48.5050, 2.2950, "non-collectif", "cc-bievre-essonne",             ["lardy","janville-sur-juine","chamarande"]),
    ("Boutervilliers",        "074", "91150", "sud",    300, 48.4050, 2.0500, "non-collectif", "cc-etampois-sud-essonne",       ["etampes","champmotteux"]),
    ("Breux-Jouy",            "095", "91650", "sud",    600, 48.5400, 2.1850, "non-collectif", "cc-bievre-essonne",             ["saint-yon","arpajon"]),
    ("Brières-les-Scellés",   "098", "91150", "sud",    600, 48.5050, 2.0300, "non-collectif", "cc-dourdannais-en-hurepoix",    ["dourdan","corbreuse","richarville"]),
    ("Brouy",                 "100", "91150", "sud",    600, 48.3900, 2.2000, "non-collectif", "cc-etampois-sud-essonne",       ["etampes","morigny-champigny"]),
    ("Buno-Bonnevaux",        "103", "91720", "sud",    800, 48.4250, 2.4600, "non-collectif", "cc-coeur-essonne-juine-renarde", ["milly-la-foret","oncy-sur-ecole","valpuiseaux"]),
    ("Cerny",                 "105", "91590", "sud",   3000, 48.4817, 2.4064, "non-collectif", "cc-coeur-essonne-juine-renarde", ["la-ferte-alais","baulne","itteville","d-huison-longueville"]),
    ("Chamarande",            "106", "91730", "sud",    900, 48.4900, 2.2150, "non-collectif", "cc-bievre-essonne",             ["lardy","etrechy","bouray-sur-juine","torfou"]),
    ("Champcueil",            "110", "91750", "sud",   3000, 48.4500, 2.3600, "non-collectif", "cc-coeur-essonne-juine-renarde", ["nainville-les-roches","boissy-le-cutte","itteville"]),
    ("Champmotteux",          "111", "91150", "sud",    200, 48.3550, 2.1550, "non-collectif", "cc-etampois-sud-essonne",       ["etampes","boutervilliers"]),
    ("Chauffour-lès-Étréchy", "113", "91580", "sud",    500, 48.4650, 2.1700, "non-collectif", "cc-etampois-sud-essonne",       ["etrechy","etampes","villeneuve-sur-auvers"]),
    ("Cheptainville",         "116", "91630", "sud",    600, 48.5500, 2.3150, "non-collectif", "cc-bievre-essonne",             ["marolles-en-hurepoix","leudeville","avrainville"]),
    ("Corbreuse",             "172", "91410", "sud",   1500, 48.5150, 2.0100, "non-collectif", "cc-dourdannais-en-hurepoix",    ["dourdan","brieres-les-scelles","roinville","authon-la-plaine"]),
    ("Courdimanche-sur-Essonne","176","91720","sud",    800, 48.4400, 2.4100, "non-collectif", "cc-coeur-essonne-juine-renarde", ["milly-la-foret","maisse","valpuiseaux"]),
    ("Courances",             "177", "91490", "sud",    500, 48.4508, 2.5031, "non-collectif", "cc-coeur-essonne-juine-renarde", ["milly-la-foret","oncy-sur-ecole","moigny-sur-ecole"]),
    ("Dannemois",             "189", "91490", "sud",    500, 48.4200, 2.4400, "non-collectif", "cc-coeur-essonne-juine-renarde", ["milly-la-foret","buno-bonnevaux"]),
    ("D'Huison-Longueville",  "196", "91590", "sud",   1200, 48.4650, 2.4050, "non-collectif", "cc-coeur-essonne-juine-renarde", ["la-ferte-alais","cerny","baulne"]),
    ("Étréchy",               "222", "91580", "sud",   7000, 48.4892, 2.1853, "mixte",         "cc-etampois-sud-essonne",       ["etampes","chamarande","lardy","auvers-saint-georges"]),
    ("Fontaine-la-Rivière",   "234", "91690", "sud",    400, 48.3750, 2.0850, "non-collectif", "cc-etampois-sud-essonne",       ["etampes","saclas","guillerval"]),
    ("Fontenay-le-Vicomte",   "237", "91540", "sud",   3000, 48.5450, 2.3950, "non-collectif", "cc-coeur-essonne-juine-renarde", ["vert-le-petit","champcueil","ballancourt-sur-essonne"]),
    ("Fontenay-lès-Briis",    "238", "91640", "sud",   2500, 48.6167, 2.0833, "non-collectif", "cc-pays-de-limours",            ["limours","forges-les-bains","janvry"]),
    ("Forges-les-Bains",      "239", "91470", "sud",   4000, 48.6408, 2.1061, "non-collectif", "cc-pays-de-limours",            ["limours","saint-jean-de-beauregard","pecqueuse","fontenay-les-briis"]),
    ("Guibeville",            "288", "91630", "sud",    800, 48.5700, 2.3650, "non-collectif", "cc-bievre-essonne",             ["marolles-en-hurepoix","cheptainville","avrainville"]),
    ("Guillerval",            "289", "91690", "sud",    600, 48.4000, 2.0750, "non-collectif", "cc-etampois-sud-essonne",       ["etampes","saclas","ormoy-la-riviere","fontaine-la-riviere"]),
    ("Itteville",             "311", "91760", "sud",   5000, 48.5150, 2.3400, "non-collectif", "cc-coeur-essonne-juine-renarde", ["cerny","champcueil","la-ferte-alais","fontenay-le-vicomte"]),
    ("Janville-sur-Juine",    "313", "91510", "sud",   3000, 48.5408, 2.2578, "non-collectif", "cc-bievre-essonne",             ["lardy","bouray-sur-juine","etrechy","chamarande"]),
    ("Janvry",                "314", "91640", "sud",    800, 48.6650, 2.1500, "non-collectif", "cc-pays-de-limours",            ["forges-les-bains","limours","fontenay-les-briis"]),
    ("La Ferté-Alais",        "228", "91590", "sud",   5000, 48.4906, 2.3483, "non-collectif", "cc-coeur-essonne-juine-renarde", ["cerny","baulne","itteville","d-huison-longueville"]),
    ("La Forêt-le-Roi",       "246", "91410", "sud",    800, 48.5350, 2.0550, "non-collectif", "cc-dourdannais-en-hurepoix",    ["dourdan","roinville","saint-escobille"]),
    ("Lardy",                 "340", "91510", "sud",   6000, 48.5239, 2.2364, "mixte",         "cc-bievre-essonne",             ["etrechy","bouray-sur-juine","janville-sur-juine","chamarande"]),
    ("Leudeville",            "349", "91630", "sud",    700, 48.5650, 2.3150, "non-collectif", "cc-bievre-essonne",             ["marolles-en-hurepoix","cheptainville","avrainville"]),
    ("Limours",               "354", "91470", "sud",   7000, 48.6483, 2.0733, "mixte",         "cc-pays-de-limours",            ["forges-les-bains","janvry","saint-jean-de-beauregard","fontenay-les-briis"]),
    ("Maisse",                "363", "91720", "sud",   2000, 48.3906, 2.4139, "non-collectif", "cc-coeur-essonne-juine-renarde", ["milly-la-foret","courdimanche-sur-essonne","valpuiseaux"]),
    ("Mauchamps",             "381", "91150", "sud",    200, 48.3600, 2.2100, "non-collectif", "cc-etampois-sud-essonne",       ["etampes","morigny-champigny"]),
    ("Méréville",             "385", "91660", "sud",   3000, 48.3264, 2.0839, "non-collectif", "cc-coeur-de-beauce-et-du-gatinais",["angerville","pussay","monnerville"]),
    ("Moigny-sur-École",      "394", "91490", "sud",   1000, 48.4264, 2.4806, "non-collectif", "cc-coeur-essonne-juine-renarde", ["milly-la-foret","courances","oncy-sur-ecole"]),
    ("Mondeville",            "399", "91590", "sud",    500, 48.4450, 2.3750, "non-collectif", "cc-coeur-essonne-juine-renarde", ["la-ferte-alais","cerny","d-huison-longueville"]),
    ("Monnerville",           "400", "91930", "sud",   1500, 48.2769, 1.9781, "non-collectif", "cc-coeur-de-beauce-et-du-gatinais",["angerville","mereville"]),
    ("Morigny-Champigny",     "406", "91150", "sud",   4000, 48.4242, 2.1239, "non-collectif", "cc-etampois-sud-essonne",       ["etampes","etrechy","abbeville-la-riviere","brouy"]),
    ("Nainville-les-Roches",  "433", "91750", "sud",    500, 48.4300, 2.3800, "non-collectif", "cc-coeur-essonne-juine-renarde", ["champcueil","milly-la-foret","boissy-le-cutte"]),
    ("Oncy-sur-École",        "468", "91490", "sud",    800, 48.4350, 2.4900, "non-collectif", "cc-coeur-essonne-juine-renarde", ["milly-la-foret","courances","moigny-sur-ecole","buno-bonnevaux"]),
    ("Ormoy-la-Rivière",      "469", "91150", "sud",   1000, 48.4100, 2.1400, "non-collectif", "cc-etampois-sud-essonne",       ["etampes","guillerval","saclas","boissy-la-riviere"]),
    ("Pecqueuse",             "478", "91470", "sud",    700, 48.6200, 2.0800, "non-collectif", "cc-pays-de-limours",            ["limours","forges-les-bains","saint-jean-de-beauregard"]),
    ("Plessis-Saint-Benoist", "481", "91410", "sud",    800, 48.5400, 2.0400, "non-collectif", "cc-dourdannais-en-hurepoix",    ["dourdan","saint-escobille","authon-la-plaine","la-foret-le-roi"]),
    ("Puiselet-le-Marais",    "507", "91150", "sud",    400, 48.3900, 2.1850, "non-collectif", "cc-etampois-sud-essonne",       ["etampes","morigny-champigny","champmotteux"]),
    ("Pussay",                "508", "91740", "sud",   2000, 48.3158, 2.0036, "non-collectif", "cc-coeur-de-beauce-et-du-gatinais",["angerville","monnerville","mereville"]),
    ("Richarville",           "517", "91410", "sud",    400, 48.5250, 2.0000, "non-collectif", "cc-dourdannais-en-hurepoix",    ["dourdan","roinville","brieres-les-scelles"]),
    ("Roinville",             "527", "91410", "sud",    800, 48.5450, 2.0650, "non-collectif", "cc-dourdannais-en-hurepoix",    ["dourdan","corbreuse","richarville","la-foret-le-roi"]),
    ("Saclas",                "533", "91690", "sud",   2000, 48.4100, 2.0900, "non-collectif", "cc-etampois-sud-essonne",       ["etampes","guillerval","ormoy-la-riviere","fontaine-la-riviere","boissy-la-riviere"]),
    ("Saint-Chéron",          "541", "91530", "sud",   5000, 48.5503, 2.0794, "non-collectif", "cc-dourdannais-en-hurepoix",    ["dourdan","ollainville","sermaise","saint-maurice-montcouronne"]),
    ("Saint-Cyr-la-Rivière",  "543", "91690", "sud",    400, 48.3750, 2.0400, "non-collectif", "cc-etampois-sud-essonne",       ["etampes","saclas","guillerval"]),
    ("Saint-Escobille",       "544", "91410", "sud",    500, 48.5200, 2.0200, "non-collectif", "cc-dourdannais-en-hurepoix",    ["dourdan","plessis-saint-benoist","authon-la-plaine","la-foret-le-roi"]),
    ("Saint-Hilaire",         "548", "91780", "sud",   1500, 48.5100, 2.2250, "non-collectif", "cc-bievre-essonne",             ["lardy","etrechy","chamarande"]),
    ("Saint-Jean-de-Beauregard","549","91940","sud",    500, 48.6700, 2.1400, "non-collectif", "cc-pays-de-limours",            ["limours","forges-les-bains","pecqueuse","janvry"]),
    ("Saint-Maurice-Montcouronne","551","91530","sud", 1500, 48.5800, 2.1200, "non-collectif", "cc-dourdannais-en-hurepoix",    ["saint-cheron","sermaise","ollainville"]),
    ("Saint-Sulpice-de-Favières","562","91910","sud",   600, 48.4150, 2.0050, "non-collectif", "cc-etampois-sud-essonne",       ["saclas","etampes"]),
    ("Saint-Yon",             "565", "91650", "sud",   2000, 48.5450, 2.2000, "non-collectif", "cc-bievre-essonne",             ["breuillet","arpajon","saint-germain-les-arpajon","breux-jouy"]),
    ("Sermaise",              "590", "91530", "sud",   2000, 48.5600, 2.0900, "non-collectif", "cc-dourdannais-en-hurepoix",    ["saint-cheron","saint-maurice-montcouronne","ollainville"]),
    ("Torfou",                "618", "91730", "sud",    500, 48.4750, 2.2600, "non-collectif", "cc-bievre-essonne",             ["chamarande","lardy","etrechy"]),
    ("Valpuiseaux",           "628", "91720", "sud",    400, 48.4100, 2.4200, "non-collectif", "cc-coeur-essonne-juine-renarde", ["milly-la-foret","maisse","courdimanche-sur-essonne","buno-bonnevaux"]),
    ("Videlles",              "648", "91720", "sud",    600, 48.4300, 2.4600, "non-collectif", "cc-coeur-essonne-juine-renarde", ["milly-la-foret","buno-bonnevaux"]),
    ("Villeneuve-sur-Auvers", "658", "91580", "sud",    600, 48.4850, 2.1700, "non-collectif", "cc-etampois-sud-essonne",       ["etrechy","etampes","chauffour-les-etrechy"]),
]


def main():
    communes = []
    for row in RAW_COMMUNES:
        name, insee_sfx, cp, zone, pop, lat, lng, ass, spanc, adj = row
        communes.append(make_commune(name, insee_sfx, cp, zone, pop, lat, lng, ass, spanc, adj))

    out_path = ROOT / "data" / "communes_input.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(communes, f, ensure_ascii=False, indent=2)

    print(f"[OK] {len(communes)} communes générées → {out_path}")
    print(f"     Nord: {sum(1 for c in communes if c['zone']=='nord')}")
    print(f"     Sud:  {sum(1 for c in communes if c['zone']=='sud')}")


if __name__ == "__main__":
    main()
