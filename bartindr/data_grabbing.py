# class DrinkMenu():
# wrap in a class that stores various conversions of data
# as well as metric and nonmetric words

import numpy as np
import pandas as pd
import string
import requests
import re

from constants import *


class BarData():
    """
    Class to retrieve and preprocess data for the bartindr project. Stores all
    stages of data processing.
    """

    def __init__(self):
        self.search_url = 'https://www.thecocktaildb.com/api/json/v1/1/search.php?f='

    def gather_data(self):
        """
        Master function for retrieving and processing data.
        Accesses thecocktaildb api, retrieves data for all cocktails,
        splits data into values and units, converts all values to mL,
        and then converts values to proportionate amounts.

        Still figuring out what to do with nonmetric units

        Parameters
        ----------
        None

        Returns
        -------
        prop_df : n*m pandas.DataFrame
            dataframe of proportional ingredients by cocktail
            n = cocktails
            m = ingredients


        Example
        -------

        An "A1" cocktail has the following row of ingredients
            Gin          Grand Marnier   Lemon Juice   Grenadine  Lemon Peel
        A1  1 3/4 shot   1 Shot          1/4 Shot      1/8 Shot   1

        shots are converted to mL and then standardized to be proportions summing to 1
        count values are listed as TRUE
            Gin          Grand Marnier   Lemon Juice   Grenadine  Lemon Peel
        A1  77.63        44.36           11.09         5.545      NONE
        """

        print('identifying api endpoints...')
        self.url_list = create_url_list()
        print('pulling data...')
        self.cocktail_df = get_cdb_data(self.url_list)
        print('standardizing data...')
        self.standard_df = standardize_measures_to_metric(self.cocktail_df, metric='mL')
        print('converting to proportions...')
        self.prop_df = standardize_measures_to_props(self.standard_df)
        print('standardizing column names...')
        self.prop_df = _rename_columns(self.prop_df, column_semantics)

# def get_and_preprocess_data():
#     """
#     Master function for retrieving and processing data.
#     Accesses thecocktaildb api, retrieves data for all cocktails,
#     splits data into values and units, converts all values to mL,
#     and then converts values to proportionate amounts.
#
#     Still figuring out what to do with nonmetric units
#
#     Parameters
#     ----------
#     None
#
#     Returns
#     -------
#     prop_df : n*m pandas.DataFrame
#         dataframe of proportional ingredients by cocktail
#         n = cocktails
#         m = ingredients
#
#
#     Example
#     -------
#
#     An "A1" cocktail has the following row of ingredients
#         Gin          Grand Marnier   Lemon Juice   Grenadine  Lemon Peel
#     A1  1 3/4 shot   1 Shot          1/4 Shot      1/8 Shot   1
#
#     shots are converted to mL and then standardized to be proportions summing to 1
#     count values are listed as TRUE
#         Gin          Grand Marnier   Lemon Juice   Grenadine  Lemon Peel
#     A1  77.63        44.36           11.09         5.545      NONE
#
#     """
#
#     print('identifying api endpoints...')
#     url_list = create_url_list()
#     print('pulling data...')
#     cocktail_df = get_cdb_data(url_list)
#     print('standardizing data...')
#     standard_df = standardize_measures_to_metric(cocktail_df, metric='mL')
#     print('converting to proportions...')
#     prop_df = standardize_measures_to_props(standard_df)
#     print('standardizing column names...')
#     prop_df = _rename_columns(prop_df, column_semantics)
#
#     return(prop_df)

def create_url_list():
    """
    Generate list of compatable urls on thecocktaildb.com api

    Parameters
    ----------
    None

    Returns
    -------
    url_list : list
        list of all possible search urls by first character
        note: includes some urls that do not exist on API
    """

    url_list = []
    #source url for searching api by first character
    search_url = 'https://www.thecocktaildb.com/api/json/v1/1/search.php?f='

    #string.printable lists all sets of punctuation, digits, ascii_letters and whitespace
    for i in (string.printable):

        url_list.append(search_url+i)

    return url_list


def get_cdb_data(url_list):
    """
    Retrieves dataset as currently listed on thecocktaildb.com

    Parameters
    ----------
    url_list : list(str)
        list of API urls to search for data from create_url_list

    Returns
    -------
    cocktail_df : pandas.DataFrame
        pandas dataframe of units and measuresments with cocktail names as the index
        and ingredients as column headers

    """

    cocktail_df = pd.DataFrame()

    for url in url_list:

        try:
            r = requests.get(url)

            if r.json()['drinks']:

                for cocktail_dict in r.json()['drinks']:
                    cdf = get_ingredients_from_cocktail(cocktail_dict)
                    cocktail_df = cocktail_df.append(cdf)
        except:
            pass

    clean_cols = sorted(cocktail_df.columns.dropna())

    return cocktail_df[clean_cols].sort_index().drop_duplicates()


def get_ingredients_from_cocktail(cocktail_dict:dict) -> pd.DataFrame:
    """
    Extract measures of ingredients from a dictionary of ingrediences and measures.

    Parameters
    ----------
    cocktail_dict : dict
        dictionary listing attributes of a single cocktail, extracted from thecocktaildb.com api
        see get_cdb_data

    Returns
    -------
    cdf : pd.DataFrame
        pandas dataframe of cocktails extracted from cocktail_dict
        ingredients listed as columns, with cocktails on each row, and measurement values in each cell
    """

    ingredients = [i for i in cocktail_dict.keys() if i.find('strIngredient') > -1]
    ingredients_list = [cocktail_dict[i] for i in ingredients if i]
    ingredients_list = [t.lower() for t in ingredients_list if t]
    # self.ingredients_list = ingredients_list

    measures = [i for i in cocktail_dict.keys() if i.find('strMeasure') > -1]
    measures_list = [cocktail_dict[m] for m in measures if m]
    measures_list = [t.lower() for t in measures_list if t]
    # self.measures_list = measures_list

    cdf = pd.DataFrame(dict(zip(ingredients_list,measures_list)), index=[cocktail_dict['strDrink']])

    return cdf



def split_value_measure(measure):
    """
    helper function to divide values from units in cocktail measuremets by individual cell

    Parameters
    ----------
    row : str
        string of numeric and characters

    Returns
    -------
    val : numeric
        numeric value of corresponding unit
    unit : str
        string unit of corresponding value
    """

    measure = _check_separate_numeric(measure)
    measure = _remove_punctuation(measure)

    val = sum([eval(i) for i in measure.split() if list(i)[0].isdigit()])

    if not val: #cases were value is implied, e.g. "ice" or "bottle wine"
        val = 1

    unit = np.array([i.lower() for i in measure.split() if list(i)[0].isalpha()]).flatten()
    unit = ' '.join(unit)

    if not unit:
        unit = 'count' #cases where unit is implied, e.g. "Lemon: 1"

    #take abs in case of misinterpretation of m-dash as negative
    return(abs(val), unit)


def split_value_measure_byrow(row):
    """
    helper function to divide units from measurements in cocktails by row

    Parameters
    ----------
    row : pandas.Series
        row of values from a pandas.DataFrame

    Returns
    -------
    values : list(numeric)
        list of numeric values corresponding to amounts of some unit
    units : list(string)
        list of strings corresponding to units of values
    """

    cleanrow = row.dropna()
    values = []
    units = []

    for i, v in cleanrow.iteritems():

        val, unit = split_value_measure(v)
        # convert_unit
        values += [val]
        units += [unit]

    return(values, units)


def convert_unit(value, input_unit, conversion='mL'):
    """
    convert values of input_units to conversion units
    only supports conversion to mL at the moment

    Parameters
    ----------
    value : numeric
        numeric value corresponding to amount of some unit
    input_unit : string
        string corresponding to unit of value
    conversion : str
        unit to convert input_unit value
        only mL is supported at the moment

    Returns
    -------
    c_values : numeric
        values converted to conversion metric
    """

    if input_unit in part_words:
        c_value = value
    #need to figure out what to do with parametic words
    elif input_unit in nonmetric_words:
        c_value = 1
    elif input_unit in ml_conversion_dict.keys():
        c_value = value*ml_conversion_dict[input_unit]
    else:
        c_value=None

    return c_value


def batch_convert_units(values, input_units, conversion='mL'):
    """
    convert multiple value-unit pairs to conversion units
    only supports conversion to mL at the moment

    Parameters
    ----------
    values : list(numeric)
        list of numeric values corresponding to amounts of some unit
    input_units : list(string)
        list of strings corresponding to units of values
    conversion : str
        unit to convert input_unit-value pairs
        only mL is supported at the moment

    Returns
    -------
    c_values : numeric
        values converted to conversion metric
    """

    c_values = []
    for v, u in zip(values, input_units):
        c_values += [convert_unit(value=v, input_unit=u, conversion=conversion)]

    return(c_values)

def standardize_measures_to_props(converted_df):
    """
    Convert uniform measures of ingredients (e.g., all ingredients listed in mL)
    to proportionate amounts per drink

    Still figuring out nonmetric units

    Parameters
    ----------
    converted_df : pd.DataFrame
        dataframe of values in a single metric; output of standardize_measures_to_metric


    Returns
    -------
    prop_df : pd.DataFrame
        dataframe of proportional values for each cocktail (row index)


    Example
    -------

    An "A1" cocktail has the following row of ingredients
        Gin          Grand Marnier   Lemon Juice   Grenadine  Lemon Peel
    A1  1 3/4 shot   1 Shot          1/4 Shot      1/8 Shot   1

    shots are converted to mL and then standardized to be proportions summing to 1
    count values are listed as TRUE
        Gin          Grand Marnier   Lemon Juice   Grenadine  Lemon Peel
    A1  .56          .32             .08           .04        TRUE

    """
    return (converted_df.fillna(0).T / converted_df.fillna(0).sum(axis=1)).T

def standardize_measures_to_metric(df, metric='mL'):
    """
    Convert raw measures of ingredients to milliliters

    Still figuring out what to do with nonmetric units

    Parameters
    ----------
    df : pandas.DataFrame
        dataframe of value-metric pairs, exported from get_cdb_data
    metric: str
        metric to convert value-metric pairs in df.
        currently only supports mL conversions

    Returns
    -------
    converted_df : pandas.DataFrame
        dataframe of input df converted to metric


    Example
    -------

    An "A1" cocktail has the following row of ingredients
        Gin          Grand Marnier   Lemon Juice   Grenadine  Lemon Peel
    A1  1 3/4 shot   1 Shot          1/4 Shot      1/8 Shot   1

    shots are converted to mL and then standardized to be proportions summing to 1
    count values are listed as TRUE
        Gin          Grand Marnier   Lemon Juice   Grenadine  Lemon Peel
    A1  77.63        44.36           11.09         5.545      NONE

    """
    converted_df = pd.DataFrame()

    for index, row in df.iterrows():
        row = row.dropna()
        # break out values and units
        ingredients = row.index
        values, units = split_value_measure_byrow(row)
        c_units = [find_unit(u) for u in units]
        c_values = batch_convert_units(values, c_units, conversion='mL')
        temp = pd.DataFrame(dict(zip(ingredients, c_values)), index=[index])
        converted_df = converted_df.append(temp)

    return(converted_df)


def find_unit(unit_string, verbose=False):
    """
    find correct unit embedded in larger string

    Parameters
    ----------
    unit_string : str
        unstructured string of unit information
        e.g., 'ounces' or 'fill to top'
    verbose : bool
        flag for printing detailed output on string matching

    Returns
    -------
    unit : str
        structured unit from list of acceptable units for converstion
        if no units match the unit_string, will return None

    """

    item = _remove_spaces(unit_string)
    unit = None

    if item in (metric_words + odd_metric_words + part_words):
        unit = item

    elif item in (nonmetric_words):
        # separating non-metric words for future editing
        unit = item

    else:
        #imperfect matches
        #prioritizing primary metrics
        matches = [metric for metric in (metric_words + part_words) if metric in item]
        if len(matches) == 1:
            unit = matches[0]
        elif any(matches):
            unit = max(matches,key=len)
            if verbose: print(f'no exact match found for [{item}]; using [{unit}]')
        else:
            #secondary metrics
            matches = [metric for metric in (odd_metric_words) if metric in item]
            if any(matches):
                unit = max(matches,key=len)
                if verbose: print(f'no exact match found for [{item}]; using [{unit}]')
            else:
                # if no unit found, search for nonmetrics
                matches = [metric for metric in (nonmetric_words) if metric in item]
                if any(matches):
                    unit = max(matches,key=len)
                    if verbose: print(f'no exact match found for [{item}]; using [{unit}]')

    if (not unit) and verbose: print(f'no units for [{item}]')

    return(unit)


def _check_separate_numeric(string):
    """
    helper function to make sure that numeric values have a space between alphabetical characters

    Parameters
    ----------
    string : str
        any string

    Returns
    -------
    new_string : str
        string with guaranteed spaces before and after numeric values
    """

    new_string = string
    space_loc = []

    for i, s in enumerate(string):
        if (s.isalpha() and string[i-1].isnumeric()) or (s.isnumeric() and string[i-1].isalpha()):
            space_loc += [i]

    space_loc.reverse()

    for i in space_loc:
        new_string = new_string[:i] + ' ' + new_string[i:]

    return new_string


def _remove_spaces(string):
    """
    verifies that no spaces exist in string
    removes spaces if found

    Parameters
    ----------
    string : str
        any string

    Returns
    -------
    new_string : str
        string with spaces removed
    """
    return string.replace(" ", "")

def _remove_punctuation(string):
    """
    remove punctuation from strings
    necessary for separating numerics from alphabetic characters

    Parameters
    ----------
    string : str
        any string

    Returns
    -------
    new_string : str
        string with punctuation replaced with a space
    """
    return re.sub(r"[+,.;@#?!&$-]+\ *", " ", string)

def _rename_columns(df, column_semantics):
    """
    helper function to rename the ouput dataframe into common semantics
    e.g., anisette, sambuca and ouzo are all types of anise liqueur,
    """
    simple_df = df.rename(columns=column_semantics)
    simple_df = simple_df.groupby(simple_df.columns, axis=1).sum()
    return(simple_df)
