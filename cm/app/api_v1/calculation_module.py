from osgeo import gdal

from ..helper import generate_output_file_tif, create_zip_shapefiles
from ..constant import CM_NAME
import time
import json

from pprint import pprint

import pandas as pd

from pint import UnitRegistry


ureg = UnitRegistry()

""" Entry point of the calculation module function"""

WASTE = "potential_municipal_solid_waste"
AGRIC = "agricultural_residues_view"
LVSTK = "livestock_effluents_view"
FORST = "potential_forest"


def check_eff(type_eff, collecting_eff, heat_eff, el_eff, warnings=None):
    warnings = [] if warnings is None else warnings
    if collecting_eff > 1 or collecting_eff < 0:
        msg = (
            "The efficiency in collecting {type_eff} " "is not between 0 and 100"
        ).format(type_eff=type_eff)
        warnings.append(msg)
    if heat_eff + el_eff > 1:
        msg = (
            "The sum of the efficiency to generate heat and "
            "electricity from {type_eff}, "
            "exceed 100."
        ).format(type_eff=type_eff)
    return warnings


def apply_efficiency(energy, collecting_eff, heat_eff, el_eff):
    return (energy * collecting_eff * heat_eff, energy * collecting_eff * el_eff)


def calculation(
    output_directory,
    inputs_raster_selection,
    inputs_vector_selection,
    inputs_parameter_selection,
):
    # retrieve the inputs layes

    # livestock:      code	source	value	note	unit
    # forset biomass: code	source	value	note	unit
    # agricolture:    code	source	value	note	unit
    # solid_waste:    code	source	value	note	unit
    waste = pd.read_json(json.dumps(inputs_vector_selection[WASTE]), orient="records")
    agric = pd.read_json(json.dumps(inputs_vector_selection[AGRIC]), orient="records")
    lvstk = pd.read_json(json.dumps(inputs_vector_selection[LVSTK]), orient="records")
    forst = pd.read_json(json.dumps(inputs_vector_selection[FORST]), orient="records")

    # convert str to float
    psel = {k: float(v) / 100.0 for k, v in inputs_parameter_selection.items()}
    """
{'agricultural_residues_view': [{'code': 'AT111',
                                 'source': 'cereal.straw',
                                 'unit': 'PetaJoule',
                                 'value': 0.110469314079422}],
 'livestock_effluents_view': [{'code': 'AT111',
                               'source': 'livestock.effluents',
                               'unit': 'PetaJoule',
                               'value': 0.0058316666697247705}],
 'potential_forest': [{'code': 'AT111',
                       'source': 'forest.residues',
                       'unit': 'PetaJoule',
                       'value': 0.49168313648148604}],
 'potential_municipal_solid_waste': [{'code': 'AT111',
                                      'source': 'household_waste',
                                      'unit': 'PetaJoule',
                                      'value': 0.0355200131152591}]}
    """
    keys = [
        ("waste_coll_perc", "waste_heat_eff", "waste_el_eff"),
        ("agric_coll_perc", "agric_heat_eff", "agric_el_eff"),
        ("forst_coll_perc", "forst_heat_eff", "forst_el_eff"),
        ("lvstk_coll_perc", "lvstk_heat_eff", "lvstk_el_eff"),
    ]
    labels = [
        "solid waste",
        "agricolture residues",
        "forest residues",
        "livestock effluents",
    ]
    warnings = []
    for label, (coll_perc, heat_eff, el_eff) in zip(labels, keys):
        check_eff(
            label, psel[coll_perc], psel[heat_eff], psel[el_eff], warnings=warnings
        )

    heats, els = [], []
    for df, (coll_perc, heat_eff, el_eff) in zip((waste, agric, forst, lvstk), keys):
        val = df.value.sum()
        # TODO: check if there are more than one unit
        unit = df.unit.drop_duplicates()[0]
        if unit == "PetaJoule":
            unit = "PJ"
        val = ureg.Quantity(val, ureg.parse_units(unit))
        val = val.to("MWh").magnitude
        heat, el = apply_efficiency(val, psel[coll_perc], psel[heat_eff], psel[el_eff])
        heats.append(heat)
        els.append(el)
    color_h = "#3e95cd"
    color_e = "#8e5ea2"
    graphics = [
        dict(
            type="bar",
            data=dict(
                labels=labels,
                datasets=[
                    dict(
                        label="Biomass heat potential",
                        backgroundColor=[color_h] * len(labels),
                        data=heats,
                    ),
                    dict(
                        label="Biomass electricity potential",
                        backgroundColor=[color_e] * len(labels),
                        data=els,
                    ),
                ],
            ),
        )
    ]

    result = dict()
    result["name"] = CM_NAME
    result["indicator"] = [{"unit": "-", "name": msg, "value": 0} for msg in warnings]
    result["graphics"] = graphics
    result["vector_layers"] = []
    result["raster_layers"] = []
    pprint(result)
    return result
