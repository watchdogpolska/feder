import os
import sys
sys.path.insert(0, '/code/tools')
import time
import json
print(os. getcwd())
from mail_parser import serialize_mail, get_message, get_manifest

import requests
import mailparser


webhook = 'http://localhost:8000/listy/webhook?secret=my-strong-secret'
def main():
    # total arguments
    n = len(sys.argv)
    print("Total arguments passed:", n)
    
    # Arguments passed
    print("\nName of Python script:", sys.argv[0])
    
    print("\nArguments passed:", end = "\n")
    for i in range(1, n):
        print(sys.argv[i], end = "\n")
    msg = get_message(sys.argv[i])
    process_msg(msg)
    # config = get_config(os.environ)
    # session = requests.Session()
    # print("Configuration: ", config)
    # if config["sentry_dsn"]:
    #     try:
    #         loop(config, session)
    #     except Exception as e:
    #         sentry_sdk.capture_exception(e)
    # else:
    #     loop(config, session, None)


def process_msg(msg):
    print(msg)
    mail = mailparser.parse_from_bytes(msg)
    body = get_manifest(mail, False)
    json.dump(body, sys.stdout, indent=4)
    start = time.time()
    email_body = serialize_mail(msg, compress_eml=True)
    msg_headers = body.get("headers") or {}
    msg_id = msg_headers.get("message_id")
    end = time.time()
    print("Message serialized in {} seconds".format(end - start))
    res = requests.post(webhook, files=email_body)
    print("Received response:", res.text)
    res.raise_for_status()
    response = res.json()



if __name__ == "__main__":
    main()
