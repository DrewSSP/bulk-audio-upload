# Bulk Upload Audio for Memrise

This script uploads chinese audio for words that don't have any audio uploaded in any course to which you have editor access

It requires two parameters:
  * **database_page** is the url of the first page for the database of your course
  * **number_of_pages** is the number of pages that exist in your course's database

To run the script:
python main.py **database_page** **number_of_pages**\

For example:
'ipython main.py http://www.memrise.com/course/1036119/hsk-level-6/edit/database/2000662/ 126'

## Set up
make a file in the root directory of your script called 'variables.py' and create a python dictionary of your cookies. It should look something like this:
    cookies = {'_sp_id.7bc7': '06d67edb75b999999.1466999953.100.1555544393.1234573782',
               '_sp_ses.7bc7': '*',
               'csrftoken': 'mxIto89I10jvWe45lt5xBJ8xnQkWayh3',
               'fbm_143688012353890': 'base_domain=.www.memrise.com',
               'fbsr_143688012353890': 'bGNeJtlEkaCEISsa4th4J1-FvygfuhFgBuu3qnnS1M.eyJhbGdvcml03f6OiJITUFDLVNIQTI1NiIsImNvZGUiOiJBUUNxNTh6ekpDMDlpNGNpTjNyaVRYR3VEN0xHZHM1TEJyMmFCVlJBTmVHeVl4WFlWanM1QVRpMDBtSzFwMWNFV2dxa28wUUxrWUVoT0RKLVdQOG1DdHVncjZhSGdxMVBEaEp3MGhTbV9pRXA3ckcxZU02d2M0LTNubFFCVkVaU0tUVml3eXFKdy1FZmxJYTVuZGJZUlhBXzVlNXdGcFFKWWVJem83ZllwcV9COWExdkJ0S3ZFQlB6OGQ2c2w0azMyOWtxcmFyVjJRYXpodVh3WXVlbVc4ejNlUUc5TE11SXJsakxTbW1hOXN3cUREVzEtcl94WlNLRlRucklsV3FxY3kzN0g1UnFVeTRwOFZ0TVVSXzEzd0Z0TjBrNF9PZjgzalJHYVZjZkV5dWFqUDJLQVhSRkxmT3RrU0R5d3lRSnRncGRMVC1ZZTVRTkNKN0xNRWxfcEVVWSIsImlzc3VlZF9hdCI6MTQ2ODY0Mzk4MiwidXNlcl9pZCI6IjUwMzc3MTY3OCJ9',
               'i18next': 'en',
               'sessionid': 'xrxg3zofonxmfmf5gfdgv5444defa71'}