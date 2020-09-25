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
                        number of audios allowed per word (default is 1)


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

You can also make a file in the root directory of your script called 'variables.py' and create a python dictionary of your cookies, as well as variables for your language and course's database page.

It should look something like this:
```python
language = 'zh-CN'
user = 'mail@yourdomain.de'
password = 'betternotputithere'
course_database_url = "http://www.memrise.com/course/1036119/hsk-level-6/edit/database/2000662/"

cookies = {'_sp_id.7bc7': '06d67edb75b999999.1466999953.100.1555544393.1234573782',
           '_sp_ses.7bc7': '*',
           'csrftoken': 'nxIto89I10jvMe45lt5xBJ8xnQkWayh3',
           'fbm_143688012353890': 'base_domain=.www.memrise.com',
           'fbsr_143688012353890': 'bGMeJtlEkaCEISsa4th4J1-FvygfuhFgBuu7qnnS1M.eyJhbGdvcml03f6OiJITUFDLVNIQTI1NiIsImNvZGUiOiJBUUNxNTh6ekpDMDlpNGNpTjNyaVRYR3VEN0xHZHM1TEJyMmFCVlJBTmVHeVl4WFlWanM1QVRpMDBtSzFwMWNFV2dxa28wUUxrWUVoT0RKLVdQOG1DdHVncjZhSGdxMVBEaEp3MGhTbV9pRXA3ckcxZU02d2M0LTNubFFCVkVaU0tUVml3eXFKdy1FZmxJYTVuZGJZUlhBXzVlNXdGcFFKWWVJem83ZllwcV9COWExdkJ0S3ZFQlB6OGQ2c2w0azMyOWtxcmFyVjJRYXpodVh3WXVlbVc4ejNlUUc5TE11SXJsakxTbW1hOXN3cUREVzEtcl94WlNLRlRucklsV3FxY3kzN0g1UnFVeTRwOFZ0TVVSXzEzd0Z0TjBrNF9PZjgzalJHYVZjZkV5dWFqUDJLQVhSRkxmT3RrU0R5d3lRSnRncGRMVC1ZZTVRTkNKN0xNRWxfcEVVWSIsImlzc3VlZF9hdCI6MTQ2ODY0Mzk4MiwidXNlcl9pZCI6IjUwMzc3MTY3OCJ9',
           'i18next': 'en',
           'sessionid': 'xrxg3zofonxnfmf5gfdgv5444defa71'}
```

### Setting the language

Please refer to [this documentation](https://soundoftext.com/docs#voices) for available languages and their language codes.

### Setting the course database url

The course database url of the first page after you go to your course's database.

**Note**: This script relies on pagination being active. It does not work unless you have added more than one level and added enough words. If your link looks like `http://www.memrise.com/course/1036119/hsk-level-6/edit/#l_2000662`, then click `+ Add Level` in the bottom left corner.

### Setting the cookies details

If you need help finding these details, you can get this through chrome. Just go onto memrise, then on the Chrome browser and open the database for the course that you want to upload audio to.

Once there, click the three dots on the top-right of the browser and go to `More Tools` --> `Developer Tools`. A window will appear at the bottom of the screen. Click the `Application` tab on that window. On the left you'll see a folder called `Cookies`. Expand that folder by clicking the triangle to the left of that.

Click `https://www.memrise.com`. What appears are your cookies. Format them as shown above. If you don't see a folder that says `https://www.memrise.com` and only see `https://www.github.com` then it's because you're reading these intructions right now and found the cookies for Github.com. Go back to the database for your course on Memrise and find the cookies there.

When formatting, do not forget the closing brackets, quote marks, or colons. Each one is important and if you miss one the script will surely fail.


# Common errors

## IndexError: list index out of range

Most likely, pagination is not active. To enable pagination, simply add more words.
