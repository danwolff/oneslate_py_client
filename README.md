# oneslate_py_client

The file oneslate.py is a partial Oneslate client for interacting over HTTP with running Oneslate instances.  The module can be called directly from the command line or the module can be imported and reused in other Python scripts.

Basic functionality is included, such as:
 - adding a node
 - searching nodes
 - viewing node details
 - viewing node statistics
 - rating nodes on a 5-bin validity scale
 - linking supports and conclusions 
 - relegating nodes 
 - listing supporting nodes
 - editing node titles

The implementation is partial at this time, since it does not yet include some features implemented in the Oneslate UI such as adding media nodes, unlinking supports from conclusions, pre-checking against cyclical dependency creation, submitting bias survey results upon node validity re-rating, flagging nodes, etc.  

# Script help output

```
dwolff@machine09707525:~/oneslate/oneslate_py_client$ ./oneslate.py --help
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
  -c <cfgfile>, --config <cfgfile>    Path to file with 3 lines: host, username,
                                      and password to use if no valid input
                                      cookies [default: os.cfg].
  -s <host>, --server <host>          Server URL [default: https://1s-dev.example.com].
  -u <username>, --user <username>    Username (e.g., email address) to fall
                                      back in if no config file and no valid input cookies.
  -p <password>, --pass <password>    Password to fall back on if no config
                                      file and no valid input cookies.
  -i <infile>, --input=<infile>       Cookies input file [default: cookies.txt].
  -o <outfile>, --output=<outfile>    Cookies output file [default: cookies.txt].
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
```

# Sample command line usage
This example assumes you have downloaded and set up the Oneslate virtual machine, with it running and set up as accesssible from https://reqests-dev.example.com. It also assumes that os.cfg contains three lines contaiing a valid server, user, and password.

```
./oneslate.py add_node "Adding"

./oneslate.py add_node "Adding2"

./oneslate.py add_node "Adding3"

./oneslate.py search_nodes "Adding"
    Search results for node title: Adding
    node_id | node_title
    --------+-----------------------------------------------------------
    52      | Adding
    54      | Adding3
    53      | Adding2

./oneslate.py rate_node 52 2

./oneslate.py rate_node 53 3

./oneslate.py edit_node 53 "Added node."

./oneslate.py link_support 52 53

./oneslate.py link_support 52 54

./oneslate.py list_supports 52
    Results for:
     node_id: 52
     node_title: Adding

    Number of supports: 2

    Supports found:
    node_id | supporting_node_title
    --------+-----------------------------------------------------------
    53      | Added node.
    54      | Adding3

./oneslate.py node_stats 54
    node_id:           54
    node_title:        Adding3
    supports_count:    0
    conclusions_count: 1
    flags_count:       0

./oneslate.py node_details 53
    Details for node_id: 53
    detail              | value
    --------------------+-----------------------------------------------
    id                  | 53
    title               | Added node.
    rating              | 3
    explanation         | This node posted via automation in oneslate.py v0.0.1-dev.
    media               | False
    type                | None
    flagged             | None
    followed            | None
    created_at          | June 23, 2018 08:40
    username            | 15973462
    rating_counts       | [0, 0, 0, 1, 0]
    ratings_count       | 1
    current_user_author | True
    communities         | []
    sources             | []
    ratings_time_series | [['0.0'], ['0.0'], ['0.0'], ['1.0'], ['0.0']]

./oneslate.py link_conclusion 54 53
```

# Sample reuse in Python
The accompanying module, example_usage.py, exemplifies importing and reusing functions from oneslate.py.
