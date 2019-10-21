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
from __future__ import print_function, unicode_literals, division

import argparse
import sys

import requests
import unicodecsv as csv
from gusregon import GUS

from utils import environ
from insert_institution import normalize_jst

from urllib.parse import urljoin


if not bool(environ("GUSREGON_SANDBOX")):
    sys.stderr.write(
        "You are using sandbox mode for the REGON database. Data may be incorrect. "
        "Set the environemnt variable GUSREGON_API_KEY correctly."
    )


class Command(object):
    REQUIRED_FIELDS = ["name", "email", "tags"]

    def __init__(self, argv):
        self.gus = GUS(
            api_key=environ("GUSREGON_API_KEY"),
            sandbox=environ("GUSREGON_SANDBOX", True),
        )
        self.s = requests.Session()
        self.argv = argv
        self.args = self.get_build_args(argv[1:])
        self.s.auth = (self.args.user, self.args.password)
        self.done_count = 0
        self.total_count = None

    def get_build_args(self, argv):
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "--input", required=True, type=argparse.FileType("r"), help="Input CSV-file"
        )
        parser.add_argument("--host", required=True, help="Host of instance")
        parser.add_argument("--user", required=True, help="User to authentication")
        parser.add_argument(
            "--password", required=True, help="Password to authentication"
        )
        return parser.parse_args(argv)

    def _match(self, host, **query):
        response = self.s.get(url=urljoin(host, "/api/institutions/"), params=query)
        data = response.json()
        return data["results"][0]["pk"] if data["results"] else None

    def _find(self, host, **query):
        response = self.s.get(url=urljoin(host, "/api/institutions/"), params=query)
        data = response.json()
        if not data.get("results") or len(data["results"]) != 1:
            import ipdb

            ipdb.set_trace()
        return data["results"][0]["pk"]

    def insert_row(
        self, host, name, email, tags, regon=None, regon_parent=None, **extra
    ):
        regon_data = None
        if regon:
            regon = regon.strip(">").strip("*").strip()
            regon_data = self.gus.search(regon=regon)
            if not regon_data:
                raise Exception("Invalid regon data", regon, name)
        data = {"name": name, "tags": tags.split(","), "email": email}

        if regon:
            data.update({"regon": regon})

        terc = None
        if "terc" in extra:
            terc = extra.get("terc")
            data.update({"jst": normalize_jst(terc), "extra": {"regon": regon_data}})
        if not terc and regon_data:
            terc = "".join(
                [
                    regon_data["adsiedzwojewodztwo_symbol"],
                    regon_data["adsiedzpowiat_symbol"],
                    regon_data["adsiedzgmina_symbol"],
                ]
            )
        if not terc:
            raise Exception("Missing terc and unable to found", name)

        data.update({"jst": normalize_jst(terc)})

        if regon_data:
            data.update({"extra": {"regon": regon_data}})

        if regon_parent:
            data.update({"parents_ids": [self._find(host, regon=regon_parent)]})

        if regon:
            pk = self._match(host, regon=regon)

            if pk:
                data.update({"id": pk})
                response = self.s.patch(
                    url=urljoin(urljoin(host, "/api/institutions/"), str(pk) + "/"),
                    json=data,
                )
            else:
                response = self.s.post(
                    url=urljoin(host, "/api/institutions/"), json=data
                )
        else:
            response = self.s.post(url=urljoin(host, "/api/institutions/"), json=data)
        if response.status_code >= 300:
            print(
                name.encode("utf-8"),
                " response 500",
                response.status_code,
                ":",
                file=sys.stderr,
            )
            print(response.text, file=sys.stderr)
            return
        json = response.json()
        self.done_count += 1
        progress = (self.done_count / self.total_count) * 100
        if response.status_code == 201:
            print(progress, name.encode("utf-8"), " created as PK", json["pk"])
        elif response.status_code == 200:
            print(progress, name.encode("utf-8"), " updated as PK", json["pk"])
        else:
            print(
                progress,
                name.encode("utf-8"),
                "response ",
                response.status_code,
                ":",
                file=sys.stderr,
            )
            print(json, file=sys.stderr)

    def fields_validation(self, fields):
        result = True
        for field_name in set(self.REQUIRED_FIELDS) - set(fields):
            print(
                "There is missing %s field. " % (field_name,)
                + "Required fields name is {}".format(self.REQUIRED_FIELDS)
            )
            result = False
        return result

    def run(self):
        reader = csv.DictReader(self.args.input)

        if not self.fields_validation(reader.fieldnames):
            print("Script stop, due previos erros.")
            return 5
        data = list(reader)
        self.total_count = len(data)
        for row in data:
            self.insert_row(host=self.args.host, **row)


if __name__ == "__main__":
    sys.exit(Command(sys.argv).run())
