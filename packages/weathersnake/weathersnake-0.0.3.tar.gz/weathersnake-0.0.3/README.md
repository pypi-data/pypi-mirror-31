[![Build Status](https://travis-ci.org/ericcheatham/weathersnake.svg?branch=master)](https://travis-ci.org/ericcheatham/weathersnake)
# weathersnake
What is the current weather in your area?

Weathersnake uses the API from openweathermap to return the current temperature in a specific area

### Installing weathersnake
It is highly recommended that you run this in a [virtual environment](https://virtualenvwrapper.readthedocs.io/en/latest/#)

#### Installing from source (installs as a developer instance)
- Clone repository to your local development environment
- `pip install -e .`


#### Normal installation (WIP)
- `pip install weathersnake`


## Running Weathersnake

```
usage: weathersnake [-h] [--format {metric,kelvin,imperial}]

Python based temperature app

optional arguments:
  -h, --help            show this help message and exit
  --format {metric,kelvin,imperial}
```

Enter the name of a location in the form of `"CITY","STATE/COUNTRY"` to get the current temperature in that location.

```
Where are you? Newport News, VA
Newport News, VA weather:
 63.84 degrees Fahrenheit
```

To exit Weathernsake you can either send a keyboard interrupt `CTRL + C` or enter
the word "quit" to exit.

### Issues?
Please open an issue here on the repo
