#! /Users/dwolff/oneslate/py_client/py3env/bin/python3
"""
Handles actions for command line or Pythonic Oneslate interaction.

Usage:
  oneslate.py [options] add_node <title>
  oneslate.py [options] search_nodes <title>
  oneslate.py [options] node_details <node_id> 
  oneslate.py [options] node_stats <node_id> 
  oneslate.py [options] rate_node <node_id> <validity> 
  oneslate.py [options] link_support <node_id> <support_node_id> 
  oneslate.py [options] link_conclusion <node_id> <conclusion_node_id> 
  oneslate.py [options] relegate_node <node_id> <confirmation>
  oneslate.py [options] list_supports <root_node_id>
  oneslate.py [options] edit_node <node_id> <new_title>
  oneslate.py -h | --help
  oneslate.py --version

Options:
  -h, --help                          Show this screen.
  -s <host>, --server <host>          URL of server [default: https://1s-dev.example.com].
  -u <username>, --user <username>    Username to fall back in if no valid cookies [default: bot@example.com].
  -p <password>, --pass <password>    Password to fall back on if no valid session from cookies provided.
  -i <file>, --input=<file>           Cookies input file.
  -o <file>, --output=<file>          Cookies output file.
  -r <validity>, --rating=<validity>  Rating to give node.
  -q, --quiet                         Print less text.
  --verbose                           Print more text.
  --debug                             Print debug level text.
  --version                           Show version.

Arguments:
    validity: 0 - none
              1 - low 
              2 - mid
              3 - high
              4 - full
    confirmation:
              confirm - do execute this (only used to confirm relegate_node actions)
"""

import logging
import pickle
import random
import requests
import json

from bs4 import BeautifulSoup
from docopt import docopt

# Configure certificate verification as needed
cert_in_use = True                                                        # Verify for secure setups
# cert_in_use = False                                                     # Do not verify (for insecure setups)
# cert_in_use = '/Users/name/certs/charles-ssl-proxying-certificate.pem'  # Proxy for development

def get_login_url(host):
    login_url = '{host}/users/sign_in'.format(**locals())
    return login_url

def get_node_url(host):
    node_url = '{host}/nodes'.format(**locals())
    return node_url 

def get_tree_url(host):
    tree_url = '{host}/trees'.format(**locals())
    return tree_url 

def get_session(server, existing_cookies_file=None):
    login_url = get_login_url(server)
    session_to_use = requests.Session()
    # read cookies if available
    if existing_cookies_file:
        with open(existing_cookies_file, 'rb') as file_to_load:
            cookies = pickle.load(file_to_load)
            cookiejar = requests.cookies.RequestsCookieJar()
            cookiejar._cookies = cookies 
            session_to_use.cookies = cookiejar
    # load login URL
    page = session_to_use.get(login_url, timeout=1, verify=False)
    logging.debug(page.content)
    page_soup = BeautifulSoup(page.content, 'html.parser')
    # try to get csrf-token to show already logged in
    try:
        xcsrf_token = page_soup.select('meta[name="csrf-token"]')[0]['content'] 
        if xcsrf_token != None:
            # Already logged in, no need to log in again, just return session
            logging.info("Provided session appears valid.  Going to try "
                         "to reuse it.")
    except:
        logging.info("Did not appear to have valid current session. About to "
                     "try logging in for a new session.")
        # Could not get csrf-token, not logged in yet, so log in freshly.
        token = page_soup.select('input[name="authenticity_token"]')[0]['value']
        logging.debug("token = " + token)
        payload = {
            'utf8': '✓',
            'authenticity_token': token,
            'private_user[email]': 'info@oneslate.com',
            'private_user[password]': 'Admin2013',
            'private_user[remember_me]': '1',
            'commit': 'Sign in',
        }
        r = session_to_use.post(login_url, data=payload, timeout=1, verify=False)
        logging.debug(r.content)
        logging.debug("status code returned = " + str(r.status_code))

        xcsrf_soup = BeautifulSoup(r.content, 'html.parser')
        xcsrf_token = xcsrf_soup.select('meta[name="csrf-token"]')[0]['content'] 
    finally:
        logging.debug("xcsrf_token = {xcsrf_token}".format(**locals()))
    return session_to_use, xcsrf_token

def save_session(session_to_save, file_to_save_to=None):
    session_to_use = requests.Session()
    if file_to_save_to:
        with open(file_to_save_to, 'wb') as pickle_file:
            pickle.dump(session_to_save.cookies._cookies, pickle_file)
        logging.debug("Tried saving cookies to {file_to_save_to}".format(**locals()))
    return None 

def add_node(server, s, xcsrf_token, title_to_add):
    node_url = get_node_url(server)
    title_text = str(title_to_add)
    title_length = len(title_text)
    if title_length <= 0:
        logging.warning("Title length of {title_length} too short. Not trying"
                        " to add node.")
        return False 
    # with requests.Session() as s:

    the_explan = 'This node posted via automation in oneslate.py v0.0.1-dev.'
    node_data = {
        "title": title_text,
        "explanation": the_explan,
        "created_at": "",
        "username": "",
        "flags_count": "",
        "ratings_count": "",
        "parents_count": "",
        "children_count": "",
        "relegated": False,
        "media": "false",
        "type": None,
        "sources": []
    }
    s.headers.update({"X-CSRF-Token": xcsrf_token})
    logging.debug("xcsrf_token = " + xcsrf_token)
    request_node  = s.post(node_url, json=node_data, timeout=1, verify=cert_in_use)
    logging.debug(request_node.content)
    logging.info("status code returned = " + str(request_node.status_code))
    if request_node.status_code == 201:  # HTTP 201 Created
        return True 
    else:
        return None

def search_nodes(server, s, xcsrf_token, search_string):
    node_url = get_node_url(server)
    query = search_string
    logging.debug("query = " + query)
    query_params = {
        "term": query,
        "filter": "title"
    }
    s.headers.update({"X-CSRF-Token": xcsrf_token})
    query_response = s.get(node_url, data=query_params, timeout=1, verify=cert_in_use)
    results_data = json.loads(query_response.text)
    logging.debug(results_data)
    logging.debug("status code returned = " + str(query_response.status_code))
    print(
        "Search results for node title: {query}\n"
        "node_id | node_title\n"
        "--------+-----------------------------------------------------------"
        "".format(**locals()))
    for result in results_data:
        id = result['id']
        title = result['title']
        print('{0: <8}'.format(id) + "| {title}".format(**locals()))
    if query_response.status_code == 200:  # HTTP 200 OK
        return True 
    else:
        return None

def get_node_details(server, s, xcsrf_token, node_id):
    logging.debug("node_id = {node_id}".format(**locals()))
    details_params = {
        "view": "detail"
    }
    node_url = get_node_url(server)
    node_details_url = node_url + "/{node_id}.json".format(**locals())
    s.headers.update({"X-CSRF-Token": xcsrf_token})
    query_response = s.get(node_details_url, params=details_params, 
            timeout=1, verify=cert_in_use)
    results_data = json.loads(query_response.text)
    logging.debug(results_data)
    logging.debug("status code returned = " + str(query_response.status_code))
    id = results_data['id']
    rating = results_data['rating']
    title = results_data['title']
    media = results_data['media']
    type = results_data['type']
    flagged = results_data['flagged']
    followed = results_data['followed']
    explanation = results_data['explanation']
    created_at = results_data['created_at']
    username = results_data['username']
    rating_counts = results_data['rating_counts']
    ratings_count = results_data['ratings_count']
    current_user_author = results_data['current_user_author']
    communities = results_data['communities']
    sources = results_data['sources']
    # May not get back any key/value pair for time series unless ratings exist
    if int(ratings_count) > 0:
      ratings_time_series = results_data['ratings_time_series']
    print(
        "Details for node_id: {node_id}\n"
        "detail              | value\n"
        "--------------------+-----------------------------------------------\n"
        "id                  | {id}\n"  
        "title               | {title}\n"  
        "rating              | {rating}\n"  
        "explanation         | {explanation}\n"  
        "media               | {media}\n"  
        "type                | {type}\n"  
        "flagged             | {flagged}\n"  
        "followed            | {followed}\n"  
        "created_at          | {created_at}\n"  
        "username            | {username}\n"  
        "rating_counts       | {rating_counts}\n"  
        "ratings_count       | {ratings_count}\n"  
        "current_user_author | {current_user_author}\n"  
        "communities         | {communities}\n"  
        "sources             | {sources}"  
        "".format(**locals()))
    if int(ratings_count) > 0:
        print("ratings_time_series | {ratings_time_series}".format(**locals()))
    else:
        print("ratings_time_series | (not applicable)")
    if query_response.status_code == 200:  # HTTP 200 OK
        return results_data
    else:
        return None

def rate_node(server, s, xcsrf_token, node_to_rate, rating):
    # Appears at this time unimportant to distinguish between rating and 
    # re-rating a node.  In the future the "type: update" pair may be added.
    rating = int(rating)
    rating_data = {
        "rating": rating,
        "timeseries": False
    }
    node_url = get_node_url(server)
    rate_node_url = node_url + "/{node_to_rate}/ratings.json".format(**locals())
    s.headers.update({"X-CSRF-Token": xcsrf_token})
    logging.debug("xcsrf_token = " + xcsrf_token)
    logging.debug("rating_data = {rating_data}".format(**locals()))
    logging.debug("rate_node_url = {rate_node_url}".format(**locals()))
    request_node  = s.post(rate_node_url, json=rating_data, timeout=1, verify=cert_in_use)
    logging.debug(request_node.content)
    logging.info("status code returned = " + str(request_node.status_code))
    if request_node.status_code == 201:  # HTTP 201 Created
        return True 
    else:
        return None

def add_support_link(server, s, xcsrf_token, node_to_support, 
                     supporting_node_id):
    support_link_data = {
        "sources": [],
        "child_id": supporting_node_id 
    }
    node_url = get_node_url(server)
    support_link_url = "{node_url}/{node_to_support}.json".format(**locals())
    s.headers.update({"X-CSRF-Token": xcsrf_token})
    logging.debug("xcsrf_token = " + xcsrf_token)
    logging.debug("support_link_data = {support_link_data}".format(**locals()))
    logging.debug("support_link_url = {support_link_url}".format(**locals()))
    request_node  = s.patch(support_link_url, json=support_link_data, 
                            timeout=1, verify=cert_in_use)
    logging.debug(request_node.content)
    logging.info("status code returned = " + str(request_node.status_code))
    if request_node.status_code == 202:  # HTTP 202 Accepted
        return True 
    else:
        return None

def add_conclusion_link(server, s, xcsrf_token, node_to_link_conclusion_to, 
        conclusion_node_id):
    conclusion_link_data = {
        "sources": [],
        "parent_id": conclusion_node_id 
    }
    node_url = get_node_url(server)
    conclusion_link_url = ("{node_url}/{node_to_link_conclusion_to}"
                ".json".format(**locals()))
    s.headers.update({"X-CSRF-Token": xcsrf_token})
    logging.debug("xcsrf_token = " + xcsrf_token)
    logging.debug("support_link_data = {conclusion_link_data}".format(**locals()))
    logging.debug("support_link_url = {conclusion_link_url}".format(**locals()))
    request_node  = s.patch(conclusion_link_url, json=conclusion_link_data, timeout=1, verify=cert_in_use)
    logging.debug(request_node.content)
    logging.info("status code returned = " + str(request_node.status_code))
    if request_node.status_code == 202:  # HTTP 202 Accepted
        return True 
    else:
        return None

def relegate_node(server, s, xcsrf_token, id_of_node, relegate_confirmation):
    node_url = get_node_url(server)
    relegation_url= node_url + "/{id_of_node}.json".format(**locals())
    s.headers.update({"X-CSRF-Token": xcsrf_token})
    logging.debug("xcsrf_token = " + xcsrf_token)
    logging.debug("relegate_link_url = {relegation_url}".format(**locals()))
    if "{relegate_confirmation}".format(**locals()) == "confirm":
        request_node  = s.delete(relegation_url, timeout=1, verify=cert_in_use)
        logging.debug(request_node.content)
        logging.info("status code returned = " + str(request_node.status_code))
        if request_node.status_code == 204:  # HTTP 204 No Content 
            return True 
        else:
            return None
    else:
        logging.warning("Confirmation argument did not match required value.")
        return None

def get_node_stats(server, s, xcsrf_token, node_id):
    logging.debug("node_id = {node_id}".format(**locals()))
    stats_params = {
        "view": "stats"
    }
    node_url = get_node_url(server)
    node_stats_url = node_url + "/{node_id}.json".format(**locals())
    s.headers.update({"X-CSRF-Token": xcsrf_token})
    query_response = s.get(node_stats_url, params=stats_params, 
            timeout=1, verify=cert_in_use)
    results_data = json.loads(query_response.text)
    logging.debug(results_data)
    logging.debug("status code returned = " + str(query_response.status_code))
    children_count = results_data['children_count']
    parents_count = results_data['parents_count']
    flags_count = results_data['flags_count']
    return (children_count, parents_count, flags_count)

def list_supports(server, s, xcsrf_token, id_of_root_node):
    tree_url = get_tree_url(server)
    (supports_qty, conclusions_qty, flag_qty) = get_node_stats(
            server, s, xcsrf_token, id_of_root_node)
    list_supports_url= tree_url + "/{id_of_root_node}.json".format(**locals())
    s.headers.update({"X-CSRF-Token": xcsrf_token})
    logging.debug("xcsrf_token = " + xcsrf_token)
    logging.debug("supports_list_url = {list_supports_url}".format(**locals()))
    supports_list_response = s.get(list_supports_url, timeout=1, verify=cert_in_use)
    supports_list_data = supports_list_response.json() 
    # logging.debug(supports_list_response.content)
    logging.info("status code returned = " + str(supports_list_response.status_code))
    # logging.debug("supports_list_response.content = " + str(supports_list_response.content))
    logging.debug("supports_list_data = " + str(supports_list_data))
    # node_title = next((x['title'] for x in supports_list_data['nodes'] if x['id'] == id_of_root_node)) 
    node_title = next((x['title'] for x in supports_list_data['nodes'] if x['id'] == supports_list_data['mapping']['id']))
    print(
        "Results for:\n"
        " node_id: {id_of_root_node}\n"
        " node_title: {node_title}\n\n"
        "Number of supports: {supports_qty}".format(**locals())
    )
    if supports_qty > 0:
        print(
            "\nSupports found:\n"
            "node_id | supporting_node_title\n"
            "--------+-----------------------------------------------------------"
            "".format(**locals()))
        if "children" in supports_list_data['mapping']:
            for support in supports_list_data['mapping']['children']:
                support_id = support['id']
                support_title = next((x['title'] for x in supports_list_data['nodes'] if x['id'] == support_id), None)
                print('{0: <8}'.format(support_id) + "| {support_title}".format(**locals()))
    else:
        logging.warning("No supports found for that node_id.")
    if supports_list_response.status_code == 200:  # HTTP 200 OK
        return True 
    else:
        return None

def edit_node(server, s, xcsrf_token, node_id, new_title):
    title_text = str(new_title)
    edit_node_data = {
        "title": title_text,
    }
    node_url = get_node_url(server)
    edit_node_url = node_url + "/{node_id}.json".format(**locals())
    s.headers.update({"X-CSRF-Token": xcsrf_token})
    logging.debug("xcsrf_token = " + xcsrf_token)
    logging.debug("edit_node_data = {edit_node_data}".format(**locals()))
    logging.debug("edit_node_url = {edit_node_url}".format(**locals()))
    request_node  = s.patch(edit_node_url, json=edit_node_data, timeout=1, verify=cert_in_use)
    logging.debug(request_node.content)
    logging.info("status code returned = " + str(request_node.status_code))
    if request_node.status_code == 202:  # HTTP 202 Accepted
        return True 
    else:
        return None

def node_stats(server, s, xcsrf_token, node_id):
    (supports_qty, conclusions_qty, flag_qty) = get_node_stats(
            server, s, xcsrf_token, node_id)
    tree_url = get_tree_url(server)
    title_url = tree_url + "/{node_id}.json".format(**locals())
    s.headers.update({"X-CSRF-Token": xcsrf_token})
    title_response = s.get(title_url, timeout=1, verify=cert_in_use)
    title_data = title_response.json() 
    node_title = next((x['title'] for x in title_data['nodes'] if x['id'] == title_data['mapping']['id']))
    print(
        "node_id:           {node_id}\n"
        "node_title:        {node_title}\n"
        "supports_count:    {supports_qty}\n"
        "conclusions_count: {conclusions_qty}\n"
        "flags_count:       {flag_qty}".format(**locals())
    )
    if title_response.status_code == 200:  # HTTP 200 OK
        return True 
    else:
        return None


def main(args):
    logging.basicConfig()
    if args['--verbose'] == True:
        logging.getLogger().setLevel(logging.INFO)
    elif args['--quiet'] == True:
        logging.getLogger().setLevel(logging.ERROR)
    elif args['--debug'] == True:
        logging.getLogger().setLevel(logging.DEBUG)
    else: 
        logging.getLogger().setLevel(logging.WARNING)
    logging.debug("Got args:\n{args}".format(**locals()))
    cookies_input = args['--input']
    cookies_output = args['--output']
    server = args['--server']
    if args['--user'] == True:
        user = args['--user']
    if args['--pass'] == True:
        password = args['--pass']

    active_session, security_token = get_session(server, cookies_input)

    if args['add_node'] == True:
        title_to_add = args['<title>']
        added_result = add_node(server, active_session, security_token, 
                                title_to_add)
        if added_result == True:
            logging.info("Done adding node.")
        else:
            logging.warning("Failed to add node.")

    if args['search_nodes'] == True:
        search_term = args['<title>']
        query_result = search_nodes(server, active_session, security_token, 
                                    search_term)
        if query_result == True:
            logging.info("Succeeded in querying nodes.")
        else:
            logging.warning("Failed while querying nodes.")
    if cookies_output is not None:
        saved_cookies = save_session(active_session, cookies_output)

    if args['node_details'] == True:
        node_id_to_look_up = args['<node_id>']
        sought_details = get_node_details(
                server, active_session, security_token, node_id_to_look_up)
        if sought_details != None:
            logging.info("Done looking up node details.")
        else:
            logging.warning("Failed to look up node details.")

    if args['rate_node'] == True:
        node_id_to_rate = args['<node_id>']
        rating_value = args['<validity>']
        rated_node = rate_node(
                server, active_session, security_token, node_id_to_rate, 
                rating_value)
        if rated_node == True:
            logging.info("Done rating node.")
        else:
            logging.warning("Failed to rate node.")

    if args['link_support'] == True:
        node_id_linked_to = args['<node_id>']
        node_id_of_support = args['<support_node_id>']
        linked_support = add_support_link(
                server, active_session, security_token, node_id_linked_to, 
                node_id_of_support)
        if linked_support == True:
            logging.info("Done linking support node.")
        else:
            logging.warning("Failed to link support node.")

    if args['link_conclusion'] == True:
        node_id_linked_to = args['<node_id>']
        node_id_of_conclusion = args['<conclusion_node_id>']
        linked_support = add_conclusion_link(
                server, active_session, security_token, node_id_linked_to, 
                node_id_of_conclusion)
        if linked_support == True:
            logging.info("Done linking conclusion node.")
        else:
            logging.warning("Failed to link conclusion node.")

    if args['relegate_node'] == True:
        node_to_relegate = args['<node_id>']
        attempt_to_confirm = args['<confirmation>']
        relegated = relegate_node(server, active_session, security_token, 
                node_to_relegate, attempt_to_confirm)
        if relegated == True:
            logging.info("Done relegating node.")
        else:
            logging.warning("Failed to relegate node.")

    if args['list_supports'] == True:
        root_id = args['<root_node_id>']
        got_tree = list_supports(server, active_session, security_token, 
                root_id)
        if got_tree == True:
            logging.info("Done listing supports.")
        else:
            logging.warning("Failed to list supports.")

    if args['edit_node'] == True:
        node_id = args['<node_id>']
        new_title = args['<new_title>']
        edited_node = edit_node(server, active_session, security_token, 
                node_id, new_title)
        if edited_node == True:
            logging.info("Done editing node.")
        else:
            logging.warning("Failed to edit_node.")

    if args['node_stats'] == True:
        node_id = args['<node_id>']
        ran_stats = node_stats(server, active_session, security_token, 
                node_id)
        if ran_stats == True:
            logging.info("Done getting stats.")
        else:
            logging.warning("Failed to get stats.")

    return None

if __name__ == "__main__":
    arguments = docopt(__doc__, version='v1.0.1-dev')
    main(arguments)
