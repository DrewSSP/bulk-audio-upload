# required modules:
# pip install gTTS

import requests, tempfile, sys
from lxml import html
from lxml.etree import tostring
from enum import Enum

import argparse
import getpass
import os
import shutil

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
	post_url = "https://www.memrise.com/ajax/thing/cell/upload_file/"
	r = s.post(post_url, files=files, data=form_data, timeout=60)
	if r.status_code != requests.codes.ok:
		print(b'Upload for word "' + original_word.encode('utf-8') + b'" failed with error: ' + str(r.status_code))
	else:
		print(b'Upload for word "' + original_word.encode('utf-8') + b'" succeeded')
	openfile.close()

def get_audio_files_from_course(first_database_page, number_of_pages):
	for page in range(1, number_of_pages + 1):
		get_thing_information(first_database_page + '?page=' + str(page))
	print('Course done: ' + first_database_page)

def get_thing_information(database_url):
	print('fetching: ' + database_url)
	response = s.get(database_url)
	tree = html.fromstring(response.text)
	div_elements = tree.xpath("//tr[contains(@class, 'thing')]")
	audios = []
	for div in div_elements:
		thing_id = div.attrib['data-thing-id']
		try:
			foreign_word = div.xpath("td[2]/div/div/text()")[0]
		except IndexError:
			print("failed to get the word of item with id " + str(thing_id) + ' on ' + str(database_url))
			continue
		try:
			column_number_of_audio = div.xpath("td[contains(@class, 'audio')]/@data-key")[0]
			audio_files = div.xpath("td[contains(@class, 'audio')]/div/div[contains(@class, 'dropdown-menu')]/div")
		except:
			print( '\nError. Course seems to have no audio column.')
			exit()
			
		number_of_audio_files = len(audio_files)		
		audios.append({'thing_id': thing_id, 'number_of_audio_files': number_of_audio_files, 'foreign_word': foreign_word, 'column_number_of_audio': column_number_of_audio})
	if args.engine == Engines.gtts:
		sequence_through_audios_gtts(audios, database_url)
	else:
		sequence_through_audios_soundoftext(audios, database_url)

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

			tts = gTTS(text=audio['foreign_word'], lang=args.language)
			temp_file = 'mp3\\' + audio['thing_id'] + '.mp3'
			tts.save(temp_file)
			upload_file_to_server(audio['thing_id'], audio['column_number_of_audio'], page_url, temp_file, audio['foreign_word'])
			if (not args.keepaudio):
				os.remove(temp_file)

def download_audio(path, temp_file_name):
	response = requests.get(path)
	if len(response.content) < 100:
		return 'Not enough data downloaded from soundoftext.com'
	elif response.status_code == requests.codes.ok:		
		temp_file = open( temp_file_name, 'wb') # tempfile.NamedTemporaryFile(suffix='.mp3')
		temp_file.write(response.content)
		temp_file.flush()
		return temp_file
	else:
		return 'Bad response when downloading file'

def sequence_through_audios_soundoftext(audios, page_url):
	for audio in audios:
		if audio['number_of_audio_files'] >= args.count:
			continue
		else:
			# print(audio['foreign_word'])
			payload = {
				'engine': "Google",
				"data": {
					"text": audio['foreign_word'],
					"voice": args.language # "de-DE"
				}
			}
			# print(payload)
			request_result = requests.post('https://api.soundoftext.com/sounds', json=payload).json()
			if not request_result['success'] :
				print('Sound could not be requested from soundoftext.com:' + request_result['message'] )
				print(request_result)
				print()
				print('See: https://soundoftext.com/docs#voices')
				exit()

			# print(requestresult)
			audio_id = request_result['id'] 
			# print(audio_id)
			download_request = requests.get('https://api.soundoftext.com/sounds/' + audio_id).json()
			download_url = download_request['location']
			temp_file_name = 'mp3\\' + audio['thing_id'] + '.mp3'
			temp_file = download_audio(download_url, temp_file_name) 
			if isinstance(temp_file, str):
				print(audio['foreign_word'] + ' skipped: ' + temp_file)
				continue
			else:
				temp_file.close()
				upload_file_to_server(audio['thing_id'], audio['column_number_of_audio'], page_url, temp_file_name, audio['foreign_word'])
				# upload_file_to_server(audio['thing_id'], audio['column_number_of_audio'], course_database_url, temp_file)
				if (not args.keepaudio):
					os.remove(temp_file_name)
				# print(audio['foreign_word'] + ' succeeded')

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
ipython main.py http://www.memrise.com/course/1036119/hsk-level-6/edit/database/2000662/\n
\n
This will add audio to any words that are missing it for the course:
http://www.memrise.com/course/1036119/hsk-level-6.
\n
This course's database page is:
http://www.memrise.com/course/1036119/hsk-level-6/edit/database/2000662/.\n""")
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
				help='number of audios allowed per word  (default is 1)')


	args = parser.parse_args()
	if (not args.URLs):
		parser.print_help()
		print()
	
	if (args.user == ''):
		args.user = python2and3input("User name or Email: ")
	if (args.password == ''):
		args.password = getpass.getpass()
	if (args.language == ''):
		args.language = python2and3input("Language code, e.g. 'en': ")
	if (not args.URLs):		
		args.URLs.append(python2and3input("URL of database of Memrise course: "))
		
	s = requests.session()
	s.headers.update({'user-agent': 'Mozilla/5.0', 'Referer':'https://www.memrise.com/login/'})
	
	login_page = s.get('https://www.memrise.com/login/').content
	login_token = html.fromstring(login_page).xpath("//form/input[contains(@name, 'csrfmiddlewaretoken')]/@value")[0]

	r_login = s.post('https://www.memrise.com/login/', 
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