"""
This file is part of Covertau.

Covertau is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Covertau is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Covertau.  If not, see <https://www.gnu.org/licenses/>.
"""

from pathlib import Path
import json

CONFIG_FILE = '.config/radio.conf'

def get_config_filepath():
    return str(Path.home().joinpath(CONFIG_FILE))

def read_config_file():
    filepath = get_config_filepath()
    try:
        with open(filepath, 'r') as config_file:
            return json.load(config_file)
    except FileNotFoundError:
        return {}

def save_config_file(config_dict):
    filepath = get_config_filepath()
    with open(filepath, 'w') as config_file:
        json.dump(config_dict, config_file, indent=2)

def list_resources(config_dict):
    resources = config_dict.get('resources', [])
    return resources

def append_resource(config_dict, res):
    try:
        config_dict['resources'].append(res)
    except KeyError:
        config_dict['resources'] = [res]

def get_res_by_alias(config_dict, alias):
    for res in config_dict.get('resources', []):
        if res.get('alias', True) == alias:
            return res
    return None

def get_res_by_index(config_dict, index):
    try:
        return config_dict.get('resources', [])[index]
    except IndexError:
        return None




