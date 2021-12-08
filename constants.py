"""
constants for metric conversion

instead of listing out stop words, I'm going to list out compatable metrics
and for each value, iterate through and strip out numerics and operators (./)
reminder to account for plurals (e.g. jigger & jiggers)
"""


# taken from wikipedia
primary_conversion_dict = {
                      'cl': 10,
                      'cup' : 236.59,
                      'dash': .92,
                      'dl'  : 100,
                      'drop' : .05,
                      'fifth': 750,
                      'gal': 3785.412,
                      'tablespoon' : 14.787,
                      'tblsp' : 14.787,
                      'tbsp' : 14.787,
                      'jigger' : 44.3602943, #aka a shot
                      'ml' : 1,
                      'ounce' : 29.574,
                      'oz' : 29.574,
                      'pony': 29.57,
                      'pinch' : .31,
                      'pint' : 568.261,
                      'pt' : 568.261,
                      'qt' : 946.35,
                      'quart' : 946.35,
                      'shot'  : 44.3602943,
                      'snit' : 88.72,
                      'splash' : 5.91,
                      'split' : 177.44,
                      'teaspoon' :  4.93,
                      'tsp' :  4.93,
                      'wineglass': 118.29}

secondary_conversion_dict = {'can': 354.882, #surprisingly decent assumption of a 12 oz can standard
                             'cube': 30,
                             'float' : 29.574, #assuming a float to be a pony/ounce
                             'g' : 1, #assuming gram; here as secondary measure to searc
                             'gr': 1, #assuming this is a misnomer abbeviation for gram
                             'gram' : 1,
                             'in' : 16.387, #this assumes cubic inches, which is almost certainly not the intention of the authors
                             'inch': 16.387}

ml_conversion_dict = {**primary_conversion_dict, **secondary_conversion_dict}

metric_words = list(primary_conversion_dict.keys())
odd_metric_words = list(secondary_conversion_dict.keys())


#since we're converting everything to parts, we'll leave "part" as it's own category
part_words = ['part', 'parts']


# there are some words that are not exact metrics but are still units. 
# for now, these will be listed as "ingrdients present" but not incorporated into ratios
nonmetric_words =  ['1', #count value
                    'bottle', # 12oz beer = 354.882 mL, bottle of wine = 750 mL, bottle of soda = 2000 mL
                    'chunks',
                    'count', #filler word where unit is implied'absent
                    'crushed', #a bad metric for ice
                    'fill',
                    'fillwith',
                    'garnish',
                    'glass',
                    'ground',
                    'juice',
                    'package',
                    'piece',
                    'rim',
                    'slice',
                    'sprig',
                    'stick',
                    'top',
                    'twist',
                    'wedge',
                    'whole']