================================================
Overview
================================================

This app provides a mechanism for monitoring file-systems meta-data without importing the actual contents.



================================================
Configuring Splunk
================================================

This app exposes a new input type that can be configured in the Splunk Manager. To configure it, create a new input in the Manager under Data inputs È File Meta-data.



================================================
Getting Support
================================================

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
|         | Added time field so that Splunk no longer interprets one of the other time fields in the results                 |
+---------+------------------------------------------------------------------------------------------------------------------+
