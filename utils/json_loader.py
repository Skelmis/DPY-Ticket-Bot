import json
from pathlib import Path


def get_path():
    """Gets the path to the current working directory

    Returns
    -------
    String
        The path to the current working directory

    """
    cwd = Path(__file__).parents[1]
    cwd = str(cwd)
    return cwd


def read_json(filename):
    """Read a json file, and return the data.

    Parameters
    ----------
    filename : String
        The json file to be opened

    Returns
    -------
    Dict
        The contents of said file

    Warnings
    --------
    This function does not check `filename` exists. As such it
    can fail if you provide an incorrect filename.

    """
    cwd = get_path()
    with open(cwd + "/bot_config/" + filename + ".json", "r") as file:
        data = json.load(file)
    return data


def write_json(data, filename):
    """Write the given data to a json file.

    Parameters
    ----------
    data : Dict
        The data to be written to the json file
    filename : String
        The json file to write `data` to

    Warnings
    --------
    This function does not check `filename` exists. As such it
    can fail if you provide an incorrect filename.

    """
    cwd = get_path()
    with open(cwd + "/bot_config/" + filename + ".json", "w") as file:
        json.dump(data, file, indent=4)
