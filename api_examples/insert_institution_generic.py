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
$ python insert_institution_generic.py -h
"""

import argparse
import csv
import sys
from urllib.parse import urljoin

import requests
from gusregon import GUS
from insert_institution import normalize_jst
from utils import environ

if not bool(environ("GUSREGON_SANDBOX")):
    sys.stderr.write(
        "You are using sandbox mode for the REGON database. Data may be incorrect. "
        "Set the environemnt variable GUSREGON_API_KEY correctly."
    )


class Command:
    REQUIRED_FIELDS = ["name", "email", "tags"]

    def __init__(self, argv):
        self.argv = argv
        self.args = self.get_build_args(argv[1:])
        self.gus = GUS(
            api_key=(
                self.args.gusregon_api_key
                or environ("GUSREGON_API_KEY", required=False)
            ),
            sandbox=self.args.gusregon_sandbox,
        )
        self.s = requests.Session()
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
        parser.add_argument(
            "--gusregon-sandbox",
            required=False,
            help="GUS REGON sandbox mode (no API key needed)",
            dest="gusregon_sandbox",
            action="store_true",
            default=False,
        )
        parser.add_argument(
            "--gusregon-api-key",
            required=False,
            help="GUS REGON API KEY",
            dest="gusregon_api_key",
            action="store",
            default=None,
        )
        parser.add_argument(
            "--name-exact",
            required=False,
            help="Do institution name should match exact GUS data name?",
            dest="name_exact",
            action="store_true",
            default=False,
        )
        parser.add_argument(
            "--name-prefix",
            required=False,
            help="Prefix of the institution name which is expected to be the same",
            dest="name_prefix",
            action="store",
            default="",
        )
        parser.add_argument(
            "--name-suffix-field",
            required=False,
            help="In what field of GUS REGON data should institution suffix "
            "be looked for",
            dest="name_suffix_field",
            action="store",
            default=None,
        )
        parser.add_argument(
            "--simulate",
            required=False,
            help="Do not insert any data",
            dest="simulate",
            action="store_true",
            default=False,
        )
        parser.add_argument(
            "--explicit",
            required=False,
            help="Prints detailed data of the institution if GUS data "
            "validation fails.",
            dest="explicit",
            action="store_true",
            default=False,
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

    def _print_gus_data(self, name, gus_data):
        print(f'GUS data for institution "{name}":')
        for key, val in gus_data.items():
            if val:
                print(f" - {key}: {val}")
        print()

    def insert_row(  # noqa: C901
        self, host, name, email, tags, regon=None, regon_parent=None, **extra
    ):
        data = {"name": name, "tags": tags.split(","), "email": email}

        regon_data = None
        if regon:
            # REGON normalization
            regon = regon.strip(".").strip().rjust(9, "0")
            regon_data = self.gus.search(regon=regon)

            if not regon_data:
                raise Exception("Invalid REGON data", regon, name)

            regon_data_name = regon_data.get("nazwa", "?").upper()

            if self.args.name_exact and name.upper() != regon_data_name:
                print(
                    'Warning! GUS name "{}" does not match '
                    'institution name "{}"'.format(regon_data_name, name.upper())
                )
                if self.args.explicit:
                    self._print_gus_data(name, regon_data)

            if (
                self.args.name_prefix
                and self.args.name_prefix.upper() not in regon_data_name
            ):
                print(
                    'Warning! GUS name "{}" does not contain '
                    'expected prefix "{}".'.format(
                        regon_data_name, self.args.name_prefix.upper()
                    )
                )
                if self.args.explicit:
                    self._print_gus_data(name, regon_data)

            # this is dynamic name part after removing constant prefix
            expected_suffix = (
                name.upper().replace(self.args.name_prefix.upper(), "").strip()
            )
            regon_suffix = regon_data.get(self.args.name_suffix_field, "").upper()

            if self.args.name_suffix_field and expected_suffix not in regon_suffix:
                print(
                    'Warning! GUS field "{}" does not contain '
                    'expected value "{}" but "{}".'.format(
                        self.args.name_suffix_field, expected_suffix, regon_suffix
                    )
                )
                if self.args.explicit:
                    self._print_gus_data(name, regon_data)

        else:
            raise Exception(
                'Regon value is missing in input file for institution: "{}".'.format(
                    name
                )
            )

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

        response = None

        if regon:
            pk = self._match(host, regon=regon)

            if pk:
                data.update({"id": pk})
                if not self.args.simulate:
                    response = self.s.patch(
                        url=urljoin(urljoin(host, "/api/institutions/"), str(pk) + "/"),
                        json=data,
                    )
                else:
                    print(f"Simulated PATCH for {name}\n")
            else:
                if not self.args.simulate:
                    response = self.s.post(
                        url=urljoin(host, "/api/institutions/"), json=data
                    )
                else:
                    print(f"Simulated POST for {name}\n")
        else:
            if not self.args.simulate:
                response = self.s.post(
                    url=urljoin(host, "/api/institutions/"), json=data
                )
            else:
                print(f"Simulated POST for {name}\n")

        if response and response.status_code >= 300:
            print(
                'Institution: "{}"; response status: {}.\n'.format(
                    name, response.status_code
                ),
                file=sys.stderr,
            )
            print(response.text, file=sys.stderr)
            return

        self.done_count += 1
        progress = (self.done_count / self.total_count) * 100

        if response:
            json = response.json()
            if response.status_code == 201:
                print(progress, name, " created as PK", json["pk"])
            elif response.status_code == 200:
                print(progress, name, " updated as PK", json["pk"])
            else:
                print(
                    progress,
                    name,
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
                f"There is missing {field_name} field. "
                + f"Required fields name is {self.REQUIRED_FIELDS}"
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
