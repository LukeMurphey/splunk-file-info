================================================
Overview
================================================

This app provides a mechanism for monitoring file-systems meta-data without importing the actual file contents.



================================================
Configuring Splunk
================================================

This app exposes a new input type that can be configured in the Splunk Manager. To configure it, create a new input in the Manager under Data inputs » File Meta-data.



================================================
Getting Support
================================================

Go to the following website if you need support:

     http://answers.splunk.com/app/questions/2776.html

You can access the source-code and get technical details about the app at:

     http://lukemurphey.net/projects/splunk-file-info



================================================
Change History
================================================

+---------+------------------------------------------------------------------------------------------------------------------+
| Version |  Changes                                                                                                         |
+---------+------------------------------------------------------------------------------------------------------------------+
| 0.5     | Initial release                                                                                                  |
|---------|------------------------------------------------------------------------------------------------------------------|
| 0.6     | Added file_count and directory_count to directory entries                                                        |
|         | Added file_count_recursive and directory_count_recursive to the root file/directory entry                        |
|         | Fixed issue where the input would terminate if a file or directory was inaccessible                              |
|         | Fixed issue where the root directory was not included in the results if the recursive option was set             |
|         | Added time field so that Splunk no longer interprets one of the other time fields in the results                 |
|---------|------------------------------------------------------------------------------------------------------------------|
| 0.7     | Added ability to only retrieve entries when they change                                                          |
|---------|------------------------------------------------------------------------------------------------------------------|
| 1.0     | Added ability to compute file hashes                                                                             |
|---------|------------------------------------------------------------------------------------------------------------------|
| 1.0.1   | Fixing source-typing of modular input logs                                                                       |
|         | Fixed issue where an exception would sometimes be thrown when the input failed to get results                    |
|         | Added more information in the logs for when a file could not be accessed                                         |
|---------|------------------------------------------------------------------------------------------------------------------|
| 1.0.2   | Fixing error that occurred in exception handling routine when attempting to generate a hash of a file            |
|---------|------------------------------------------------------------------------------------------------------------------|
| 1.1     | Adding output of Windows file ACLs                                                                               |
+---------+------------------------------------------------------------------------------------------------------------------+
