# A very simple [De]Activator for config files

This tool renames files by adding and removing a predefined prefix and suffix. It's intented use is to quickly activate and deactivate config files. 
## Installation 
```
$ pip install ActDeact
```
## Usage
```
Usage: actDeact [options] args

Options:
  --version         show program's version number and exit
  -h, --help        show this help message and exit
  -a, --activate    Activate file(s)
  -d, --deactivate  Deactivate file(s)
  -v, --verbose     Verbose output
  -c, --config      Show the filename of the config file for editing
```
Also two helper programs `act` and `deact` are provided. They are aliases to `actDeact -d` and `actDeact -a` and pass every argument directly to those programs. 
### Example
`actDeact -d foo` renames `foo` to `foo_bak` by default. This is equivaltent to `deact foo` .
`actDeact -a foo` renames `foo_bak` to `foo` by default. This is equivaltent to `act foo` .

## Configuration 
`actDeact -c` shows the filename of the configuration file. Its default content is:
```
[Main]
Prefix=
Suffix=_bak
```
In this file a prefix and a suffix can be set. 

