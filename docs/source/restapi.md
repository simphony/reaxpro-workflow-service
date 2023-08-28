# Tutorial: launch a simulation through Python


In this quick tutorial, we will walk through a Python script that interacts with the FastAPI of the ReaxPro-platform using the `requests` library. The script performs various HTTP requests to retrieve information from the API.

```{note}
This is a tutorial how to technically run the API-endpoints from the quickstart-chapter of this document. The endpoints are explained more in detail in this particular chapter. Hence, it might make sense to you looking into the previous chapter first. If you are particularly interested in the description of the scienfitic models of the simulation engines, please do to the **use case chapter** of this document.
```

### Prerequisites

- Python 3.x installed
- `requests` library installed (you can install it using `pip install requests`), if not already installed on your environment
- The docker-compose up and running
- FastAPI-application through Docker available under your localhost

### Step 1: Import Dependencies

First, let's import the necessary dependencies for our script:

```
import requests
from pprint import pprint

```

### Step 2: Set the API Host

Next, let's define the host address of the FastAPI we want to interact with (e.g. through a localhost-forward from a remote VM):

```

HOST = "localhost:56442"

```

Make sure to replace localhost:56442 with the actual host address of your API.

### Step 3: Get Overview of Models Listed

To start, we will retrieve an overview of the models listed in the API. Here's the code for this step:

```

response = requests.get(f"http://{HOST}/models/registered")
print("Get overview of models listed")
pprint(response.json())

```

The requests.get() method is used to send a GET request to the /models/registered endpoint of the API. The response is then pretty printed using pprint().

The response will look like this:

```
Get overview of models listed
{'message': 'Fetched registry of data models.',
 'registered_models': ['COCatalyticFOAMModel', 'EnergyLandscape']}
```

### Step 4: Get Schema of a Model

Next, we will retrieve the schema of a specific model called COCatalyticFOAMModel. Here's the code:

```

response = requests.get(f"http://{HOST}/models/get_schema/COCatalyticFOAMModel")
print("Get schema of model COCatalyticFOAMModel")
pprint(response.json())

```

Similar to the previous step, we use requests.get() to send a GET request to the /models/get_schema/COCatalyticFOAMModel endpoint. The response is pretty printed.

Your response will look like this:


<Details>
<summary><b>Click here to expand</b></summary>

```
Get schema of model COCatalyticFOAMModel
{'definitions': {'Boundary': {'description': 'Model with a chosen set of '
                                             'boundary types.',
                              'enum': ['FixedValue',
                                       'FixedGradient',
                                       'CatalyticWall',
                                       'Empty',
                                       'ZeroGradient',
                                       'Processor',
                                       'Patch',
                                       'SymmetryPlane',
                                       'Wedge',
                                       'Wall'],
                              'title': 'Boundary',
                              'type': 'string'},
                 'BoundaryCondition': {'description': 'Patch and boundary type '
                                                      'definition.',
                                       'properties': {'boundary_type': {'allOf': [{'$ref': '#/definitions/Boundary'}],
                                                                        'default': 'ZeroGradient',
                                                                        'description': 'Boundary types available in 'OpenFOAM (most popular ones)'},
                                                      'patch': {'description': 'Patch in the mesh available from the use case.',
                                                                'standard_patches': ['inlet',
                                                                                     'outlet',
                                                                                     'inertWall',
                                                                                     'reactingWall',
                                                                                     'wedge1',
                                                                                     'wedge2',
                                                                                     'wedge3',
                                                                                     'wedge4'],
                                                                'title': 'Patch',
                                                                'type': 'string'},
                                                      'value': {'anyOf': [{'type': 'number'},
                                                                          {'type': 'integer'},
                                                                          {'items': {'type': 'number'},
                                                                           'type': 'array'}],
                                                                'description': 'Fixed value (Dirichlet-condition), fixed gradient (von-Neumann-condition) or field value at reacting catalyst wall. Field will be ignored for other conditions.',
                                                                'title': 'Value'}},
                                       'required': ['patch'],
                                       'title': 'BoundaryCondition',
                                       'type': 'object'},
                 'COCatalyticFOAMModel': {'properties': {'catalyst_amount': {'description': 'Amount fraction of catalyst in the reactive wall patch.',
                                                                             'maximum': 1,
                                                                             'minimum': 0,
                                                                             'title': 'Catalyst '
                                                                                      'Amount',
                                                                             'type': 'number'},
                                                         'chemical_species': {'description': 'List of chemical species involed into the reaction.',
                                                                              'items': {'$ref': '#/definitions/ChemicalSpecies'},
                                                                              'title': 'Chemical Species',
                                                                              'type': 'array'},
                                                         'fraction_sum_error': {'default': 3,
                                                                                'description': 'Number of decimal places which shall be used while rounding sum of mass fractions. E.g. the test passes when CO=0.4468 and O2=0.5531 with an error 3 digits, but fails for 4 digits.',
                                                                                'title': 'Fraction Sum Error',
                                                                                'type': 'integer'},
                                                         'patches_from_upload': {'description': 'If defined, UUID of the use case tar-ball in the cache to be used instead of the standard use case',
                                                                                 'format': 'uuid',
                                                                                 'title': 'Patches '
                                                                                          'From '
                                                                                          'Upload',
                                                                                 'type': 'string'},
                                                         'pressure': {'allOf': [{'$ref': '#/definitions/Pressure'}],
                                                                      'description': ''Pressure model of the mixture.',
                                                                      'title': 'Pressure'},
                                                         'solver_options': {'allOf': [{'$ref': '#/definitions/SolverOptions'}],
                                                                            'default': {'diffusivity_model': 'FicksDiffusion',
                                                                                        'turbulence_model': 'LaminarModel',
                                                                                        'use_energy_equation': False},
                                                                            'description': 'Solver options including turbulence and diffusion properties.',
                                                                            'title': 'Solver '
                                                                                     'Options'},
                                                         'species_from_upload': {'description': 'UUID of the PKL in the cache to be used instead of the standard model',
                                                                                 'format': 'uuid',
                                                                                 'title': 'Species From Upload',
                                                                                 'type': 'string'},
                                                         'temperature': {'allOf': [{'$ref': '#/definitions/Temperature'}],
                                                                         'description': 'Temperature model of the mixture.',
                                                                         'title': 'Temperature'},
                                                         'velocity': {'allOf': [{'$ref': '#/definitions/Velocity'}],
                                                                      'description': 'Velocity model of the mixture.',
                                                                      'title': 'Velocity'}},
                                          'required': ['chemical_species',
                                                       'velocity',
                                                       'pressure',
                                                       'temperature',
                                                       'catalyst_amount'],
                                          'title': 'COCatalyticFOAMModel',
                                          'type': 'object'},
                 'ChemicalSpecies': {'description': 'A chemical species with '
                                                    'defined properties.',
                                     'properties': {'boundaries': {'description': 'Mapping between available patches and boundary condition. NOTE: All patches in the mesh must be defined!',
                                                                   'items': {'$ref': '#/definitions/BoundaryCondition'},
                                                                   'title': 'Boundaries',
                                                                   'type': 'array'},
                                                    'composition': {'description': ''Chemical composition of the species. Available subset is forwarded from the standard surrogate model.',
                                                                    'standard_species': ['CO',
                                                                                         'O2',
                                                                                         'CO2'],
                                                                    'title': 'Composition',
                                                                    'type': 'string'},
                                                    'mass_fraction': {'description': 'Mass fraction of the species within the composition. Sum of all mass fractions must be 1.',
                                                                      'maximum': 1,
                                                                      'minimum': 0,
                                                                      'title': 'Mass '
                                                                               'Fraction',
                                                                      'type': 'number'}},
                                     'required': ['boundaries',
                                                  'composition',
                                                  'mass_fraction'],
                                     'title': 'ChemicalSpecies',
                                     'type': 'object'},
                 'DiffusivityModel': {'description': 'An enumeration.',
                                      'enum': ['FicksDiffusion',
                                               'MaxwellStefanDiffusion'],
                                      'title': 'DiffusivityModel',
                                      'type': 'string'},
                 'Pressure': {'description': 'Pressure model of the mixture.',
                              'properties': {'boundaries': {'description': 'Mapping between available patches and boundary condition. NOTE: All patches in the mesh must be defined!',
                                                            'items': {'$ref': '#/definitions/BoundaryCondition'},
                                                            'title': 'Boundaries',
                                                            'type': 'array'},
                                             'value': {'description': 'Pressure '
                                                                      'value '
                                                                      'of the '
                                                                      'mixture '
                                                                      'in Pa.',
                                                       'title': 'Value',
                                                       'type': 'number'}},
                              'required': ['boundaries', 'value'],
                              'title': 'Pressure',
                              'type': 'object'},
                 'SolverOptions': {'description': 'Solver options model for '
                                                  'diffusivity and turbulence '
                                                  'properties.',
                                   'properties': {'diffusivity_model': {'allOf': [{'$ref': '#/definitions/DiffusivityModel'}],
                                                                        'default': 'FicksDiffusion',
                                                                        'description': 'Diffusivity of the mixture: Fick's multi component diffusion or Maxwell Stefan diffusion.',},
                                                  'turbulence_model': {'allOf': [{'$ref': '#/definitions/TurbulenceModel'}],
                                                                       'default': 'LaminarModel',
                                                                       'description': 'Turbulence model of the mixture: laminar, RAS or LES.'},
                                                  'use_energy_equation': {'default': False,
                                                                          'description': 'Whether the energy equation should be regarded or not.',
                                                                          'title': 'Use Energy Equation',
                                                                          'type': 'boolean'}},
                                   'title': 'SolverOptions',
                                   'type': 'object'},
                 'Temperature': {'description': 'Temperature model of the '
                                                'mixture.',
                                 'properties': {'boundaries': {'description': 'Mapping between available patches and boundary condition. NOTE: All patches in the mesh must be defined!',
                                                               'items': {'$ref': '#/definitions/BoundaryCondition'},
                                                               'title': 'Boundaries',
                                                               'type': 'array'},
                                                'value': {'description': 'Temperature value of the mixture in K.',
                                                          'title': 'Value',
                                                          'type': 'number'}},
                                 'required': ['boundaries', 'value'],
                                 'title': 'Temperature',
                                 'type': 'object'},
                 'TurbulenceModel': {'description': 'Turblence model of the '
                                                    'CFD-calculation.',
                                     'enum': ['KOmegaSST',
                                              'KEpsilon',
                                              'LaminarModel',
                                              'SmagorinskyTurbulenceModel',
                                              'KineticEnergyEquation'],
                                     'title': 'TurbulenceModel',
                                     'type': 'string'},
                 'Velocity': {'description': 'Velocity model of the mixture.',
                              'properties': {'boundaries': {'description': 'Mapping between available patches and boundary condition. NOTE: All patches in the mesh must be defined!',
                                                            'items': {'$ref': '#/definitions/BoundaryCondition'},
                                                            'title': 'Boundaries',
                                                            'type': 'array'},
                                             'value': {'description': 'Velocity '
                                                                      'vector '
                                                                      'in m/s.',
                                                       'items': {'type': 'number'},
                                                       'maxItems': 3,
                                                       'minItems': 3,
                                                       'title': 'Value',
                                                       'type': 'array'}},
                              'required': ['boundaries', 'value'],
                              'title': 'Velocity',
                              'type': 'object'}}}
```

</Details>

<p></p>

### Step 5: Get Example of a Model

We will now retrieve an example of the COCatalyticFOAMModel. Here's the code:

```
response = requests.get(f"http://{HOST}/models/get_example/COCatalyticFOAMModel")
print("Get example of COCatalyticFOAMModel")
data = response.json()
pprint(data)
```

Again, we use requests.get() to send a GET request to the /models/get_example/COCatalyticFOAMModel endpoint. The response is pretty printed.

The expected result will look like this:

<Details>
<summary><b>Click here to expand</b></summary>

```
Get example of COCatalyticFOAMModel
{'catalyst_amount': 1.5e-05,
 'chemical_species': [{'boundaries': [{'boundary_type': 'Wedge',
                                       'patch': 'wedge1'},
                                      {'boundary_type': 'Wedge',
                                       'patch': 'wedge2'},
                                      {'boundary_type': 'Wedge',
                                       'patch': 'wedge3'},
                                      {'boundary_type': 'Wedge',
                                       'patch': 'wedge4'},
                                      {'boundary_type': 'FixedValue',
                                       'patch': 'inlet',
                                       'value': 0.432432432432432},
                                      {'boundary_type': 'ZeroGradient',
                                       'patch': 'outlet'},
                                      {'boundary_type': 'ZeroGradient',
                                       'patch': 'inertWall'},
                                      {'boundary_type': 'CatalyticWall',
                                       'patch': 'reactingWall',
                                       'value': 0.432432432432432}],
                       'composition': 'O2',
                       'mass_fraction': 0.432432432432432},
                      {'boundaries': [{'boundary_type': 'Wedge',
                                       'patch': 'wedge1'},
                                      {'boundary_type': 'Wedge',
                                       'patch': 'wedge2'},
                                      {'boundary_type': 'Wedge',
                                       'patch': 'wedge3'},
                                      {'boundary_type': 'Wedge',
                                       'patch': 'wedge4'},
                                      {'boundary_type': 'FixedValue',
                                       'patch': 'inlet',
                                       'value': 9.45945945945946e-06},
                                      {'boundary_type': 'ZeroGradient',
                                       'patch': 'outlet'},
                                      {'boundary_type': 'ZeroGradient',
                                       'patch': 'inertWall'},
                                      {'boundary_type': 'CatalyticWall',
                                       'patch': 'reactingWall',
                                       'value': 9.45945945945946e-06}],
                       'composition': 'CO',
                       'mass_fraction': 9.45945945945946e-06},
                      {'boundaries': [{'boundary_type': 'Wedge',
                                       'patch': 'wedge1'},
                                      {'boundary_type': 'Wedge',
                                       'patch': 'wedge2'},
                                      {'boundary_type': 'Wedge',
                                       'patch': 'wedge3'},
                                      {'boundary_type': 'Wedge',
                                       'patch': 'wedge4'},
                                      {'boundary_type': 'FixedValue',
                                       'patch': 'inlet',
                                       'value': 0.567558108108108},
                                      {'boundary_type': 'ZeroGradient',
                                       'patch': 'outlet'},
                                      {'boundary_type': 'ZeroGradient',
                                       'patch': 'inertWall'},
                                      {'boundary_type': 'CatalyticWall',
                                       'patch': 'reactingWall',
                                       'value': 0.567558108108108}],
                       'composition': 'CO2',
                       'mass_fraction': 0.567558108108108}],
 'pressure': {'boundaries': [{'boundary_type': 'ZeroGradient',
                              'patch': 'inlet'},
                             {'boundary_type': 'FixedValue',
                              'patch': 'outlet',
                              'value': 100000.0},
                             {'boundary_type': 'ZeroGradient',
                              'patch': 'inertWall'},
                             {'boundary_type': 'ZeroGradient',
                              'patch': 'reactingWall'},
                             {'boundary_type': 'Wedge', 'patch': 'wedge1'},
                             {'boundary_type': 'Wedge', 'patch': 'wedge2'},
                             {'boundary_type': 'Wedge', 'patch': 'wedge3'},
                             {'boundary_type': 'Wedge', 'patch': 'wedge4'}],
              'value': 100000.0},
 'solver_options': {'turbulence_model': 'LaminarModel',
                    'use_energy_equation': True},
 'temperature': {'boundaries': [{'boundary_type': 'FixedValue',
                                 'patch': 'inlet',
                                 'value': 900.0},
                                {'boundary_type': 'ZeroGradient',
                                 'patch': 'outlet'},
                                {'boundary_type': 'ZeroGradient',
                                 'patch': 'inertWall'},
                                {'boundary_type': 'CatalyticWall',
                                 'patch': 'reactingWall',
                                 'value': 900.0},
                                {'boundary_type': 'Wedge', 'patch': 'wedge1'},
                                {'boundary_type': 'Wedge', 'patch': 'wedge2'},
                                {'boundary_type': 'Wedge', 'patch': 'wedge3'},
                                {'boundary_type': 'Wedge', 'patch': 'wedge4'}],
                 'value': 900.0},
 'velocity': {'boundaries': [{'boundary_type': 'FixedValue',
                              'patch': 'inlet',
                              'value': [0.0, 0.0, 1.0]},
                             {'boundary_type': 'ZeroGradient',
                              'patch': 'outlet'},
                             {'boundary_type': 'FixedValue',
                              'patch': 'inertWall',
                              'value': [0.0, 0.0, 1.0]},
                             {'boundary_type': 'FixedValue',
                              'patch': 'reactingWall',
                              'value': [0.0, 0.0, 1.0]},
                             {'boundary_type': 'Wedge', 'patch': 'wedge1'},
                             {'boundary_type': 'Wedge', 'patch': 'wedge2'},
                             {'boundary_type': 'Wedge', 'patch': 'wedge3'},
                             {'boundary_type': 'Wedge', 'patch': 'wedge4'}],
              'value': [0.0, 0.0, 1.0]}}
```

</Details>

<p></p>

#### Step 5 a): Modify Example Dataset - simple

To modify the mass fraction and boundary condition in the example dataset, we can update the corresponding values in the `data` dictionary. Here's the code:

```
data["chemical_species"][0]["mass_fraction"] = 0.5
data["chemical_species"][0]["boundaries"][-2]["boundary_type"] = "ZeroValue"
data["chemical_species"][1]["mass_fraction"] = 0.4
data["chemical_species"][1]["boundaries"][-2]["boundary_type"] = "ZeroValue"
data["chemical_species"][2]["mass_fraction"] = 0.1
data["chemical_species"][2]["boundaries"][-2]["boundary_type"] = "ZeroValue"
```

In this code snippet, we access the relevant nested dictionaries in the `data` dictionary and update the desired values.

We are simply indexing the respective `chemical_species` in the `data`-dictionary and assign new values to the `mass_fraction`-entries (here: `0`->`O2`, `1` -> `CO`, `2`-> `CO2`). Additionally, we are setting a 0-valued Von-Neumann condition to the `-2 `-indexed patch (which is the `interWall` in the example data).

#### Step 5 b): Modify Example Dataset - Iterative Approach

Alternatively, if we have a new set of mass fractions and boundary types as dictionaries, we can iterate over the chemical species in the `data` dictionary and update the values dynamically. Here's the code:

```
new_mass_fraction = {"O2": 0.1, "CO": 0.4, "CO2": 0.5}
new_boundaries = {"inlet": "ZeroGradient", "outlet": "ZeroGradient"}

for species in data["chemical_species"]:
    composition = species["composition"]
    species["mass_fraction"] = new_mass_fraction[composition]
    for boundary in species["boundaries"]:
        patch = boundary["patch"]
        if patch in new_boundaries:
            boundary["boundary_type"] = new_boundaries[patch]

```

In this code snippet, we iterate over each chemical species in the `data` dictionary, since the order in the `chemical_species` might be arbitrarily set. We retrieve the composition and update the mass fraction using the corresponding value from the `new_mass_fraction `dictionary. We also update the boundary type based on the `new_boundaries` dictionary if the patch is present.

> Note: we modify set the `inlet` and `outlet` of this examplary dataset. You might be interested to set the boundary conditions for other patches in other scenarios as well.

### Step 6: Create a Model Based on modified example

Now, let's instanciate a COCatalyticFOAMModel based on the nodified example. Here's the code:

```
response = requests.post(f"http://{HOST}/models/create/COCatalyticFOAMModel", headers={"Content-Type": "application/json"}, json=data)
print("Create model COCatalyticFOAMModel based on example")
pprint(response.json())
```

We use requests.post() to send a POST request to the /models/create/COCatalyticFOAMModel endpoint. We pass the retrieved schema as JSON data in the request body using the json parameter. The response is pretty printed.

The expected output might look like this:

```
Create model COCatalyticFOAMModel based on example
{'cache_id': 'N2c20ce67ba9b4b81b37d09ac013ac919'}
```

### Step 7: Run a Task for the Instantiated Model

Let's run a task for the instantiated COCatalyticFOAMModel. Here's the code:

```

data = {
    "cache_id": response.json()["cache_id"],
    "format": "turtle"
}
response = requests.post(f"http://{HOST}/task/send", headers={"Content-Type": "application/json"}, json=data)
print("Run task for instantiated model")
print(response.json()
```

Let's run a task for the instantiated COCatalyticFOAMModel. Here's the code:

The expected output will look like this:

```
Run task for instantiated model
{'args': None,
 'date_done': None,
 'kwargs': None,
 'state': 'PENDING',
 'status': 'PENDING',
 'task_id': '923fb7ff-0b28-4bd7-a352-13e99474807d',
 'traceback': None}
```

### Step 8: Get Status for Running Task

To check the status of a running task, we can send a GET request to the `/task/status/{task_id}` endpoint, where `{task_id}` represents the ID of the task. Here's the code:

```
print("Get status for running task")
response = requests.get(f"http://{HOST}/task/status/{response.json()['task_id']}")
pprint(response.json())
```

We use requests.get() to send a GET request to the /task/status/{task_id} endpoint, where {task_id} is obtained from the response of the previous step. The response contains the status information of the task, which we then pretty print using pprint().

Here is the expected output:

```
Get status for running task
{'args': None,
 'date_done': None,
 'kwargs': None,
 'state': 'PENDING',
 'status': 'PENDING',
 'task_id': 'ed2a511e-5902-4e8e-b66e-267702e8fff3',
 'traceback': None}
```


## Additional instructions

### Enter the container through commandline

If you want to launch the solvers in the container directly, please type in:

```
docker exec -it fastapi-celery_simphony_1 bash
```

You will end up in the `/home/openfoam`-directory within the simphony-container as `openfoam`-user (no root-rights).

> **Note**: _If you want to launch the container with root-rights, simply type: `docker exec -u root -it fastapi-celery_simphony_1 bash`


When you navigate to `/home/openfoam/catalyticFoam/example`, choose a usecase (e.g. `laminar_2D_ML`) and type `catalyticPimpleTurbulentFOAM`, you will launch the catalyticFoam-solver on the defined use cases.
