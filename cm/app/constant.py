CELERY_BROKER_URL_DOCKER = "amqp://admin:mypass@rabbit:5672/"
CELERY_BROKER_URL_LOCAL = "amqp://localhost/"


CM_REGISTER_Q = "rpc_queue_CM_register"  # Do no change this value

CM_NAME = "CM - Biomass residues potential"
RPC_CM_ALIVE = "rpc_queue_CM_ALIVE"  # Do no change this value
RPC_Q = "rpc_queue_CM_compute"  # Do no change this value
CM_ID = 12384384  # CM_ID is defined by the enegy research center of Martigny (CREM)
PORT_LOCAL = int("500" + str(CM_ID))
PORT_DOCKER = 80

# TODO ********************setup this URL depending on which version you are running***************************

CELERY_BROKER_URL = CELERY_BROKER_URL_DOCKER
PORT = PORT_DOCKER

# TODO ********************setup this URL depending on which version you are running***************************

#    waste = inputs_vector_selection[WASTE]
#    agric = inputs_vector_selection[AGRIC]
#    lvstk = inputs_vector_selection[LVSTK]
#    forst = inputs_vector_selection[FORST]
TRANFER_PROTOCOLE = "http://"
INPUTS_CALCULATION_MODULE = [
    # Waste
    {
        "input_name": "Percentage of solid waste collected [%]",
        "input_type": "input",
        "input_parameter_name": "waste_coll_perc",
        "input_value": "90",
        "input_priority": 0,
        "input_unit": "none",
        "input_min": 0,
        "input_max": 100,
        "cm_id": CM_ID,  # Do no change this value
    },
    {
        "input_name": "Efficiency in transforming solid waste in thermal energy [%]",
        "input_type": "input",
        "input_parameter_name": "waste_heat_eff",
        "input_value": "50",
        "input_priority": 0,
        "input_unit": "none",
        "input_min": 0,
        "input_max": 100,
        "cm_id": CM_ID,  # Do no change this value
    },
    {
        "input_name": "Efficiency in transforming solid waste in eletrical energy [%]",
        "input_type": "input",
        "input_parameter_name": "waste_el_eff",
        "input_value": "20",
        "input_priority": 0,
        "input_unit": "none",
        "input_min": 0,
        "input_max": 100,
        "cm_id": CM_ID,  # Do no change this value
    },
    # Agriculture
    {
        "input_name": "Percentage of agriculture residues collected [%]",
        "input_type": "input",
        "input_parameter_name": "agric_coll_perc",
        "input_value": "60",
        "input_priority": 0,
        "input_unit": "none",
        "input_min": 0,
        "input_max": 100,
        "cm_id": CM_ID,  # Do no change this value
    },
    {
        "input_name": "Efficiency in transforming agriculture residues in thermal energy [%]",
        "input_type": "input",
        "input_parameter_name": "agric_heat_eff",
        "input_value": "50",
        "input_priority": 0,
        "input_unit": "none",
        "input_min": 0,
        "input_max": 100,
        "cm_id": CM_ID,  # Do no change this value
    },
    {
        "input_name": "Efficiency in transforming agriculture residues in eletrical energy [%]",
        "input_type": "input",
        "input_parameter_name": "agric_el_eff",
        "input_value": "20",
        "input_priority": 0,
        "input_unit": "none",
        "input_min": 0,
        "input_max": 100,
        "cm_id": CM_ID,  # Do no change this value
    },
    # Livestock
    {
        "input_name": "Percentage of livestock effluents collected [%]",
        "input_type": "input",
        "input_parameter_name": "lvstk_coll_perc",
        "input_value": "50",
        "input_priority": 0,
        "input_unit": "none",
        "input_min": 0,
        "input_max": 100,
        "cm_id": CM_ID,  # Do no change this value
    },
    {
        "input_name": "Efficiency in transforming livestock effluents in thermal energy [%]",
        "input_type": "input",
        "input_parameter_name": "lvstk_heat_eff",
        "input_value": "50",
        "input_priority": 0,
        "input_unit": "none",
        "input_min": 0,
        "input_max": 100,
        "cm_id": CM_ID,  # Do no change this value
    },
    {
        "input_name": "Efficiency in transforming livestock effluents in eletrical energy [%]",
        "input_type": "input",
        "input_parameter_name": "lvstk_el_eff",
        "input_value": "20",
        "input_priority": 0,
        "input_unit": "none",
        "input_min": 0,
        "input_max": 100,
        "cm_id": CM_ID,  # Do no change this value
    },
    # Forest
    {
        "input_name": "Percentage of forest residues collected [%]",
        "input_type": "input",
        "input_parameter_name": "forst_coll_perc",
        "input_value": "50",
        "input_priority": 0,
        "input_unit": "none",
        "input_min": 0,
        "input_max": 100,
        "cm_id": CM_ID,  # Do no change this value
    },
    {
        "input_name": "Efficiency in transforming forest residues in thermal energy [%]",
        "input_type": "input",
        "input_parameter_name": "forst_heat_eff",
        "input_value": "50",
        "input_priority": 0,
        "input_unit": "none",
        "input_min": 0,
        "input_max": 100,
        "cm_id": CM_ID,  # Do no change this value
    },
    {
        "input_name": "Efficiency in transforming forest residues in eletrical energy [%]",
        "input_type": "input",
        "input_parameter_name": "forst_el_eff",
        "input_value": "20",
        "input_priority": 0,
        "input_unit": "none",
        "input_min": 0,
        "input_max": 100,
        "cm_id": CM_ID,  # Do no change this value
    },
]


SIGNATURE = {
    "category": "Supply",
    "authorized_scale": ["NUTS 3", "NUTS 2", "NUTS 1", "NUTS 0"],
    "cm_name": CM_NAME,
    "layers_needed": [
        # https://github.com/HotMaps/Hotmaps-toolbox-service/blob/master/api/app/models/indicators.py
    ],
    "type_layer_needed": [],
    "vectors_needed": [
        "potential_municipal_solid_waste",
        "agricultural_residues_view",
        "livestock_effluents_view",
        "potential_forest",
    ],
    "cm_url": "Do not add something",
    "cm_description": "this computation module allows to divide the HDM",
    "cm_id": CM_ID,
    "inputs_calculation_module": INPUTS_CALCULATION_MODULE,
}
