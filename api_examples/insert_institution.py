#!/bin/python2.7
# pip install requests
import argparse
import csv
import requests

# TODO: Load community and voivodeship


def insert_row(s, host, name, email, code):
    code = "%7d" % (int(code))
    code = code[:2] if code[2:] == '0' * 5 else code  # voivodeship
    response = s.post(url="%s/api/institutions/" % (host,), json={
        "name": name,
        "tags": ["wojewoda"],
        "jst": code,
        "email_set": [{'email': x} for x in email.split(',')]
    })
    if response.status_code == 200:
        print u"{name} saved as PK {status}".format(name=name, status=str(response.json()['pk']))
    else:
        print u"{name} response returned {status}".format(name=name, status=str(response.json()))


def fields_validation(fields):
    result = True
    for field_name in ['Organ', 'E-mail', 'TERC']:
        if 'TERC' not in fields:
            print("There is missing %s field. " % (field_name, ) +
                  "Required fields name is Organ, E-mail, TERC")
            result = False
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', nargs='?', type=argparse.FileType('r'),
                        help="Input CSV-file")
    parser.add_argument('--host',  nargs='?',
                        help="Host of instance")
    parser.add_argument('--user', nargs='?',
                        help="User to authentication")
    parser.add_argument('--password', nargs='?',
                        help="Password to authentication")
    parser.add_argument('--tags', '-t', nargs='+')
    args = parser.parse_args()

    s = requests.Session()
    s.auth = (args.user, args.password)

    reader = csv.DictReader(args.input)

    if not fields_validation(reader.fieldnames):
        print("Script stop, due previos erros.")
        return

    for row in reader:
        insert_row(s=s,
                   host=args.host,
                   name=unicode(row['Organ'], 'utf-8'),
                   email=unicode(row['E-mail'], 'utf-8'),
                   code=unicode(row['TERC'], 'utf-8'))


if __name__ == "__main__":
    main()
