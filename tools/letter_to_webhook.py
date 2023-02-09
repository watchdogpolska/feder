import os
import sys
import time
import json
import requests
import mailparser
import argparse

tools_dir = os.path.dirname(__file__)
sys.path.insert(0, tools_dir)

from mail_parser import serialize_mail, get_message, get_manifest

# print(tools_dir)

description = """
Send email from eml file to feder webhook for registration or webhook test.
"""
url_help = """
webhook url example: http://localhost:8000/listy/webhook?secret=my-strong-secret 
"""
file_help = """
file example: /code/feder/media_prod/messages/2022/04/03/c6ceae935fed401bae7d12da3be6c775.eml.gz
"""

def main():
    parser = argparse.ArgumentParser(description=description, add_help=True)
    parser.add_argument("--url", help=url_help, required=True)
    parser.add_argument("--file", help=file_help, required=True)
    try:
        args = vars(parser.parse_args())
    except argparse.ArgumentError:
        parser.print_help()
    print(args)
    process_msg(msg_file=args["file"], webhook_url=args["url"])


def process_msg(msg_file, webhook_url):
    print(f"Eml file to processs: {msg_file}")
    msg_content = get_message(msg_file)
    mail = mailparser.parse_from_bytes(msg_content)
    body = get_manifest(mail, False)
    # json.dump(body, sys.stdout, indent=4)
    start = time.time()
    email_body = serialize_mail(msg_content, compress_eml=True)
    msg_headers = body.get("headers") or {}
    msg_id = msg_headers.get("message_id")
    end = time.time()
    print(f"Message {msg_id} serialized in {end - start} seconds")
    res = requests.post(webhook_url, files=email_body)
    print("Received response:", res.text)
    res.raise_for_status()
    response_txt = json.dumps(res.json(), indent=2)
    print("Full response: ", response_txt, "\n")


if __name__ == "__main__":
    main()
