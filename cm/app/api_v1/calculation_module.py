import json
import logging
import pathlib
from pprint import pprint

import tempfile
from urllib.request import Request, urlopen

import numpy as np
import pandas as pd
from pint import UnitRegistry

import resutils.unit as ru

from ..constant import CM_NAME


# set a logger
LOG_FORMAT = (
    "%(levelname) -10s %(asctime)s %(name) -30s %(funcName) "
    "-35s %(lineno) -5d: %(message)s"
)
logging.basicConfig(format=LOG_FORMAT)
LOGGER = logging.getLogger(__name__)
# LOGGER.setLevel("DEBUG")

# set a unit register to convert between units
ureg = UnitRegistry()

""" Entry point of the calculation module function"""
# store vector layer names in global variables
WASTE = "potential_municipal_solid_waste"
AGRIC = "agricultural_residues_view"
LVSTK = "livestock_effluents_view"
FORST = "potential_forest"

BASEURL = (
    "https://gitlab.com/hotmaps/potential/"
    "{repo}/-/raw/master/data/{csv}?inline=false"
)

URLS = {
    WASTE: dict(repo="potential_municipal_solid_waste", csv="solid_waste.csv"),
    AGRIC: dict(repo="potential_biomass", csv="agricultural_residues.csv"),
    LVSTK: dict(repo="potential_biomass", csv="livestock_effluents.csv"),
    FORST: dict(repo="potential_biomass", csv="forest_residues.csv"),
}


def check_eff(type_eff, collecting_eff, heat_eff, el_eff, warnings=None):
    warnings = [] if warnings is None else warnings
    if collecting_eff > 1 or collecting_eff < 0:
        msg = (
            "The efficiency in collecting {type_eff} " "is not between 0 and 100"
        ).format(type_eff=type_eff)
        LOGGER.warning(msg)
        warnings.append(msg)
    if heat_eff + el_eff > 1:
        msg = (
            "The sum of the efficiency to generate heat and "
            "electricity from {type_eff}, "
            "exceed 100."
        ).format(type_eff=type_eff)
        LOGGER.warning(msg)
    return warnings


def apply_efficiency(energy, collecting_eff, heat_eff, el_eff):
    res = (energy * collecting_eff * heat_eff, energy * collecting_eff * el_eff)
    LOGGER.info(
        "heat = (energy * collecting_eff * heat_eff)\n"
        f"heat = ({energy} * {collecting_eff} * {heat_eff}) = {res[0]}\n"
        "elec = (energy * collecting_eff * el_eff)\n"
        f"elec = ({energy} * {collecting_eff} * {el_eff}) = {res[1]}"
    )
    return res


def get_data(repo, csv):
    """Retrieve/read agricultural residues data"""
    # TODO: once the dataset is integrated remove this function
    def read_csv(csvpath):
        try:
            return pd.read_csv(csvpath, header=0, index_col=0)
        except Exception as exc:
            LOGGER.exception(f"Failed to read: {csvpath} >> " f"exception = {exc}")
            raise exc

    # check if the file exists and in case download
    csvpath = pathlib.Path(tempfile.gettempdir(), csv)
    if csvpath.exists():
        return read_csv(csvpath)
    else:
        url = BASEURL.format(repo=repo, csv=csv)
        print(url)
        req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with open(csvpath, mode="wb") as cfile:
            cfile.write(urlopen(req).read())
        try:
            return read_csv(csvpath)
        except Exception as exc:
            LOGGER.exception(
                f"Failed to read: {csvpath} the file "
                f"has not been downloaded correctly from {url}."
            )
            raise exc


def calculation(
    output_directory,
    inputs_raster_selection,
    inputs_vector_selection,
    inputs_parameter_selection,
):
    # retrieve the inputs layes
    # TODO: the part in >>>>> {part} <<<<< have to be removed as soon as the layer
    # on agricurltural residues is integrated.
    # >>>>>
    # we need to retrieve the agricultural residues dataset
    waste = get_data(**URLS[WASTE])
    agric = get_data(**URLS[AGRIC])
    lvstk = get_data(**URLS[LVSTK])
    forst = get_data(**URLS[FORST])
    # <<<<<

    # livestock:      code	source	value	note	unit
    # forset biomass: code	source	value	note	unit
    # agriculture:    code	source	value	note	unit
    # solid_waste:    code	source	value	note	unit
    LOGGER.info("Start reading input json strings.")
    # TODO: uncomment the line bellow as soon as the layer it is available on the datawarehouse
    # >>>>>
    # waste = pd.read_json(json.dumps(inputs_vector_selection[WASTE]), orient="records")
    # agric = pd.read_json(json.dumps(inputs_vector_selection[AGRIC]), orient="records")
    # lvstk = pd.read_json(json.dumps(inputs_vector_selection[LVSTK]), orient="records")
    # forst = pd.read_json(json.dumps(inputs_vector_selection[FORST]), orient="records")
    # <<<<<

    # convert str to float
    psel = {k: float(v) / 100.0 for k, v in inputs_parameter_selection.items()}
    LOGGER.info(f"Selected parameters: {psel}")
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
        "agriculture residues",
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
        units = df.unit.drop_duplicates()
        if len(units) > 1:
            LOGGER.warnings(
                f"More than one unit found: {units} " "only the first will be used."
            )
            # TODO: In case of more units do something to handle this case
        unit = units.iloc[0]
        if unit == "PetaJoule":
            unit = "PJ"
        out_unit = "MWh"
        val = ureg.Quantity(val, ureg.parse_units(unit))
        val = val.to(out_unit).magnitude
        heat, el = apply_efficiency(val, psel[coll_perc], psel[heat_eff], psel[el_eff])
        heats.append(heat)
        els.append(el)

    hres = np.array(heats)
    eres = np.array(els)

    array = np.array(heats + els)
    _, graph_unit, graph_factor = ru.best_unit(
        array, out_unit, no_data=0, fstat=np.median, powershift=0
    )
    LOGGER.info(
        f"Moving from {out_unit} to {graph_unit} " "to improve the visualization"
    )
    heats_l = list((hres * graph_factor).round(decimals=3))
    els_l = list((eres * graph_factor).round(decimals=3))

    indicators = [
        {
            "unit": graph_unit,
            "name": "Total biomass heat energy potential",
            "value": np.round(hres.sum() * graph_factor, decimals=1),
        },
        {
            "unit": graph_unit,
            "name": "Total biomass electric energy potential",
            "value": np.round(eres.sum() * graph_factor, decimals=1),
        },
    ]

    color_h = "#3e95cd"
    color_e = "#8e5ea2"
    graphics = [
        dict(
            type="bar",
            xLabel="Biomass typologies",
            yLabel=graph_unit,
            data=dict(
                labels=labels,
                datasets=[
                    dict(
                        label="Biomass heat potential",
                        backgroundColor=[color_h] * len(labels),
                        data=heats_l,
                    ),
                    dict(
                        label="Biomass electricity potential",
                        backgroundColor=[color_e] * len(labels),
                        data=els_l,
                    ),
                ],
            ),
        )
    ]
    LOGGER.info(f"Computation graphics for biomass is: {graphics}")
    result = dict()
    result["name"] = CM_NAME
    result["indicator"] = []
    if len(warnings) > 0:
        result["indicator"].extend(
            [{"unit": "-", "name": msg, "value": 0} for msg in warnings]
        )
    result["indicator"].extend(indicators)
    result["graphics"] = graphics
    # result["vector_layers"] = []
    # result["raster_layers"] = []
    pprint(result)
    LOGGER.info(f"Computation result for biomass is: {result}")
    return result
