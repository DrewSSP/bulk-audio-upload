import requests, tempfile, sys, subprocess
from variables import cookies
from multiprocessing import Pool
from lxml import html

def upload_file_to_server(thing_id, cell_id, course, file):
	files = {'f': ('whatever.mp3', open(file.name, 'rb'), 'audio/mp3')}
	form_data = { 
		"thing_id": thing_id, 
		"cell_id": cell_id, 
		"cell_type": "column",
		"csrfmiddlewaretoken": cookies['csrftoken']}
	headers = {
		"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:35.0) Gecko/20100101 Firefox/35.0",
		"referer": course}
	post_url = "http://www.memrise.com/ajax/thing/cell/upload_file/"
	r = requests.post(post_url, files=files, cookies=cookies, headers=headers, data=form_data, timeout=60)

def get_audio_files_from_course(first_database_page, number_of_pages):
	database_urls = []
	for page in range(1, number_of_pages + 1):
		database_urls.append(first_database_page + '?page=' + str(page))
	pool = Pool(processes = 7)
	pool.map(get_thing_information, database_urls)

def get_thing_information(database_url):
	print(database_url)
	response = requests.get(database_url, cookies = cookies)
	tree = html.fromstring(response.text)
	div_elements = tree.xpath("//tr[contains(@class, 'thing')]")
	audios = []
	for div in div_elements:
		chinese_word = div.xpath("td[2]/div/div/text()")[0]
		thing_id = div.attrib['data-thing-id']
		column_number_of_audio = div.xpath("td[contains(@class, 'audio')]/@data-key")[0]
		audio_files = div.xpath("td[contains(@class, 'audio')]/div/div[contains(@class, 'dropdown-menu')]/div")
		number_of_audio_files = len(audio_files)
		audios.append({'thing_id': thing_id, 'number_of_audio_files': number_of_audio_files, 'chinese_word': chinese_word, 'column_number_of_audio': column_number_of_audio})
	sequence_through_audios(audios)

def download_audio(path):
	response = requests.get(path)
	if response.status_code == requests.codes.ok:
		temp_file = tempfile.NamedTemporaryFile(suffix='.mp3')
		temp_file.write(response.content)
		return temp_file
	else:
		return False

def sequence_through_audios(audios):
	for audio in audios:
		if audio['number_of_audio_files'] > 0:
			continue
		else:
			print('Adding audio to ' + audio['chinese_word'])
			requests.post('http://soundoftext.com/sounds', data={'text':audio['chinese_word'], 'lang':'zh-CN'}) # warn the server of what file I'm going to need
			temp_file = download_audio('http://soundoftext.com/static/sounds/zh-CN/' + audio['chinese_word'] + '.mp3') #download audio file
			if temp_file == False:
				continue
			else:
				upload_file_to_server(audio['thing_id'], audio['column_number_of_audio'], course_database_url, temp_file)
				temp_file.close()

if __name__ == "__main__":
	course_database_url = sys.argv[1]
	number_of_pages = int(html.fromstring(requests.get(course_database_url, cookies=cookies).content).xpath("//div[contains(@class, 'pagination')]/ul/li")[-2].text_content())
	get_audio_files_from_course(course_database_url, number_of_pages)
