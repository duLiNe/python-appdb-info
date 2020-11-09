# python-appdb-info
This repository contains the Python client to get a list of providers supporting a given VO. The client provides a JSON file with the list of providers and the published resources provided by the EGI AppDB information system. 

## Requirements

* Basic knowledge of the `json`, `xmltodict`, `urlparse`, `urlopen` and `httplib` python libraries are requested
* Python v3.5.2+

## Settings

For simple one-off requests, you can use this library as a drop-in replacement for the requests library:

<pre>
import json
import http.client
import xmltodict
from urllib.request import urlopen
from urllib.parse import urlparse


# VO_NAME used to query the EGI AppDB
vo = "vo.access.egi.eu"
[..]
</pre>

## Usage

<pre>
]$ python3 python-appdb-info.py > result.json
</pre>
