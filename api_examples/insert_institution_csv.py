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
import sys

import requests
import csv
from gusregon import GUS

from utils import environ
from insert_institution import normalize_jst

from urllib.parse import urljoin


class ScriptError(Exception):
    pass


class Command:
    REQUIRED_FIELDS = ["name", "email", "regon", "tags"]
    FIELDS_MAP = {
        # Fields which are processed with their alternate names
        "obj_id": "Id",
        "name": "Nazwa",
        "email": "Adres e-mail instytucji",
        "regon": "Kod REGON",
        "jst": "JST id",
        "tags": "Nazwy tagów",
    }

    def __init__(self, argv):
        self.argv = argv
        self.args = self.get_build_args(argv[1:])

        if self.args.gusregon_sandbox:
            sys.stderr.write(
                "You are using sandbox mode for the REGON database. "
                "Data may be incorrect. "
            )

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
        self.tags = self._get_tags()

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
        parser.add_argument(
            "--create-missing-tags",
            required=False,
            help="Creates nonexistent tags, if not set the script will be stopped "
            "after failed attempt of finding tag with given name.",
            dest="create_tags",
            action="store_true",
            default=False,
        )
        return parser.parse_args(argv)

    def _match(self, host, **query):
        response = self.s.get(url=urljoin(host, "/api/institutions/"), params=query)
        data = response.json()
        return data["results"][0]["pk"] if data["results"] else None

    def _get_tags(self):
        response = self.s.get(
            url=urljoin(self.args.host, "/api/tags/"), params={"page_size": 10000}
        )
        data = response.json()
        return data["results"]

    def _find_tag(self, name):
        for tag in self.tags:
            if tag["name"] == name:
                return tag
        return None

    def _print_gus_data(self, name, gus_data):
        print('GUS data for institution "{}":'.format(name))
        for key, val in gus_data.items():
            if val:
                print(" - {}: {}".format(key, val))
        print()

    def _normalize_row(self, **data):
        def _get_val(f_name):
            return (
                data.get(f_name) or data.get(self.FIELDS_MAP[f_name])
                if f_name in self.FIELDS_MAP
                else None
            )

        mapped = {}
        for field_name in self.FIELDS_MAP.keys():
            mapped[field_name] = _get_val(field_name)

        tag_names = [tag.strip() for tag in mapped["tags"].split("|")]
        mapped["tags"] = []

        for tag_name in tag_names:
            tag = self._find_tag(tag_name)
            if tag:
                mapped["tags"].append(tag["name"])
            else:
                print('Warning! Found nonexistent tag named "{}".'.format(tag_name))

                if not self.args.create_tags:
                    raise ScriptError(
                        'Missing tag named "{}" with --create-tags flag turned off. '
                        "The script will be terminated.".format(tag_name),
                    )
                else:
                    mapped["tags"].append(tag_name)

        return mapped

    def _get_and_validate_regon_data(self, data):
        regon_data = self.gus.search(regon=data["regon"])

        if not regon_data:
            raise ScriptError(
                'Regon {} for institution "{}" has not been found '
                "in GUS database.".format(data["regon"], data["name"])
            )

        regon_data_name = regon_data.get("nazwa", "?").upper()

        if self.args.name_exact and data["name"].upper() != regon_data_name:
            print(
                'Warning! GUS name "{}" does not match '
                'institution name "{}"'.format(regon_data_name, data["name"].upper())
            )
            if self.args.explicit:
                self._print_gus_data(data["name"], regon_data)

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
                self._print_gus_data(data["name"], regon_data)

        # this is dynamic name part after removing constant prefix
        expected_suffix = (
            data["name"].upper().replace(self.args.name_prefix.upper(), "").strip()
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
                self._print_gus_data(data["name"], regon_data)

        return regon_data

    def _get_terc(self, data, extra, jst, regon_data):
        if "terc" in extra:
            terc = extra.get("terc")

        elif regon_data:
            terc = "".join(
                [
                    regon_data["adsiedzwojewodztwo_symbol"],
                    regon_data["adsiedzpowiat_symbol"],
                    regon_data["adsiedzgmina_symbol"],
                ]
            )
            if normalize_jst(jst) != normalize_jst(terc):
                print(
                    'Warning! Row JST: "{}" differs from GUS JST: "{}" '
                    'for institution "{}"'.format(jst, terc, data["name"])
                )
                if self.args.explicit:
                    self._print_gus_data(data["name"], regon_data)

        elif jst:
            terc = jst

        else:
            raise ScriptError("Missing terc and unable to find.", data["name"])

        return terc

    def _handle_api_response(self, response, data, progress):
        json = response.json()
        if response.status_code == 201:
            print(
                '{:6.2f}%: "{}" created as PK {}'.format(
                    progress, data["name"], json["pk"]
                )
            )
        elif response.status_code == 200:
            print(
                '{:6.2f}%: "{}" updated as PK {}'.format(
                    progress, data["name"], json["pk"]
                )
            )
        else:
            print(
                '{:6.2f}%: "{}" Response status code: {}.'.format(
                    progress, data["name"], response.status_code
                ),
                file=sys.stderr,
            )
            print(json, file=sys.stderr)

    def _push_to_api(self, data, regon_data, obj_id):
        response = None

        if obj_id:
            pk = obj_id
        elif data["regon"]:
            pk = self._match(self.args.host, regon=data["regon"])
        else:
            pk = None

        if pk:
            data.update({"id": pk})
            if not self.args.simulate:
                response = self.s.patch(
                    url=urljoin(self.args.host, "/api/institutions/{}/".format(pk)),
                    json=data,
                )
            else:
                print('Simulated PATCH for "{}"\n'.format(data["name"]))

        else:
            if not self.args.simulate:
                response = self.s.post(
                    url=urljoin(self.args.host, "/api/institutions/"), json=data
                )
            else:
                print('Simulated POST for "{}"\n'.format(data["name"]))

        if response is not None and response.status_code >= 300:
            error_msg = 'Error! Institution: "{}" got response status: {}.'.format(
                data["name"], response.status_code
            )
            print(error_msg, file=sys.stderr)
            print(response.text, file=sys.stderr)
            if self.args.explicit:
                self._print_gus_data(data["name"], regon_data)
            raise ScriptError(error_msg)

        self.done_count += 1
        progress = (self.done_count / self.total_count) * 100

        if response:
            self._handle_api_response(response, data, progress)

    def insert_row(self, host, obj_id, name, email, regon, jst, tags, **extra):
        data = {"name": name, "email": email, "tags": tags}

        if regon:
            regon = regon.strip(".").strip().rjust(9, "0")
            data["regon"] = regon
            regon_data = self._get_and_validate_regon_data(data)
        else:
            regon_data = None

        terc = self._get_terc(data, extra, jst, regon_data)
        data["jst"] = normalize_jst(terc)

        if regon_data:
            data["extra"] = {"regon": regon_data}

        regon_parent = extra.get("regon_parent")
        if regon_parent:
            matched_parent = [self._match(host, regon=regon_parent)]
            if matched_parent is None:
                raise ScriptError(
                    "Parent institution with REGON {} not found".format(regon_parent)
                )
            data["parents_ids"] = [matched_parent]

        self._push_to_api(data, regon_data, obj_id)

    def fields_validation(self, fields):
        recog_fields = []
        for field in fields:
            if field in self.REQUIRED_FIELDS or field in self.FIELDS_MAP.values():
                recog_fields.append(field)

        result = True
        for req_field in self.REQUIRED_FIELDS:
            if req_field not in fields and self.FIELDS_MAP.get(req_field) not in fields:
                alt_name = ""
                for key, val in self.FIELDS_MAP.items():
                    if val == req_field:
                        alt_name += ' or "{}"'.format(key)
                print(
                    "There is missing column in the input file. "
                    'Required field\'s name is "{}"{}'.format(req_field, alt_name),
                    file=sys.stderr,
                )
                result = False
        return result

    def run(self):
        reader = csv.DictReader(self.args.input)

        if not self.fields_validation(reader.fieldnames):
            print("Script stop, due previos erros.", file=sys.stderr)
            return 5

        data = list(reader)
        self.total_count = len(data)
        for row in data:
            normalized_row = self._normalize_row(**row)
            self.insert_row(host=self.args.host, **normalized_row)


if __name__ == "__main__":
    sys.exit(Command(sys.argv).run())
