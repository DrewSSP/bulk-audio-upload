import requests
import sys
import re
import os
import subprocess
import click
import logging

def append_ns_for_regex(number_of_ns):
	compiled_string = ''
	for n in range(number_of_ns-1):
		compiled_string += '.*\\n.*\\n.*\\n.*\\n'
	return compiled_string

def get_words_and_info(course_database_url, column_of_audio):
	number_of_database_pages = int(sys.argv[2])+1
	cookies = dict(__uvt='',
		__utmt='6',
		csrftoken='2N828n66bh5Alhbc463wYtoqpyWosyON',
		sessionid='zj8suxtx841zlwrn10o6x3suzdjw9wpt',
		__utma='216705802.691983187.1416840006.1429942996.1430039373.8',
		__utmb='216705802.6.10.1440401822',
		__utmc='216705802',
		__utmz='216705802.1416840006.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)',
		uvts='2Mnc8QsWzuuv8GVh')
	words_and_info = list()
	with click.progressbar(range(1, number_of_database_pages), width=0, label='Getting database info') as bar:
		for n in bar:
			response = requests.get(course_database_url+'?page='+str(n), cookies=cookies)
			regex_pattern = re.compile('data-thing-id="(.*?)".*\\n.*\\n.*\\n.*\\n.*"text">(.*?)</div>' + append_ns_for_regex(column_of_audio) + '.*\\n.*\\n.*no audio file')
			for (id, word) in re.findall(regex_pattern, response.text):
				words_and_info.append(dict(
					id=id,
					word=word))
				print id + ' ' + word
	return words_and_info

def download_audio(path):
	with open('temp.mp3', "wb") as file:
		# get request
		response = requests.get(path)
		# write to file
		if response.status_code == requests.codes.ok:
			file.write(response.content)
		else:
			return False

def main():
	logging.basicConfig(filename='main.log',level=logging.DEBUG)
	course_database_url = sys.argv[1]
	column_of_audio = int(sys.argv[3])
	# download database list and extract the words, their ids, and whther they have audio
	words_and_info = get_words_and_info(course_database_url, column_of_audio)
	with click.progressbar(words_and_info, width=0, label='Uploading audio') as bar:
		for item in bar:
			try:
				logging.info('getting audio for ' + item['word'])
				requests.post('http://soundoftext.com/sounds', data={'text':item['word'], 'lang':'zh-CN'}) # for some reason the server doesn't guarantee that a file will be there until we trick it into thinking that we're using the form on the front page
				audio = download_audio('http://soundoftext.com/static/sounds/zh-CN/' + item['word'] + '.mp3') # download temporary audio file
				if audio == False:
					continue
				else:
					subprocess.call(['php', 'upload.php', item['id'], 'temp.mp3', course_database_url, str(column_of_audio)]) # upload audio
			except requests.exceptions.RequestException as e:
				logging.warning(e)
				continue

if __name__ == "__main__":
	main()