# dhis2-pocket-knife [![Version](https://img.shields.io/pypi/v/dhis2-pocket-knife.svg)](https://pypi.python.org/pypi/dhis2-pocket-knife) [![Build](https://travis-ci.org/davidhuser/dhis2-pk.svg?branch=master)](https://travis-ci.org/davidhuser/dhis2-pk) [![Licence](https://img.shields.io/pypi/l/dhis2-pocket-knife.svg)](https://pypi.python.org/pypi/dhis2-pocket-knife) 

Command-line tools to interact with the RESTful Web API of [DHIS2](https://dhis2.org). Features:

* [Mass sharing of objects via filtering](#mass-sharing-of-objects-via-filtering)
* [Readable indicator definition to CSV](#readable-indicator-definition-to-csv)
* [User information to CSV](#export-user-info-to-csv)
* [Post CSS file](#post-css-file)

## Installation / updating

* Installation with [pip](https://pip.pypa.io/en/stable/installing) (python package manager, see if it is installed: `pip -V`)
* `pip install dhis2-pocket-knife` or `sudo -H pip install dhis2-pocket-knife`
* Upgrade with `pip install dhis2-pocket-knife -U`

## Usage

* Either pass arguments for a server / username / password or it make it read from a `dish.json` file as described in [baosystems/dish2](https://github.com/baosystems/dish2#configuration).
* Get help on using arguments, e.g.`dhis2-pk-share-objects --help`
* In the help text, `[-v]` means an optional argument

---

## Mass sharing of objects via filtering

Apply [sharing](https://docs.dhis2.org/master/en/user/html/sharing.html) for DHIS2 metadata and data objects (dataElements, indicators, programs, ...) through **[metadata object filtering](https://docs.dhis2.org/master/en/developer/html/dhis2_developer_manual_full.html#webapi_metadata_object_filter)** (for both shareable objects and userGroups).

- [For DHIS2 servers older than 2.29](#dhis2-servers-older-than-229)
- [For DHIS2 servers that are 2.29 or newer](#dhis2-servers-that-are-229-or-newer)

### DHIS2 servers older than 2.29

**Script name:** `dhis2-pk-share-objects`

#### Usage
```
dhis2-pk-share-objects --help
usage: dhis2-pk-share-objects [-h] [-s] -t -f [-w] [-r] -a [-o] [-l] [-v] [-u] [-p] [-d]

arguments:
  -h, --help            show this help message and exit
  
  -s SERVER             DHIS2 server URL without /api/, e.g. -s='play.dhis2.org/demo'
  
  -t OBJECT TYPE        DHIS2 object type to apply sharing, e.g. -t=sqlViews or -t=dataElements
                        
  -f FILTER             Filter on objects with DHIS2 field filter
                        add multiple filters with '&&' (rootJunction AND)
                        or '||' (rootJunction OR)
                        e.g. -f='name:like:ABC||name:like:XYZ'
                        
  -w USERGROUP_READWRITE
                        UserGroup filter for Read-Write access
                        add multiple filters with '&&' (rootJunction AND)
                        or '||' (rootJunction OR)
                        e.g. -w='name:$ilike:aUserGroup7&&id:!eq:aBc123XyZ0u'
                        
  -r USERGROUP_READONLY
                        UserGroup filter for Read-Only access
                        add multiple filters with '&&' (rootJunction AND)
                        or '||' (rootJunction OR)
                        e.g. -r='id:eq:aBc123XyZ0u'
                       
  -a {readwrite,none,readonly}
                        Public Access (with login), e.g. -a=readwrite
  
  -o OVERWRITE          Overwrite sharing - updates 'lastUpdated' field 
                        of all shared objects, otherwise it only updates if changed
  
  -l LOGGING_TO_FILE    Path to Log file (default level: INFO, pass -d for DEBUG)
                        e.g. l='/var/log/pk.log'
                        
  -v API_VERSION        DHIS2 API version e.g. -v=28
                        (if omitted, <URL>/api/endpoint will be used)
  -u USERNAME           DHIS2 username, e.g. -u=admin
  -p PASSWORD           DHIS2 password, e.g. -p=district
  -d                    Debug calls with -d

```
Other example:
Share `Hypertension` dataElements with _Read-Write_ access for `Admin` and `Research Group` User Groups while _Public Access_ should be _Read only_:

`
dhis2-pk-share-objects -s=play.dhis2.org/dev -u=admin -p=district -t=dataElements -f='name:like:Hypertension' -w='name:like:Admin||name:like:Research Group' -a=readonly
`


### DHIS2 servers that are 2.29 or newer

This script has a slightly different syntax since the format for Sharing changed in 2.29. It is now possible
to share DATA access for object types data set, tracked entity type, program and program stage. 
Read more [here.](https://docs.dhis2.org/master/en/user/html/ch23s04.html)

**Script name:** `dhis2-pk-share`

```
usage: dhis2-pk-share [-h] [-s] -t -f [-g] -a [-o] [-l] [-v] [-u] [-p] [-d]

Share DHIS2 objects with userGroups FOR 2.29 SERVERS or newer

required arguments:
  -s URL                DHIS2 server URL, e.g. 'play.dhis2.org/demo'
  -t OBJECT_TYPE        DHIS2 object type to apply sharing, e.g. sqlView
  -f FILTER             Filter on objects with DHIS2 field filter.
                        Add multiple filters with '&&' or '||'.
                        Example: -f 'name:like:ABC||code:eq:X'
  -a PUBLIC [PUBLIC ...]
                        publicAccess (with login). 
                        Valid choices are: readwrite, none, readonly

optional arguments:
  -g USERGROUP [USERGROUP ...]
                        Usergroup setting: FILTER METADATA [DATA] - can be repeated any number of times."
                        FILTER: Filter all User Groups. See -f for filtering mechanism
                        METADATA: Metadata access for this User Group. See -a for allowed choices
                        DATA: Data access for this User Group. optional (only for objects that support data sharing). see -a for allowed choices.
                        Example: -g 'id:eq:OeFJOqprom6' readwrite none 
  -o                    Overwrite sharing - updates 'lastUpdated' field of all shared objects
  -l LOGGING_TO_FILE    Path to Log file (default level: INFO, pass -d for DEBUG), e.g. l='/var/log/pk.log'
  -v API_VERSION        DHIS2 API version e.g. -v=28
  -u USERNAME           DHIS2 username, e.g. -u=admin
  -p PASSWORD           DHIS2 password, e.g. -p=district
  -d                    Debug flag
```

Example to share metadata only:

`
dhis2-pk-share -s play.dhis2.org/2.29 -u admin -p district -f='id:eq:P3jJH5Tu5VC' -t=dataelement -a readonly -g 'id:eq:wl5cDMuUhmF' readwrite -g 'id:eq:OeFJOqprom6' readwrite
`

Example to share data sets (with data access):

`
dhis2-pk-share -s play.dhis2.org/2.29 -u admin -p district -f='id:eq:P3jJH5Tu5VC' -t=dataelement -a readonly -g 'id:eq:wl5cDMuUhmF' readwrite -g 'id:eq:OeFJOqprom6' readwrite
`


---
## Readable indicator definition to CSV

**Script name:** `dhis-pk-indicator-definitions`

Writes indicator expressions (numerators/denominators) in a **readable format to a csv file**. Includes _names and number of orgunits for orgunit groups_, _dataelements (dataelement.categoryoptioncombo)_, _program dataelements_, _program indicators_, _trackedEntityAttributes_ and _constants_. It's possible to filter indicators with an object filter (see [`dhis2-pk-share-objects`](https://github.com/davidhuser/dhis2-pocket-knife#mass-sharing-of-objects-with-usergroups-through-filtering) for details). Note that when e.g. a dataElement is not shared with the user running the script but the indicator is, dataElement may still show up only with the UID.

Example output:
![ind-definitions](https://i.imgur.com/LFAlFpY.png)

Example column for numerator `ReUHfIn0pTQ - ANC 1-3 Dropout Rate`:
```
#{ANC 1st visit.Fixed}+#{ANC 1st visit.Outreach}-#{ANC 3rd visit.Fixed}-#{ANC 3rd visit.Outreach}
```

### Usage

```
dhis2-pk-indicator-definitions --help
usage: dhis2-pk-indicator-definitions [-h] [-s] [-f] [-u] [-p] [-v] [-d]

optional arguments:
  -h, --help           show this help message and exit
  -s SERVER            DHIS2 server URL without /api/ e.g. -s=play.dhis2.org/demo
  -f INDICATOR_FILTER  Indicator filter, e.g. -f='name:$like:HIV'
  -u USERNAME          DHIS2 username
  -p PASSWORD          DHIS2 password
  -v API_VERSION       DHIS2 API version e.g. -v=28
  -d                   Debug flag - writes more info to log file
```
### Indicator variables
For interpreting indicator variables (like `OUG{someUID}`), refer to [DHIS2 docs](https://docs.dhis2.org/master/en/developer/html/dhis2_developer_manual_full.html#d9584e5669)

##### Example (try it out against DHIS2 demo instance):
```
dhis2-pk-indicator-definitions -s=play.dhis2.org/demo -u=admin -p=district
```
---

## Export user info to CSV

Write information about users (paths of organisationUnits, userGroup membership) to a CSV file.

Click image for example CSV output:
![issue](https://i.imgur.com/2zkIFVi.png)

```
dhis2-pk-userinfo -h
usage: dhis2-pk-userinfo [-h] [-s] [-u] [-p] [-v] [-d]

optional arguments:
  -h, --help      show this help message and exit
  -s SERVER       DHIS2 server URL without /api/ e.g. -s=play.dhis2.org/demo
  -u USERNAME     DHIS2 username
  -p PASSWORD     DHIS2 password
  -v API_VERSION  DHIS2 API version e.g. -v=28
  -d              Writes more info in log file

```

Example (try it out against DHIS2 demo instance):
`dhis2-pk-userinfo -s=play.dhis2.org/demo -u=admin -p=district`

---
## Post CSS file

Simply post a CSS file to a server. 

```
dhis2-pk-post-css -h
usage: dhis2-pk-post-css [-h] [-s] -c [-u] [-p] [-d]

optional arguments:
  -h, --help      show this help message and exit
  -s SERVER       DHIS2 server URL without /api/ e.g. -s=play.dhis2.org/demo
  -c CSS          CSS file to post
  -u USERNAME     DHIS2 username
  -p PASSWORD     DHIS2 password
  -d              Writes more info in log file

```

Example (with reading out a `dish.json` file):

`dhis2-pk-post-css -c=style.css`

---

### Install from source

```
wget https://github.com/davidhuser/dhis2-pk/archive/master.zip
unzip master.zip
cd dhis2-pocket-knife
python setup.py install
```

### Done

- [x] debug flag as optional argument
- [x] multiple filters for userGroups
- [x] API version as optional
- [x] added indicator expression script
- [x] multiple filter should be added with `&&` instead of `&`
- [x] read from dish.json file
- [x] new feature: POST CSS to server
- [x] sharing: honor existing sharing settings and only update when different to arguments
- [x] color output
- [x] file logging
- [x] 2.29 Support (data and metadata sharing)

### Todos

- [ ] Script tests
- [ ] Interactive sharing
