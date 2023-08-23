#!/bin/env python3

import csv
import json
import sys
import argparse
from io import StringIO

def flatten(json_object, parent_key='', sep='.'):
    """
    Recursively flatten a JSON object.
    """
    items = {}
    # If the json_object is a dictionary
    if isinstance(json_object, dict):
        for k, v in json_object.items():
            new_key = parent_key + sep + k if parent_key else k
            # If the value is a dictionary, recursively flatten
            if isinstance(v, dict):
                items.update(flatten(v, new_key, sep=sep))
            # If the value is a list
            elif isinstance(v, list):
                for idx, elem in enumerate(v):
                    # Construct a new key based on the index
                    list_key = new_key + sep + str(idx)
                    if isinstance(elem, (dict, list)):
                        items.update(flatten(elem, list_key, sep=sep))
                    else:
                        items[list_key] = elem
            else:
                items[new_key] = v
    return items

def json_to_csv_output(json_data):
    """
    Convert a list of JSON objects to CSV and output to console.
    """
    # Convert each JSON object into a flattened dictionary
    flattened_data = []
    for item in json_data:
        if isinstance(item, dict):
            flattened_data.append(flatten(item))
    # Check if there's any data to write
    if not flattened_data:
        print("No valid data found to convert to CSV.")
        return
    # Use StringIO to simulate a file object
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=flattened_data[0].keys())
    writer.writeheader()
    for row in flattened_data:
        writer.writerow(row)
    # Move the cursor to the beginning of the file and print its contents
    output.seek(0)
    print(output.read())

parser = argparse.ArgumentParser(
    prog='json2csv.py',
    description='Read json data from stdin and convert it into csv. Can handle inner dict and inner lists recursively.',
)
args = parser.parse_args()
json_str = sys.stdin.read()
json_to_csv_output(json.loads(json_str))
