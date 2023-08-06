"""
Simple methods for processing JSON files
"""

import os
import json

'''
Write given JSON to given file.
'''

def save_json(json_struct, json_filepath):
    with open(json_filepath, 'w') as f:
        json.dump(json_struct, f, indent=2, sort_keys=True)

def load_config():
    filepath = os.path.abspath('hone/config.json')
    with open(filepath, 'r') as f:
        return json.load(f)
