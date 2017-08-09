#!/bin/python2.7
"""
A tool to insert institutions from CSV files.

Requirements:
 - requests
 - gusregon
 - unicodecsv
 - tqdm

Example usage:

To run help text use:
$ python insert_court.py -h
"""
from __future__ import print_function

import argparse
import os
import sys

import requests
import requests_cache
import unicodecsv as csv
from gusregon import GUS
from tqdm import trange

from insert_institution import normalize_jst

try:
    from urlparse import urljoin
except ImportError:
    from urllib.parse import urljoin

REQUIRED_FIELDS = ['parent__name', 'name', 'district', 'appeal', 'street',
                   'postcode', 'phone', 'fax', 'email', 'active', 'regon']

requests_cache.configure()


def environ(key, bool=False):
    if key not in os.environ:
        sys.stderr.write("Set the environemnt variable {} correctly. It's required!".format(key))
        sys.exit(2)
    if bool:
        return os.environ[key].lower() == 'true'
    return os.environ[key]


if not bool(environ('GUSREGON_SANDBOX')):
    sys.stderr.write("You are using sandbox mode for the REGON database. Data may be incorrect. "
                     "Set the environemnt variable GUSREGON_API_KEY correctly.")
gus = GUS(api_key=environ('GUSREGON_API_KEY'), sandbox=environ('GUSREGON_SANDBOX', True))
s = requests.Session()

JST_VOIVODESHIP_KEYS = ['adsiedzwojewodztwo_symbol', 'adkorwojewodztwo_symbol']
JST_COUNTY_KEYS = ['adsiedzpowiat_symbol', 'adkorpowiat_symbol', ]
JST_COMMUNITY_KEYS = ["adsiedzgmina_symbol", 'adkorgmina_symbol', ]


def get_jst_id(data):
    for a, b, c in zip(JST_VOIVODESHIP_KEYS, JST_COUNTY_KEYS, JST_COMMUNITY_KEYS):
        if a in data and b in data and c in data:
            value = data[a] + data[b] + data[c]
            if value:
                return value


def get_court(host, name):
    response = s.get(url=urljoin(host, "/api/institutions/"), params={'name': name}).json()
    if not response['results']:
        import ipdb; ipdb.set_trace();
    return response['results'][0]['pk']


def insert_row(host, name, email, regon, tags, **extra):
    data = gus.search(regon=regon)
    if not data:
        print("Unable find REGON {} for {}".format(regon, name), file=sys.stderr)
        return
    response = s.post(url=urljoin(host, "/api/institutions/"), json={
        "name": name,
        "tags": tags,
        "jst": normalize_jst(get_jst_id(data)),
        "email": email,
        "extra": extra,
        "regon": regon
    })
    if response.status_code == 500:
        print(name.encode('utf-8'), " response 500", response.status_code, ":", file=sys.stderr)
        print(response.text, file=sys.stderr)
        return

    json = response.json()
    if response.status_code == 201:
        print(name.encode('utf-8'), " created as PK", json['pk'])
    else:
        print(name.encode('utf-8'), "response ", response.status_code, ":", file=sys.stderr)
        print(json, file=sys.stderr)


def update_row(host, parent__name, name, **extra):
    court = get_court(host, name)
    parent_court = get_court(host, parent__name)
    if not parent_court:
        print(u"Unable to find parent court for {}".format(name))
        return
    url = urljoin(host, "/api/institutions/{}/".format(court))
    params = {'parents_ids': [parent_court]}


def fields_validation(fields):
    result = True
    for field_name in set(REQUIRED_FIELDS) - set(fields):
        print("There is missing %s field. " % (field_name,) +
              "Required fields name is {}".format(REQUIRED_FIELDS))
        result = False
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input',
                        required=True,
                        type=argparse.FileType('r'),
                        help="Input CSV-file")
    parser.add_argument('--host',
                        required=True,
                        help="Host of instance")
    parser.add_argument('--user',
                        required=True,
                        help="User to authentication")
    parser.add_argument('--password',
                        required=True,
                        help="Password to authentication")
    parser.add_argument('-t', '--tags',
                        required=True,
                        nargs='+')
    args = parser.parse_args()
    s.auth = (args.user, args.password)

    reader = csv.DictReader(args.input)

    if not fields_validation(reader.fieldnames):
        print("Script stop, due previos erros.")
        return
    data = list(reader)
    with trange(len(data) * 2, leave=True) as t:
        for row in data:
            t.set_description(row['name'])
            t.update(1)
        for row in data:
            t.set_description(row['name'])
            update_row(host=args.host, **row)
            t.update(1)

if __name__ == "__main__":
    main()
