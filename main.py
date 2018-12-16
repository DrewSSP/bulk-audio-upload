# required modules:
# pip install gTTS

import requests, tempfile, sys
# from variables import cookies
from multiprocessing import Pool
from lxml import html
from lxml.etree import tostring

from gtts import gTTS
import argparse
import getpass
import os

def upload_file_to_server(thing_id, cell_id, course, file_name, original_word):
	files = {'f': ('whatever.mp3', open(file_name, 'rb'), 'audio/mp3')}
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
		print('Upload for word "' + original_word + '" failed with error: ' + str(r.status_code))
	else:
		print('Upload for word "' + original_word + '" succeeded')

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
	sequence_through_audios(audios, database_url)

def sequence_through_audios(audios, page_url):        
	for audio in audios:
		if audio['number_of_audio_files'] > 0:
			# print(audio['foreign_word'] + ' has audio already ')
			continue
		else:
			tts = gTTS(text=audio['foreign_word'], lang='en')
			temp_file = 'mp3\\' + audio['thing_id'] + '.mp3'
			tts.save(temp_file)
			upload_file_to_server(audio['thing_id'], audio['column_number_of_audio'], page_url, temp_file, audio['foreign_word'])
			os.remove(temp_file)

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
			    help='an integer for the accumulator')
	parser.add_argument('-l', '--login', default='',
			    help='user name or email address to login at memrise.com (if not provided it will be asked for interactively)')
	parser.add_argument('-p', '--password', default='',
			    help='password to login at memrise.com (if not provided it will be asked for interactively)')

	args = parser.parse_args()
	if (not args.URLs):
		parser.print_help()
		print()
                
	if (args.login == ''):
		args.login = input("User name or Email:")
	if (args.password == ''):
		args.password = getpass.getpass()
	if (not args.URLs):		
		args.URLs.append(input("URL of database of Memrise course:"))
		
	s = requests.session()
	s.headers.update({'user-agent': 'Mozilla/5.0', 'Referer':'https://www.memrise.com/login/'})
	
	login_page = s.get('https://www.memrise.com/login/').content
	login_token = html.fromstring(login_page).xpath("//form/input[contains(@name, 'csrfmiddlewaretoken')]/@value")[0]

	r_login = s.post('https://www.memrise.com/login/', 
		data={ 'username': args.login, 'password': args.password, 'csrfmiddlewaretoken' : login_token })
	if (r_login.status_code != requests.codes.ok):
		print( 'login failed with error ' + str(r_login.status_code))
		exit()
	print( 'Login succeeded...')

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
		get_audio_files_from_course(course_database_url, number_of_pages)
	print('all done')
