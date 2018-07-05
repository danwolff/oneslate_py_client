#! /Users/dwolff/oneslate/py_client/py3env/bin/python3

'''
Test importing and calling the oneslate.py module.
'''

import oneslate as o

server = 'https://1s-dev.example.com/'
title = "The import and function call worked."
usr = 'bot@example.com'
pwd = 'password'

session, token = o.get_session(server, None, usr, pwd)
added = o.add_node(server, session, token, title)

print("{added}".format(**locals()))
