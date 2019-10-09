import tempfile
import unittest
from werkzeug.exceptions import NotFound
import pathlib as pth
from pprint import pprint

from app import create_app
from app.api_v1.calculation_module import WASTE, AGRIC, LVSTK, FORST
from app.constant import INPUTS_CALCULATION_MODULE

import os.path
from shutil import copyfile
from .test_client import TestClient

import numpy as np
import matplotlib.pyplot as plt

import json

from pint import UnitRegistry


ureg = UnitRegistry()
if os.environ.get("LOCAL", False):
    UPLOAD_DIRECTORY = os.path.join(
        tempfile.gettempdir(), "hotmaps", "cm_files_uploaded"
    )
else:
    UPLOAD_DIRECTORY = "/var/hotmaps/cm_files_uploaded"

if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)
    os.chmod(UPLOAD_DIRECTORY, 0o777)


class TestAPI(unittest.TestCase):
    def setUp(self):
        self.app = create_app(os.environ.get("FLASK_CONFIG", "development"))
        self.ctx = self.app.app_context()
        self.ctx.push()

        self.client = TestClient(self.app)

    def tearDown(self):
        self.ctx.pop()

    def test_compute(self):
        def read_json(jsname):
            tdir = pth.Path(__file__).parent
            print(tdir.absolute())
            jsfile = tdir / "data" / jsname
            with open(jsfile, mode="r") as js:
                return json.load(js)

        def sel_by_code(dlist, code):
            return [d for d in dlist if d["code"] == code]

        inputs_raster_selection = {}
        inputs_parameter_selection = {
            d["input_parameter_name"]: d["input_value"]
            for d in INPUTS_CALCULATION_MODULE
        }
        inputs_vector_selection = {}

        json_names = (
            "agricultural_residues.json",
            "solid_waste.json",
            "livestock_effluents.json",
            "forest_residues.json",
        )
        json_keys = (AGRIC, WASTE, LVSTK, FORST)
        for jskey, jsname in zip(json_keys, json_names):
            jsn = sel_by_code(read_json(jsname), code="AT111")
            inputs_vector_selection[jskey] = jsn

        inputs_parameter_selection["multiplication_factor"] = 2

        # register the calculation module a
        payload = {
            "inputs_raster_selection": inputs_raster_selection,
            "inputs_parameter_selection": inputs_parameter_selection,
            "inputs_vector_selection": inputs_vector_selection,
        }

        rv, js = self.client.post("computation-module/compute/", data=payload)
        self.assertTrue(rv.status_code == 200)
