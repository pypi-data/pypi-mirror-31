# Copyright 2018 Benedikt Bergenthal

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import sys
import configparser
import os
from optparse import OptionParser
import pkg_resources

def rreplace(s, old, new, occurrence):
	li = s.rsplit(old, occurrence)
	return new.join(li)

def main():
	configFilename = pkg_resources.resource_filename(__name__, "actDeact.conf")
	config = configparser.ConfigParser()
	config.read(configFilename)
	
	prefix = ""
	suffix = ""
	if 'prefix' in config['Main']:
		prefix = config['Main']['prefix']
	if 'suffix' in config['Main']:
		suffix = config['Main']['suffix']

	parser = OptionParser(usage="usage: %prog [options] args" ,version="%prog 1.0")
	parser.add_option("-a", "--activate",  action="store_true", dest="activate", default=False, help="Activate file(s)")
	parser.add_option("-d", "--deactivate",  action="store_true", dest="deactivate", default=False, help="Deactivate file(s)")
	parser.add_option("-c", "--config",  action="store_true", dest="config", default=False, help="Show the filename of the config file for editing")
	parser.add_option("-v", "--verbose",  action="store_true", dest="verbose", default=False, help="Verbose output")
	

	(options, args) = parser.parse_args()
	if options.activate and options.deactivate:
		parser.error('options -a and -d are mutually exclusive')

	if options.config:
		print(configFilename)

	if options.deactivate:
		for arg in args:
			if options.verbose:
				print("Deactivating: " , arg , " to ", prefix + arg + suffix)
			try:
				os.rename(arg, prefix + arg + suffix)
			except:
				if options.verbose:
					print("Error renaming: ", arg)

	if options.activate:
		for arg in args:
			newname = arg
			if prefix != "":
				newname = newname.replace(prefix , "", 1)
			if suffix != "":
				newname = rreplace(newname, suffix, "", 1)
			if options.verbose:
				print("Activating: " , arg , " to ", newname)
			try:
				os.rename(arg, newname)
			except:
				if options.verbose:
					print("Error renaming: ", arg)
