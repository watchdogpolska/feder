#!/bin/python2.7
# -*- coding: utf-8 -*-
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
from __future__ import print_function, unicode_literals

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

requests_cache.configure()


if not bool(environ('GUSREGON_SANDBOX')):
    sys.stderr.write("You are using sandbox mode for the REGON database. Data may be incorrect. "
                     "Set the environemnt variable GUSREGON_API_KEY correctly.")


class Command(object):
    JST_VOIVODESHIP_KEYS = ['adsiedzwojewodztwo_symbol', 'adkorwojewodztwo_symbol']
    JST_COUNTY_KEYS = ['adsiedzpowiat_symbol', 'adkorpowiat_symbol', ]
    JST_COMMUNITY_KEYS = ["adsiedzgmina_symbol", 'adkorgmina_symbol', ]
    REQUIRED_FIELDS = ['parent__name', 'name', 'district', 'appeal', 'street',
                       'postcode', 'phone', 'fax', 'email', 'active', 'regon']

    def __init__(self, argv):
        self.gus = GUS(api_key=os.environ('GUSREGON_API_KEY'), sandbox=os.environ('GUSREGON_SANDBOX', True))
        self.s = requests.Session()
        self.argv = argv
        self.args = self.get_build_args(argv[1:])
        self.s.auth = (self.args.user, self.args.password)

    def get_build_args(self, argv):
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
        return parser.parse_args(argv)

    def _get_jst_id(self, data):
        for a, b, c in zip(self.JST_VOIVODESHIP_KEYS,
                           self.JST_COUNTY_KEYS,
                           self.JST_COMMUNITY_KEYS):
            if a in data and b in data and c in data:
                value = data[a] + data[b] + data[c]
                if value:
                    return value

    def _get_court(self, host, name):
        response = self.s.get(url=urljoin(host, "/api/institutions/"), params={'name': name}).json()
        if not response['results']:
            import ipdb; ipdb.set_trace();
        return response['results'][0]['pk']

    def insert_row(self, host, name, email, regon, **extra):
        data = self.gus.search(regon=regon)
        if not data:
            print("Unable find REGON {} for {}".format(regon, name), file=sys.stderr)
            return

        tags = []
        for keyword in ['Sąd Apelacyjny', 'Sąd Okręgowy', 'Sąd Rejonowy']:
            if keyword in name:
                tags = ['Sąd', keyword]

        data = {
            "name": name,
            "tags": tags,
            "jst": normalize_jst(self._get_jst_id(data)),
            "email": email,
            "extra": {'db': extra, 'regon': data},
            "regon": regon
        }
        response = self.s.post(url=urljoin(host, "/api/institutions/"), json=data)
        if response.status_code == 500:
            print(name.encode('utf-8'), " response 500", response.status_code, ":", file=sys.stderr)
            print(response.text, file=sys.stderr)
            return
        json = response.json()

        if response.status_code == 400 and json.keys() == ['regon']:
            court = self._get_court(host, name)
            parent_court = self._get_court(host, extra['parent__name'])
            url = urljoin(host, "/api/institutions/{}/".format(court))
            data['parents_ids'] = [parent_court]
            self.s.patch(url, json=data)
            if response.status_code == 500:
                print(name.encode('utf-8'), " response 500", response.status_code, ":", file=sys.stderr)
                print(response.text, file=sys.stderr)
                return

        if response.status_code == 201:
            print(name.encode('utf-8'), " created as PK", json['pk'])
        else:
            print(name.encode('utf-8'), "response ", response.status_code, ":", file=sys.stderr)
            print(json, file=sys.stderr)

    def update_parent(self, host, parent__name, name, **extra):
        court = self._get_court(host, name)
        parent_court = self._get_court(host, parent__name)
        if not parent_court:
            print(u"Unable to find parent court for {}".format(name))
            return
        url = urljoin(host, "/api/institutions/{}/".format(court))
        params = {'parents_ids': [parent_court]}

    def fields_validation(self, fields):
        result = True
        for field_name in set(self.REQUIRED_FIELDS) - set(fields):
            print("There is missing %s field. " % (field_name,) +
                  "Required fields name is {}".format(self.REQUIRED_FIELDS))
            result = False
        return result

    def run(self):
        reader = csv.DictReader(self.args.input)

        if not self.fields_validation(reader.fieldnames):
            print("Script stop, due previos erros.")
            return
        data = list(reader)
        with trange(len(data) * 2, leave=True) as t:
            for row in data:
                self.insert_row(host=self.args.host, **row)
                t.set_description(row['name'])
                t.update(1)
            for row in data:
                t.set_description(row['name'])
                self.update_parent(host=self.args.host, **row)
                t.update(1)


if __name__ == "__main__":
    Command(sys.argv).run()
