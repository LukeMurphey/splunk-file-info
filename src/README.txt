================================================
Overview
================================================

This app provides a mechanism for monitoring file-systems meta-data without importing the actual file contents.



================================================
Configuring Splunk
================================================

Install this app into Splunk by doing the following:

  1. Log in to Splunk Web and navigate to "Apps » Manage Apps" via the app dropdown at the top left of Splunk's user interface
  2. Click the "install app from file" button
  3. Upload the file by clicking "Choose file" and selecting the app
  4. Click upload
  5. Restart Splunk if a dialog asks you to

Once the app is installed, you can use the app by configuring a new "File Meta-data" input:
  1. Navigate to "Settings » Data Inputs" at the menu at the top of Splunk's user interface.
  2. Click "File Meta-data"
  3. Click "New" to make a new instance of an input



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
| 1.1     | Adding output of ACLs                                                                                            |
|---------|------------------------------------------------------------------------------------------------------------------|
| 1.1.1   | Input now continues to run even if the ACL data lookups generates an exception                                   |
|---------|------------------------------------------------------------------------------------------------------------------|
| 1.1.2   | Fixing error that could happen if the input doesn't have access to a directory                                   |
|---------|------------------------------------------------------------------------------------------------------------------|
| 1.2     | Adding ability to define a recursion limit                                                                       |
|---------|------------------------------------------------------------------------------------------------------------------|
| 1.3     | Added support for running the input on a Universal Forwarder                                                     |
|---------|------------------------------------------------------------------------------------------------------------------|
| 1.4     | Added support for filtering files by name                                                                        |
+---------+------------------------------------------------------------------------------------------------------------------+
