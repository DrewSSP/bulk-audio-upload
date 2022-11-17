# required modules:
# pip install requests
# pip install bs4
# pip install gTTS

import requests, sys
from enum import Enum
import argparse
import getpass
import os
import shutil
import concurrent.futures

import memrise

endpoint = 'https://api.soundoftext.com/sounds/'
os.system('chcp 65001')


def handle_single_database_page(database_url):
	print('fetching: ' + database_url)
	things = memriseService.get_thing_information(database_url)
	if args.engine == Engines.gtts:
		sequence_through_audios_gtts(things, database_url)
	else:
		sequence_through_audios_soundoftext(things, database_url)

def get_audio_files_from_course(first_database_page, number_of_pages):
	database_urls = []

	for page in range(1, number_of_pages + 1):
		if (args.pooled):
			database_urls.append(first_database_page + '?page=' + str(page))
		else:
			handle_single_database_page(first_database_page + '?page=' + str(page))
			
	if (args.pooled):
		# We can use a with statement to ensure threads are cleaned up promptly
		with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
			future_to_url = {executor.submit(handle_single_database_page, url): url for url in database_urls}
	print('Course done: ' + first_database_page)

def sequence_through_audios_gtts(audios : memrise.MemriseThing, page_url):        
	for audio in audios:
		if len(audio.audio_files) >= args.count:
			# print(audio['foreign_word'] + ' has audio already ')
			continue
		else:
			try:
				from gtts import gTTS
			except:
				print('gTTS engine not installed. use: pip install gTTS')
				exit()

			tts = gTTS(text=audio.original_word, lang=args.language)
			temp_file = 'mp3\\' + audio.thing_id + '.mp3'
			tts.save(temp_file)
			audio.file_name = temp_file
			memriseService.upload_file_to_server( page_url, audio)
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

def sequence_through_audios_soundoftext(audios : memrise.MemriseThing, page_url):
	for audio in audios:
		if len(audio.audio_files) >= args.count:
			continue
		else:
			args_request = {
				'engine': 'Google',
				'data': {
					'text':audio.original_word,
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
				print(audio.original_word + ' skipped: ' + temp_file)
				continue
			else:			
				audio.file_name = temp_file.name
				memriseService.upload_file_to_server(page_url, audio)
				temp_file.close()				
				if (not args.keepaudio):
					os.remove(audio.file_name)
				# print(audio.original_word + ' succeeded')

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
	parser.add_argument('-d', '--debug', default=False, action='store_true',
				help='Print debug output')

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

	memriseService = memrise.Service()
	memriseService.SetDebugMode()

	if not memriseService.isLoggedIn():
		if memriseService.login(args.user,args.password):
			print('login successful')
		else:
			print( "Couldn't log in. Please check your credentials.")
			exit
		
	print( 'Login succeeded...')

	if (args.keepaudio):
		print('   keeping audio files in subdirectory "mp3"...')

	# make sure we have the working directory
	if (not os.path.isdir('mp3')):
		os.mkdir('mp3') 

	for course_database_url in args.URLs:
		print('Getting database links of course ' + course_database_url )
		for database in memriseService.getDatabases(course_database_url):
			url = database[0]
			number_of_pages = database[1]
			print ('Processing database URL : ' + url)
			print('number of pages: ' + str(number_of_pages))
			
			get_audio_files_from_course(url, number_of_pages)

	print('all done')
	if (not args.keepaudio):
		shutil.rmtree('mp3', ignore_errors=True)
