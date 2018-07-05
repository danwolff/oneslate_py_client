#! /Users/dwolff/oneslate/py_client/py3env/bin/python3

'''
Test importing and calling the oneslate.py module.
'''

import oneslate as o

server = 'https://requests-dev6.1s.com'
title = "The import and function call worked."

session, token = o.get_session(server)
added = o.add_node(server, session, token, title)

print("{added}".format(**locals()))
