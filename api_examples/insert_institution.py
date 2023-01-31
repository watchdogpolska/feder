#!/bin/python2.7
"""
A tool to insert institutions from CSV files.

Requirements:
 - requests

Example usage:

To run help text use:
$ python insert_institution.py -h

To insert prefiltered database use:
$ (cat /tmp/wojewodowie.csv | grep -E 'Wojewoda|TERC') | python insert_institution.py \
                                                        --host="http://localhost:8000" \
                                                        --user="xyz" \
                                                        --password="xyz" \
                                                        --tags="wojewoda" \
                                                        --input=-
"""

import argparse
import sys

import requests
import unicodecsv as csv


# TODO: Load community and voivodeship


def normalize_jst(code):
    code = "%07d" % (int(code))
    code = code[:2] if code[2:] == "0" * 5 else code  # voivodeship
    code = code[:4] if code[4:] == "0" * 3 else code  # community (TODO: Test)
    return code


def insert_row(s, host, name, email, code, tags):
    response = s.post(
        url=f"{host}/api/institutions/",
        json={"name": name, "tags": tags, "jst": code, "email": email},
    )
    if response.status_code == 500:
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
    if response.status_code == 201:
        print(name.encode("utf-8"), " created as PK", json["pk"])
    else:
        print(
            name.encode("utf-8"),
            "response ",
            response.status_code,
            ":",
            file=sys.stderr,
        )
        print(json, file=sys.stderr)


def fields_validation(fields):
    result = True
    for field_name in {"Organ", "E-mail", "TERC"} - set(fields):
        print(
            f"There is missing {field_name} field. "
            + "Required fields name is Organ, E-mail, TERC"
        )
        result = False
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input", required=True, type=argparse.FileType("r"), help="Input CSV-file"
    )
    parser.add_argument("--host", required=True, help="Host of instance")
    parser.add_argument("--user", required=True, help="User to authentication")
    parser.add_argument("--password", required=True, help="Password to authentication")
    parser.add_argument("-t", "--tags", required=True, nargs="+")
    args = parser.parse_args()

    s = requests.Session()
    s.auth = (args.user, args.password)
    reader = csv.DictReader(args.input)

    if not fields_validation(reader.fieldnames):
        print("Script stop, due previos erros.")
        return

    for row in reader:
        insert_row(
            s=s,
            host=args.host,
            name=row["Organ"],
            email=row["E-mail"],
            code=row["TERC"],
            tags=args.tags,
        )


if __name__ == "__main__":
    main()
