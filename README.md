# Bulk Upload Audio for Memrise
This script uploads chinese audio for words that don't have any audio uploaded in any course to which you have editor access

## Set up
This script has the following requirements:
* python 3
* libraries:
  * requests
  * tempfile
  * sys
  * gTTS
  * lxml
  * argparse
  * getpass
  * os

It requires your login data for Memrise and the database URL of the desired course.

## To run the script
usage: python bulk-audio-upload.py [-h] [-l LOGIN] [-p PASSWORD] [URL [URL ...]]

Bulk Upload Audio for Memrise

positional arguments:
  URL                   is the url of the first page after you go to your
                        course's database

optional arguments:
  -h, --help            show this help message and exit
  -l LOGIN, --login LOGIN
                        user name or email address to login at memrise.com (if
                        not provided it will be asked for interactively)
  -p PASSWORD, --password PASSWORD
                        password to login at memrise.com (if not provided it
                        will be asked for interactively)

Where URL is the url of the first page after you go to your course's database.

For example:
ipython main.py http://www.memrise.com/course/1036119/hsk-level-6/edit/database/
2000662/

This will add audio to any words that are missing it for the course:
http://www.memrise.com/course/1036119/hsk-level-6.

This course's database page is:
http://www.memrise.com/course/1036119/hsk-level-6/edit/database/2000662/.

For example:
`python bulk-audio-upload.py http://www.memrise.com/course/1036119/hsk-level-6/edit/database/2000662/`

The script will ask for your login and password and then add audio to any words that are missing it for the course `http://www.memrise.com/course/1036119/hsk-level-6`. This course's database page is `http://www.memrise.com/course/1036119/hsk-level-6/edit/database/2000662/`.
