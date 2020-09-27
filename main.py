# required modules:
# pip install requests
# pip install lxml
# pip install gTTS

import requests, sys
from lxml import html
from lxml.etree import tostring
from enum import Enum
import argparse
import getpass
import os
import shutil
import concurrent.futures

base_url = 'https://app.memrise.com/'
endpoint = 'https://api.soundoftext.com/sounds/'
os.system('chcp 65001')

def upload_file_to_server(thing_id, cell_id, course, file_name, original_word):
	openfile = open(file_name, 'rb')
	files = {'f': ('whatever.mp3', openfile, 'audio/mp3')}
	form_data = {
		"thing_id": thing_id,
		"cell_id": cell_id,
		"cell_type": "column",
		"csrfmiddlewaretoken": login_token }
	s.headers["referer"] = course
	s.headers["Cookie"] = "csrftoken=" + login_token + "; sessionid_2=" + s.cookies["sessionid_2"]
	post_url = base_url + "ajax/thing/cell/upload_file/"
	r = s.post(post_url, files=files, data=form_data, timeout=60)
	if r.status_code != requests.codes.ok:
		print(b'Upload for word "' + original_word.encode('utf-8') + b'" failed with error: ' + str(r.status_code).encode('utf-8'))
		print('request headers:')
		print(r.request.headers)
		print('response headers:')
		print(r.headers)
	else:
		print(b'Upload for word "' + original_word.encode('utf-8') + b'" succeeded')
	openfile.close()

def get_thing_information(database_url):
	print('fetching: ' + database_url)
	response = s.get(database_url)
	tree = html.fromstring(response.text)
	div_elements = tree.xpath("//tr[contains(@class, 'thing')]")
	audios = []
	for div in div_elements:
		thing_id = div.attrib['data-thing-id']
		try:
			word = div.xpath("td[2]/div/div/text()")[0]
		except IndexError:
			print("failed to get the word of item with id " + str(thing_id) + ' on ' + str(database_url))
			print("   source: " + div.text_content())
			continue
		try:
			column_number_of_audio = div.xpath("td[contains(@class, 'audio')]/@data-key")[0]
			audio_files = div.xpath("td[contains(@class, 'audio')]/div/div[contains(@class, 'dropdown-menu')]/div")
		except:
			print( '\nError. Course seems to have no audio column.')
			exit()
			
		number_of_audio_files = len(audio_files)
		audios.append({'thing_id': thing_id, 'number_of_audio_files': number_of_audio_files, 'word': word, 'column_number_of_audio': column_number_of_audio})
	if args.engine == Engines.gtts:
		sequence_through_audios_gtts(audios, database_url)
	else:
		sequence_through_audios_soundoftext(audios, database_url)

def get_audio_files_from_course(first_database_page, number_of_pages):
	database_urls = []

	for page in range(1, number_of_pages + 1):
		if (args.pooled):
			database_urls.append(first_database_page + '?page=' + str(page))
		else:
			get_thing_information(first_database_page + '?page=' + str(page))
			
	if (args.pooled):
		# We can use a with statement to ensure threads are cleaned up promptly
		with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
			future_to_url = {executor.submit(get_thing_information, url): url for url in database_urls}
	print('Course done: ' + first_database_page)

def sequence_through_audios_gtts(audios, page_url):        
	for audio in audios:
		if audio['number_of_audio_files'] >= args.count:
			# print(audio['foreign_word'] + ' has audio already ')
			continue
		else:
			try:
				from gtts import gTTS
			except:
				print('gTTS engine not installed. use: pip install gTTS')
				exit()

			tts = gTTS(text=audio['word'], lang=args.language)
			temp_file = 'mp3\\' + audio['thing_id'] + '.mp3'
			tts.save(temp_file)
			upload_file_to_server(audio['thing_id'], audio['column_number_of_audio'], page_url, temp_file, audio['word'])
			if (not args.keepaudio):
				os.remove(temp_file)

def download_audio(id):
	resp = requests.get(endpoint + id)
	if resp.ok and resp.json()['status'] == 'Done':
		resp = requests.get(resp.json()['location'])
		if len(resp.content) < 1000:
			return 'Not enough data downloaded from soundoftext.com'
		elif resp.ok:
			temp_file = 'mp3\\' + id + '.mp3'
			openfile = open(temp_file, 'wb')
			openfile.write(resp.content)
			openfile.flush()
			return openfile
	return 'Bad response when downloading file'

def sequence_through_audios_soundoftext(audios, page_url):
	for audio in audios:
		if audio['number_of_audio_files'] >= args.count:
			continue
		else:
			args_request = {
				'engine': 'Google',
				'data': {
					'text':audio['word'],
					'voice':args.language,
				}
			}
			response = requests.post(endpoint, json=args_request) # warn the server of what file I'm going to need
			if response.ok:
				temp_file = download_audio(response.json()["id"]) #download audio file
			else:
				print('Sound could not be requested from soundoftext.com:' + response.json()['message'] )
				print(response.json())
				print()
				print('See: https://soundoftext.com/docs#voices')
				exit()

			if isinstance(temp_file, str):
				print(audio['word'] + ' skipped: ' + temp_file)
				continue
			else:			
				temp_file_name = temp_file.name
				upload_file_to_server(audio['thing_id'], audio['column_number_of_audio'], page_url, temp_file_name, audio['word'])
				temp_file.close()				
				if (not args.keepaudio):
					os.remove(temp_file_name)
				# print(audio['word'] + ' succeeded')

def python2and3input(output):
	#Works in Python 2 and 3:
	if hasattr(__builtins__, 'raw_input'): 
		input = raw_input
		#print("python 2 detected")
	else:
		from builtins import input
	#try: input = raw_input
	#except NameError: 
	#	print("python 3 detected")
	#	pass
	return input(output)

class Engines(Enum):
	gtts = 'gTTS'
	sot = 'SOT'

	def __str__(self):
		return self.value

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Bulk Upload Audio for Memrise',
					 formatter_class=argparse.RawDescriptionHelpFormatter,
					 epilog="""Where URL is the url of the first page after you go to your course's database.
\n
For example:
python main.py http://app.memrise.com/course/1036119/hsk-level-6/edit/database/2000662/\n
\n
This will add audio to any words that are missing it for the course:
http://app.memrise.com/course/1036119/hsk-level-6.
\n
This course's database page is:
http://app.memrise.com/course/1036119/hsk-level-6/edit/database/2000662/.\n
\n
Parameters can also be set in a configuration file 'variables.py'. See README.md for details.""")
	parser.add_argument('URLs', metavar='URL', type=str, nargs='*',
				help="is the url of the first page after you go to your course's database")
	parser.add_argument('-u', '--user', default='',
				help='user name or email address to login at memrise.com (if not provided it will be asked for interactively)')
	parser.add_argument('-p', '--password', default='',
				help='password to login at memrise.com (if not provided it will be asked for interactively)')
	parser.add_argument('-l', '--language', default='',
				help='language of the audio file to be produced by Google Text-to-Speech (if not provided it will be asked for interactively)')
	parser.add_argument('-k', '--keepaudio', action='store_true',
				help='don\'t deleted generated MP3 files in subdirectory \'mp3\' after upload')
	parser.add_argument('-e', '--engine', type=Engines, default=Engines.gtts, choices=list(Engines),
				help='sound engine to be used. gTTS = "google Text To Speech", SOT = "soundoftext.com" (default is gTTS)')
	parser.add_argument('-c', '--count', type=int, default=1,
				help='number of audios allowed per word  (default is 1). This can be useful if you want to enforce another audio version.')
	parser.add_argument('-o', '--pooled', action='store_true',
				help='Enable parallel fetching')

	# parameters are initialized in this order:
	# 1. from command line arguments
	# 2. (if not yet provided) from file "variables.py" 
	# 3. (if still not provided) user input
	args = parser.parse_args()
	
	if (args.user == ''):
		try:
			from variables import user
			args.user = user
		except:
			args.user = python2and3input("User name or Email: ")
	if (args.password == ''):
		try:
			from variables import password
			args.password = password
		except:
			args.password = getpass.getpass()
	if (args.language == ''):
		try:
			from variables import language
			args.language = language
		except:
			args.language = python2and3input("Language code, e.g. 'en': ")
	if (not args.URLs):
		try:
			from variables import course_database_url
			args.URLs.append( course_database_url )
		except:
			args.URLs.append( python2and3input("URL of database of Memrise course: "))

        
	login_url = base_url + 'login/'
	s = requests.session()
	s.headers.update({'user-agent': 'Mozilla/5.0', 'referer': login_url})
	
	login_page = s.get(login_url).content	
	login_token = html.fromstring(login_page).xpath("//form/input[contains(@name, 'csrfmiddlewaretoken')]/@value")[0]

	r_login = s.post(login_url, 
		data={ 'username': args.user, 'password': args.password, 'csrfmiddlewaretoken' : login_token })
	if (r_login.status_code != requests.codes.ok):
		print( 'login failed with error ' + str(r_login.status_code))
		exit()
	print( 'Login succeeded...')
	
	# make sure we have the working directory
	if (not os.path.isdir('mp3')):
		os.mkdir('mp3') 
	
	for course_database_url in args.URLs:
		print ('Processing URL : ' + course_database_url)
		headers = {
			"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:35.0) Gecko/20100101 Firefox/35.0",
			"referer": course_database_url}
		r = s.get(course_database_url, headers=headers)
		test = r.content

		# depending on the number of pages of the course the actual maximum number can be on different positions
		try:
			number_of_pages = int(html.fromstring(test).xpath("//div[contains(@class, 'pagination')]/ul/li")[-2].text_content())
		except:
			try:
				number_of_pages = int(html.fromstring(test).xpath("//div[contains(@class, 'pagination')]/ul/li")[-1].text_content())
			except:
				try:
					number_of_pages = int(html.fromstring(test).xpath("//div[contains(@class, 'pagination')]/ul/li")[0].text_content())
				except:
					print (test)
					print( '\nError. Could not parse number of pages from HTML above.')
					print( 'Please check if you are logged in and that you provided the link to the database of the Memrise course.')
					exit()
		print('number of pages: ' + str(number_of_pages))
		if (args.keepaudio):
			print('   keeping audio files in subdirectory "mp3"...')
		get_audio_files_from_course(course_database_url, number_of_pages)
	print('all done')
	if (not args.keepaudio):
		shutil.rmtree('mp3', ignore_errors=True)
