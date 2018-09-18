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
./oneslate.py --help
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
  -c <cfgfile>, --config <cfgfile>    Path to file with three lines: host,
                                      username, and password.  Used if no
                                      current session from cookies.  Overrides
                                      arguments for these three params if also
                                      provided at command line.
  -s <host>, --server <host>          Server URL [default: https://1s-dev.example.com].
  -u <username>, --user <username>    Username to fall back to if no config file
  				      and no session from cookies
				      [default: bot@example.com].
  -p <password>, --pass <password>    Password to fall back to if no config
                                      file and no session from cookies.
  -i <infile>, --input=<infile>       Cookies input file [default: cookies.txt].
  -o <outfile>, --output=<outfile>    Cookies output file [default: cookies.txt].
  -r <validity>, --rating=<validity>  Rating to give node.
  -q, --quiet                         Print less text.
  --verbose                           Print more text.
  --debug                             Print even more text, for debugging.
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
This example assumes you have downloaded and set up the Oneslate virtual machine, with it running and set up as accesssible from https://requests-dev.example.com. It also assumes that os.cfg contains three lines specifying the valid server, user, and password.

```
./oneslate.py -c os.cfg add_node "Adding 71" 2>/dev/null

./oneslate.py -c os.cfg add_node "Adding 72" 2>/dev/null

./oneslate.py -c os.cfg add_node "Adding 73" 2>/dev/null

./oneslate.py -c os.cfg search_nodes "Adding 7" 2>/dev/null
	Search results for node title: Adding 7
	node_id | node_title
	--------+-----------------------------------------------------------
	66      | Adding 72
	65      | Adding 71
	67      | Adding 73

./oneslate.py -c os.cfg rate_node 65 2 2>/dev/null

./oneslate.py -c os.cfg rate_node 66 3 2>/dev/null

./oneslate.py -c os.cfg edit_node 67 "Added node." 2>/dev/null

./oneslate.py -c os.cfg link_support 65 66 2>/dev/null

./oneslate.py -c os.cfg link_support 65 67 2>/dev/null

./oneslate.py -c os.cfg list_supports 65 2>/dev/null

./oneslate.py -c os.cfg list_supports 65 2>/dev/null
	Results for:
	 node_id: 65
	 node_title: Adding 71
	
	Number of supports: 2
	
	Supports found:
	node_id | supporting_node_title
	--------+-----------------------------------------------------------
	66      | Adding 72
	67      | Added node.
	
./oneslate.py -c os.cfg node_stats 67 2>/dev/null
	node_id:           67
	node_title:        Added node.
	supports_count:    0
	conclusions_count: 1
	flags_count:       0

./oneslate.py -c os.cfg node_details 67 2>/dev/null
	Details for node_id: 67
	detail              | value
	--------------------+-----------------------------------------------
	id                  | 67
	title               | Added node.
	rating              | None
	explanation         | This node posted via automation in oneslate.py v0.0.1-dev.
	media               | False
	type                | None
	flagged             | None
	followed            | None
	created_at          | August 17, 2018 01:38
	username            | 40278369
	rating_counts       | None
	ratings_count       | 0
	current_user_author | True
	communities         | []
	sources             | []
	ratings_time_series | (not applicable)

./oneslate.py -c os.cfg link_conclusion 67 66 2>/dev/null
```

# Sample reuse in Python
The accompanying module, example_usage.py, exemplifies importing and reusing functions from oneslate.py.
