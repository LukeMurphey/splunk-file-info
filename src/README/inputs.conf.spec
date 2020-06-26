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
* If true, then a cryptographic hash will be generated for the files using the SHSA224 algorithm
* WARNING: enabling this can generate a large amount of IO load especially if large files are being monitored.
* It is generally recommended you set a file_hash_limit limit too if you include file hashes so that large files do not generate a large amount of IO load

file_hash_limit = <value>
* This places a limit on the size of the files that will be hashed (see include_file_hash above); files larger than this value will not be hashed
* This value can include units (e.g. 15mb for 15 megabytes, 1gb for 1 gigabyte)

depth_limit = <value>
* If set and greater than zero, then only the input will stop after recurising down directories once the limit is reached

file_filter = <value>
* Limits the files analyzed to those that match this wildcard

extract_strings = <value>
* If true, then strings will be extracted

extract_data = <value>
* If true, then data specific to the type of file will be extracted
