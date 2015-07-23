[file_meta_data://default]
* Configure an input for importing syndication feeds (RSS, ATOM, RDF)

file_path = <value>
* The url of the feed

interval = <value>
* Indicates how often to perform the check

recurse = <value>
* If true, then all files within the directory will be analyzed

only_if_changed = <value>
* If true, then the only entries that will be returned will be the ones in which one of the time values changed

include_file_hash = <value>
* If true, then a cryptographic hash will be generated for the files using the SHSA224 algorith
* WARNING: enabling this will generate a large amount of IO load

file_hash_limit = <value>
* This places a limit on the size of the files that will be hashed (see include_file_hash above); files larger than this value will not be hashed
* This value can include units (e.g. 15mb for 15 megabytes, 1gb for 1 gigabyte) 