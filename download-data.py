#!/bin/env python3

import os
import argparse
import urllib.request
import base64
import json
from datetime import datetime

REQUEST_URL_TEMPLATE = 'https://app.fakturoid.cz/api/v2/accounts/{}/{}'

def get_auth():
    """
    Get user slug, username, API key and store it .auth file. If there is already .auth file, use it.
    """
    auth_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".auth")
    # Check if .auth file already exists
    if os.path.exists(auth_path):
        with open(auth_path, 'r') as file:
            lines = file.readlines()
            slug = lines[0].strip()
            username = lines[1].strip()
            api_key = lines[2].strip()
            return [slug, username, api_key]
    # If .auth file doesn't exist, prompt the user for details
    slug = input("Enter slug: ")
    username = input("Enter username: ")
    api_key = input("Enter API key: ")
    # Save the details in .auth file
    with open(auth_path, 'w') as file:
        file.write(slug + '\n')
        file.write(username + '\n')
        file.write(api_key + '\n')
    return [slug, username, api_key]

def download_all(type, since):
    """
    Download paginated data from API, ask for since date.
    """
    auth_data = get_auth()
    all_data = []
    api_url = REQUEST_URL_TEMPLATE.format(auth_data[0], type)
    if since:
        api_url = api_url + '?since={}'.format(datetime.strptime(since, '%Y-%m-%d').isoformat())
    while api_url:
        # set auth header
        request = urllib.request.Request(api_url)
        base64string = base64.b64encode(bytes('%s:%s' % (auth_data[1], auth_data[2]), 'ascii'))
        request.add_header("Authorization", "Basic %s" % base64string.decode('utf-8'))
        result = urllib.request.urlopen(request)
        # print(result.info())
        data = json.loads(result.read().decode("utf-8"))
        all_data += data
        api_url = None
        # get next api_url for paginated data
        link_header = result.getheader('Link')
        # print(result.info())
        if link_header:
            # Splitting the Link header value to get individual links
            links = link_header.split(',')
            next_link = None
            for link in links:
                # Extracting URL and rel type
                parts = link.split(';')
                url = parts[0].strip()[1:-1]  # Remove < and >
                rel = parts[1].strip()
                if 'next' == rel:
                    next_link = url
                    break
            api_url = next_link
    print(json.dumps(all_data))

parser = argparse.ArgumentParser(
    prog='download-data.py',
    description='Download requested data from Fakturoid API and prints them to the output.',
)
parser.add_argument(
    '-t', '--type',
    required=True,
    choices=['invoices', 'expenses'],
    action='store',
    help='Choose a Fakturoid data type to download.'
)
parser.add_argument(
    '-s', '--since',
    action='store',
    help='Download since, e.g. 2021-01-01 (empty for no date).'
)
args = parser.parse_args()

match args.type:
    case 'invoices' | 'expenses':
        download_all('{}.json'.format(args.type), args.since)
