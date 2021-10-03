import os
from configparser import ConfigParser


def initialize_config(variables):
    """ Parse env variables or config file to find program config params

    Function that search and parse program configuration parameters in the
    program environment variables first and the in a config file.
    If at least one of the config parameters is not found a KeyError exception
    is thrown. If a parameter could not be parsed, a ValueError is thrown.
    If parsing succeeded, the function returns a ConfigParser object
    with config parameters
    """

    config = ConfigParser(os.environ)
    # If config.ini does not exists original config object is not modified
    config.read("config.ini")

    config_params = {}
    try:
        for variable_name, variable_type in variables:
            config_params[variable_name] = variable_type(config["DEFAULT"][variable_name])
    except KeyError as e:
        raise KeyError("Key was not found. Error: {} .Aborting src".format(e))
    except ValueError as e:
        raise ValueError("Key could not be parsed. Error: {}. Aborting src".format(e))

    return config_params
