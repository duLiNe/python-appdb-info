#!/usr/bin/env python2

#
#  Copyright 2019 EGI Foundation
# 
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
#

import json
import httplib
import xmltodict
import urllib2
from urlparse import urlparse

__author__    = "Giuseppe LA ROCCA"
__email__     = "giuseppe.larocca@egi.eu"
__version__   = "$Revision: 0.0.0"
__date__      = "$Date: 04/10/2019 12:32:27"
__copyright__ = "Copyright (c) 2019 EGI Foundation"
__license__   = "Apache Licence v2.0"

# VO_NAME used to query the EGI AppDB
vo = "vo.access.egi.eu"


def appdb_call(c):
	''' Connect to the EGI AppDB server and get the list of providers supporting the given VO '''

        conn = httplib.HTTPSConnection("appdb.egi.eu")
        conn.request("GET", c)
        data = conn.getresponse().read()
        conn.close()
        data.replace('\n','')
        return xmltodict.parse(data)


def get_provider_metadata(providerID):
	''' Get metadata from the given cloud provider '''

	# Initialize the JSON object
	provider = []

	try:
		value = 0
		keystone_url = ""

                # E.g.: https://appdb.egi.eu/rest/1.0/va_providers/8253G0
        	data = appdb_call('/rest/1.0/va_providers/%s' %providerID)
		
		provider_name = data['appdb:appdb']['virtualization:provider']['provider:name']	
		provider_authn = data['appdb:appdb']['virtualization:provider']
		provider_service_type = data['appdb:appdb']['virtualization:provider']

		if (data['appdb:appdb']['virtualization:provider'].has_key('provider:endpoint_url')):
			provider_endpoint_url = data['appdb:appdb']['virtualization:provider']['provider:endpoint_url']
			
			if (provider_service_type['@service_type'] == "org.openstack.nova"):
				keystone_url = data['appdb:appdb']['virtualization:provider']['provider:url']
			else:
				keystone_url = "N/A"
		else:
			provider_endpoint_url = 'N/A' 
			
		site_name = data['appdb:appdb']['virtualization:provider']['appdb:site']['site:officialname']
		status = data['appdb:appdb']['virtualization:provider']['appdb:site']
		#provider_id = ("https://appdb.egi.eu/rest/1.0/va_providers/%s" %id)

		# Creation of the final JSON object
		provider.append({ 
			"id": providerID,
			"sitename" : provider_name, 
                       	"status" : status['@status'], 
	                "authn" : provider_authn['@authn'],
        	        "occi_endpoint" : provider_endpoint_url,
                        "keystone_endpoint" : keystone_url
	         })

        except Exception as error:
		pass

	return provider


def get_resource_tpl(providerID):

        try:
		# Initialize the JSON object
		resources_tpl = []

                main_memory_size = ""
                logical_cpus = ""
                physical_cpus = ""
		resource_serialized = ""

                # E.g.: https://appdb.egi.eu/rest/1.0/va_providers/8253G0
                data = appdb_call('/rest/1.0/va_providers/%s' %providerID)
                
		for resource_tpl in data['appdb:appdb']['virtualization:provider']['provider:template']:
			resource_name = resource_tpl['provider_template:resource_name']
			main_memory_size = resource_tpl['provider_template:main_memory_size']
			logical_cpus = resource_tpl['provider_template:logical_cpus']
			physical_cpus = resource_tpl['provider_template:physical_cpus']

		        resources_tpl.append({ 
                	        "resource_name": resource_name,
                        	"main_memory_size" : main_memory_size,
                                "logical_cpus" : logical_cpus,
	                        "physical_cpus" : physical_cpus
        	        })
        
	except Exception as error:
		pass

	return resources_tpl


def get_os_tpl(providerID):

        try:
		# Initialize the JSON object
		oss_tpl = []

		appname = ""
		vmiversion = ""
		va_provider_image_id = ""

                # E.g.: https://appdb.egi.eu/rest/1.0/va_providers/8253G0
                data = appdb_call('/rest/1.0/va_providers/%s' %providerID)

		for os_tpl in data['appdb:appdb']['virtualization:provider']['provider:image']:
			try:
				if vo in os_tpl['@voname']:
					#print "- Name = %s [v%s] [%s] " %(os_tpl['@appname'], os_tpl['@vmiversion'], providerID)
					appname = os_tpl['@appname']
					vmiversion = os_tpl['@vmiversion']

					provider_service_type = data['appdb:appdb']['virtualization:provider']
					# Check whether the provider supports: X509-VOMS or OIDC
					# Possible @service_type values: org.openstack.nova, eu.egi.cloud.vm-management.occi	
					if (provider_service_type['@service_type'] == "org.openstack.nova"):

						provider_url = data['appdb:appdb']['virtualization:provider']['provider:url']
						o = urlparse(provider_url)
						_url = o.scheme + "://" + o.hostname

						if os_tpl['@va_provider_image_id'].startswith("os_tpl"):
							_os_tpl=os_tpl['@va_provider_image_id'].replace("os_tpl","os")
							#print " - ID = http://schemas.openstack.org/template/%s" %_os_tpl
							va_provider_image_id = "%s/%s" %(_url, _os_tpl)
				 		else:
							#print " - ID = %s" %os_tpl['@va_provider_image_id']
							va_provider_image_id = "%s/%s" %(_url, \
									        os_tpl['@va_provider_image_id'].split("#")[1])
					else:
						if os_tpl['@va_provider_image_id'].startswith("os_tpl"):
							_os_tpl=os_tpl['@va_provider_image_id'].replace("os_tpl","os")
							va_provider_image_id = "%s" %_os_tpl
							#print " - ID = http://schemas.openstack.org/template/%s" %_os_tpl
						else:
							va_provider_image_id = "%s" %os_tpl['@va_provider_image_id']
							#print " - ID = %s" %os_tpl['@va_provider_image_id']

					oss_tpl.append({
			                	"appname": appname,
                			        "vmiversion" : vmiversion,
                                		"va_provider_image_id" : va_provider_image_id
		                        })

		        except Exception as error:
                		pass

        except Exception as error:
                pass

	return oss_tpl


def get_provider_url(providerID):

	try:
                data = appdb_call('/rest/1.0/va_providers/%s' %providerID)

		provider_url = data['appdb:appdb']['virtualization:provider']['provider:url']
		#provider_endpoint_url = data['appdb:appdb']['virtualization:provider']['provider:endpoint_url']
        
	except Exception as error:
		pass

	return provider_url

def main():

	try:
		# E.g. https://appdb.egi.eu/rest/1.0/sites?flt=%%2B%%3Dvo.name:vo.access.egi.eu&%%2B%%3Dsite.supports:1
	        #data = appdb_call('/rest/1.0/sites?flt=%%2B%%3Dvo.name:%s&%%2B%%3Dsite.supports:1' %vo)
		# E.g. https://appdb.egi.eu/rest/1.0/sites?listmode=details&flt=%%3Dvo.access.egi.eu%%3A
	        data = appdb_call('/rest/1.0/sites?listmode=details&flt=%%3Dvo.name%%3A%s' %vo)

		# Initialize the JSON object
		providers = []
	
		# Initialize the array	
		providersID = []

		for site in data['appdb:appdb']['appdb:site']:
        	        if  type(site['site:service']) == type([]):
        			for service in site['site:service']:
					# Check if the provider_url is defined 
					provider_url = get_provider_url(service['@id'])
					if (provider_url != ""):	
						providersID.append(service['@id'])
			else:
				providersID.append(site['site:service']['@id'])

		for providerID in providersID:
			# Check if lists are not empty ...
			if get_os_tpl(providerID) and get_resource_tpl(providerID):
				# Creation of the final JSON object
		                providers.append({ 
				     # Collect the provider metadata
				     "provider" : get_provider_metadata(providerID),
                        	     # Collect the resource_tpl published by the providerID (if any)
	                             "resource_tpl" : get_resource_tpl(providerID),
        	                     # Collect the os_tpl published by the providerID (if any)
	        	             "os_tpl" : get_os_tpl(providerID)
                		})

		# Diplay the final JSON object
		print ("\n %s" %json.dumps(providers, 
			       indent=4, 
			       sort_keys=False))

		

	except Exception as error:
		pass

	print ""

if __name__ == "__main__":
        main()
