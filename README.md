# Bulk Upload Audio for Memrise
This script uploads audio for words that don't have any audio uploaded in any course to which you have editor access

## Set up
This script has the following requirements:
* python 3
* libraries:
  * requests
  * sys
  * (gTTS optional)
  * lxml
  * argparse
  * getpass
  * os
  * shutil

It requires your login data for Memrise and the database URL of the desired course.

## To run the script
usage: bulk-audio-upload.py [-h] [-u USER] [-p PASSWORD] [-l LANGUAGE] [-k]
                            [-e {gTTS,SOT}] [-c COUNT]
                            [URL [URL ...]]

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


Where URL is the url of the first page after you go to your course's database.

For example:
python main.py http://app.memrise.com/course/1036119/hsk-level-6/edit/database/2000662/

This will add audio to any words that are missing it for the course:
http://app.memrise.com/course/1036119/hsk-level-6.

This course's database page is:
http://app.memrise.com/course/1036119/hsk-level-6/edit/database/2000662/.

### Example:
`python bulk-audio-upload.py http://app.memrise.com/course/1036119/hsk-level-6/edit/database/2000662/`

The script will ask for your login, password and language code and then add audio to any words that are missing for the course `http://app.memrise.com/course/1036119/hsk-level-6`. This course's database page is `http://app.memrise.com/course/1036119/hsk-level-6/edit/database/2000662/`.

## Alternative configuration

You can also make a file in the root directory of your script called 'variables.py' and create variables for your language, login information and course's database page.

It should look something like this:
```python
language = 'zh-CN'
user = 'mail@yourdomain.de'
password = 'BetterNotPutItHere'
course_database_url = "http://www.memrise.com/course/1036119/hsk-level-6/edit/database/2000662/"
```

### Setting the language

Please refer to [this documentation](https://soundoftext.com/docs#voices) for available languages and their language codes.

### Setting the course database url

The course database url of the first page after you go to your course's database.

**Note**: This script relies on pagination being active. It does not work unless you have added more than one level and added enough words. If your link looks like `http://www.memrise.com/course/1036119/hsk-level-6/edit/#l_2000662`, then click `+ Add Level` in the bottom left corner.

# Common errors

## IndexError: list index out of range

Most likely, pagination is not active. To enable pagination, simply add more words.
