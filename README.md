# Bulk Upload Audio for Memrise
This script uploads audio for words that don't have any audio uploaded in any course to which you have editor access

## Set up
This script has the following requirements:
* python 3
* libraries:
  * requests
  * sys
  * (gTTS optional)
  * bs4
  * argparse
  * getpass
  * os
  * shutil

It requires your login data for Memrise and the URL of the desired course.

## To run the script

```
usage: python main.py [-h] [-u USER] [-p PASSWORD] [-l LANGUAGE] [-k]
                            [-e {gTTS,SOT}] [-c COUNT] [-o] [-d]
                            [URL] [URL ...]

Bulk Upload Audio for Memrise

positional arguments:
  URL                   is the url of the first page after you go to your
                        course's database

optional arguments:
  -h, --help            show this help message and exit
  -u USER, --user USER  user name or email address to login at memrise.com (if
                        not provided it will be asked for interactively)
  -p PASSWORD, --password PASSWORD
                        password to login at memrise.com (if not provided it
                        will be asked for interactively)
  -l LANGUAGE, --language LANGUAGE
                        language of the audio file to be produced by Google
                        Text-to-Speech (if not provided it will be asked for
                        interactively)
  -k, --keepaudio       don't deleted generated MP3 files in subdirectory
                        'mp3' after upload
  -e {gTTS,SOT}, --engine {gTTS,SOT}
                        sound engine to be used. gTTS = "google Text To
                        Speech", SOT = "soundoftext.com" (default is gTTS)
  -c COUNT, --count COUNT
                        number of audios allowed per word (default is 1). This can be useful if you want to enforce another audio version.
  -o, --pooled          Enable parallel fetching
```

Where URL is the url of your course. (The script will try to upload audios to all databases of the course.)

For example:
python main.py http://app.memrise.com/course/1036119/hsk-level-6

This will add audio to any words that are missing it for the course.

### Example:
`python bulk-audio-upload.py http://app.memrise.com/course/1036119/hsk-level-6`

The script will ask for your login, password and language code and then add audio to any words that are missing for the course `http://app.memrise.com/course/1036119/hsk-level-6`.

## Alternative configuration

You can also make a file in the root directory of your script called 'variables.py' and create variables for your language, login information and course's database page.

It should look something like this:
```python
### you can use these as defaults for missing values in "alltasks" (remove '#' from lines to activate a value):
language = 'zh-CN'
user = 'mail@yourdomain.de'
password = 'BetterNotPutItHere'
course_database_url = "http://www.memrise.com/course/1036119/hsk-level-6/edit/database/2000662/"
# tld = "co.uk"
# count = 2

### if you want to update more than one course then you can define multiple tasks like this:
# alltasks = [
#     {
#         "user": "mail@yourdomain.de",
#         "password": "BetterNotPutItHere",
#         "language": "en-GB",
#         "engine": "gTTS",
#         "tld": "co.uk",
#         "count": 3,
#         "course_database_url": "https://app.memrise.com/course/2069455/kreaenglisch/edit/database/3078867/",
#     },
#     {
#         "user": "mail@yourdomain.de",
#         "password": "BetterNotPutItHere",
#         "language": "fr-FR",
#         "course_database_url": "https://app.memrise.com/course/2121400/kreafranzosisch/edit/database/3132443/",
#     },
# ]
```

## Setting the language

Please refer to [this documentation](https://soundoftext.com/docs#voices) for available languages and their language codes.

If you use the Google Text to Speech engine "gTTs": https://gtts.readthedocs.io/en/latest/module.html#languages-gtts-lang

# Common errors

## IndexError: list index out of range

Most likely, pagination is not active. To enable pagination, simply add more words.
