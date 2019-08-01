# python-appdb-info
This repository contains the Python client to get a list of providers supporting a given VO. The client provides a JSON file with the list of providers and the published resources provided by the EGI AppDB information system. 

## Requirements

* Basic knowledge of the `json`, `xmltodict` and `httplib` python libraries are requested
* Python v2.7.12+

## Settings

For simple one-off requests, you can use this library as a drop-in replacement for the requests library:

<pre>
import json
import httplib
import xmltodict
import urllib2

# VO_NAME used to query the EGI AppDB
vo = "vo.access.egi.eu"
[..]
</pre>

## Usage

<pre>
]$ python python-appdb-info.py > result.json
</pre>
