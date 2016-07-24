import requests, tempfile, sys, subprocess, logging
from variables import cookies
from multiprocessing import Pool
from lxml.html.soupparser import fromstring
from lxml import html

# logging.getLogger("requests").setLevel(logging.WARNING)

def get_audio_files_from_course(first_database_page, number_of_pages):
	database_urls = []
	for page in range(1, number_of_pages + 1):
		database_urls.append(first_database_page + '?page=' + str(page))
	pool = Pool(processes = 7)
	audio_files = pool.map(get_thing_information, database_urls)
	return fix_list(audio_files)

def get_thing_information(database_url):
	response = requests.get(database_url, cookies = cookies)
	tree = fromstring(response.text)
	div_elements = tree.xpath("//tr[contains(@class, 'thing')]")
	return_object = []
	for div in div_elements:
		chinese_word = div.xpath("td[2]/div/div/text()")[0]
		thing_id = div.attrib['data-thing-id']
		column_number_of_audio = div.xpath("td[contains(@class, 'audio')]/@data-key")[0]
		audio_files = div.xpath("td[contains(@class, 'audio')]/div/div[contains(@class, 'dropdown-menu')]/div")
		number_of_audio_files = len(audio_files)
		return_object.append({'thing_id': thing_id, 'number_of_audio_files': number_of_audio_files, 'chinese_word': chinese_word, 'column_number_of_audio': column_number_of_audio})
	return return_object

def fix_list(given_list):
	new_list = []
	for bunch_of_items in given_list:
		for item in bunch_of_items:
			new_list.append(item)
	return new_list

def download_audio(path):
	response = requests.get(path)
	# write to file
	if response.status_code == requests.codes.ok:
		logging.info('Getting ' + path + ': ' + str(response.status_code))
		temp_file = tempfile.NamedTemporaryFile(suffix='.mp3')
		temp_file.write(response.content)
		return temp_file
	else:
		return False

def download_then_upload_audios(audios):
	pool = Pool(processes=7)
	pool.map(map_function, audios)

def map_function(audio):
	try:
		if audio['number_of_audio_files'] > 0:
			logging.info('SKIPPED: ' + audio['chinese_word'] + ' - Audio files already exist')
			return None
		else:
			print('Adding audio to ' + audio['chinese_word'])
			requests.post('http://soundoftext.com/sounds', data={'text':audio['chinese_word'], 'lang':'zh-CN'}) # warn the server of what file I'm going to need
			temp_file = download_audio('http://soundoftext.com/static/sounds/zh-CN/' + audio['chinese_word'] + '.mp3') #download audio file
			if temp_file == False:
				logging.warning('SKIPPED -- soundoftext.com returned a bad response code on ' + audio['chinese_word'])
				return None
			else:
				subprocess.call(['php', 'upload.php', audio['thing_id'], temp_file.name, course_database_url, audio['column_number_of_audio']]) # upload audio
				temp_file.close()
	except requests.exceptions.RequestException as e:
		logging.warning("SKIPPED - Error uploading  " + audio['chinese_word'])
		loggin.warning(e)
		return None

if __name__ == "__main__":
	logging.basicConfig(filename='main.log',level=logging.DEBUG)
	logging.getLogger("urllib3").setLevel(logging.CRITICAL)
	course_database_url = sys.argv[1]
	number_of_pages = int(html.fromstring(requests.get(course_database_url, cookies=cookies).content).xpath("//div[contains(@class, 'pagination')]/ul/li")[-2].text_content())
	print(number_of_pages)
	words_and_info = get_audio_files_from_course(course_database_url, number_of_pages)
	download_then_upload_audios(words_and_info)	