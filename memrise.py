# taken from:
# https://github.com/wilddom/memrise2anki-extension

import urllib.request, urllib.error, urllib.parse, http.cookiejar, http.client
import re, time, os.path, json, functools, uuid, errno
import bs4
import requests.sessions

base_url_plain = 'https://app.memrise.com'

class MemriseThing(object):
    def __init__(self):
        self.thing_id = ""
        self.audio_cell_id = -1 # column_number_of_audio
        self.file_name = ""
        self.original_word = ""
        self.audio_files = []


class IncompleteReadHttpAndHttpsHandler(urllib.request.HTTPHandler, urllib.request.HTTPSHandler):
    def __init__(self, debuglevel=0):
        urllib.request.HTTPHandler.__init__(self, debuglevel)
        urllib.request.HTTPSHandler.__init__(self, debuglevel)

    @staticmethod
    def makeHttp10(http_class, *args, **kwargs):
        h = http_class(*args, **kwargs)
        h._http_vsn = 10
        h._http_vsn_str = "HTTP/1.0"
        return h

    @staticmethod
    def read(response, reopen10, amt=None):
        if hasattr(response, "response10"):
            return response.response10.read(amt)
        else:
            try:
                return response.read_savedoriginal(amt)
            except http.client.IncompleteRead:
                response.response10 = reopen10()
                return response.response10.read(amt)

    def do_open_wrapped(self, http_class, req, **http_conn_args):
        response = self.do_open(http_class, req, **http_conn_args)
        response.read_savedoriginal = response.read
        reopen10 = functools.partial(self.do_open, functools.partial(self.makeHttp10, http_class, **http_conn_args), req)
        response.read = functools.partial(self.read, response, reopen10)
        return response

    def http_open(self, req):
        return self.do_open_wrapped(http.client.HTTPConnection, req)

    def https_open(self, req):
        return self.do_open_wrapped(http.client.HTTPSConnection, req, context=self._context, check_hostname=self._check_hostname)

class MemriseError(RuntimeError):
    pass

class LevelNotFoundError(MemriseError):
    pass

class MemNotFoundError(MemriseError):
    pass

class Service(object):
    def __init__(self, downloadDirectory=None, cookiejar=None):
        self.downloadDirectory = downloadDirectory
        if cookiejar is None:
            cookiejar = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(IncompleteReadHttpAndHttpsHandler, urllib.request.HTTPCookieProcessor(cookiejar))
        self.session = requests.Session()
        self.session.cookies = cookiejar
    def SetDebugMode(self):
        self.debugOutput = True

    def openWithRetry(self, url, maxAttempts=5, attempt=1):
        try:
            return self.opener.open(url)
        except urllib.error.URLError as e:
            if e.errno == errno.ECONNRESET and maxAttempts > attempt:
                time.sleep(1.0*attempt)
                return self.openWithRetry(url, maxAttempts, attempt+1)
            else:
                raise
        except http.client.BadStatusLine:
            # not clear why this error occurs (seemingly randomly),
            # so I regret that all we can do is wait and retry.
            if maxAttempts > attempt:
                time.sleep(0.1)
                return self.openWithRetry(url, maxAttempts, attempt+1)
            else:
                raise

    def isLoggedIn(self):
        response = self.session.get(base_url_plain + '/v1.17/me/', headers={'Referer': 'https://www.memrise.com/app'})
        return response.status_code == 200

    def login(self, username, password):
        signin_page = self.session.get(base_url_plain + "/signin")
        signin_soup = bs4.BeautifulSoup(signin_page.content, "html.parser")
        info_json = json.loads(signin_soup.select_one("#__NEXT_DATA__").string)
        client_id = info_json["runtimeConfig"]["OAUTH_CLIENT_ID"]
        signin_data = {
            'username': username,
            'password': password,
            'client_id': client_id,
            'grant_type': 'password'
        }

        obtain_login_token_res = self.session.post(base_url_plain + '/v1.17/auth/access_token/', json=signin_data)
        if not obtain_login_token_res.ok:
            return False
        token = obtain_login_token_res.json()["access_token"]["access_token"]

        actual_login_res = self.session.get(base_url_plain + '/v1.17/auth/web/', params={'invalidate_token_after': 'true', 'token': token})

        if not actual_login_res.json()["success"]:
            return False

        return True

    
    def getDatabases(self, courseUrl):
        result = []
        urls = []
        response = self.openWithRetry(courseUrl)
        soup = bs4.BeautifulSoup(response.read(), 'html.parser')
        for href in soup.find_all('a', {'href': lambda link: link and bool(re.match('/course/.*/edit/database/\d*/', link))}):
            urls.append( base_url_plain + href.get('href')) 

        for db_url in urls:
            response = self.openWithRetry(db_url)
            max = 0
            soup = bs4.BeautifulSoup(response.read(), 'html.parser')
            pag = soup.find('div', {'class':lambda x: x and 'pagination' in x.split() })
            for page in pag.find_all('a', {'href' : lambda link: link and bool(re.match('\?page=\d+', link))}):
                lnk = page.get('href')
                match = re.match('.*=(\d+).*', lnk)
                if match:
                    nr = int(match.group(1))
                    if nr > max:
                        max = nr
            result.append([db_url, max])
        return result

    def get_thing_information(self, database_url):
        response = self.openWithRetry(database_url)
        soup = bs4.BeautifulSoup(response.read(), 'html.parser')
        things = []
        for div in soup.find_all('tr', {'class': lambda x: x and 'thing' in x.split() }):
            thing_id = div.get('data-thing-id')
            try:
                word = div.find_all('td')[1].find('div', {'class' : 'text'}).string
            except IndexError:
                print("failed to get the word of item with id " + str(thing_id) + ' on ' + str(database_url))
                print("   source: " + div.prettify())
                continue
            try:

                # <td class="cell text column" data-key="1" data-cell-type="column">
                column_number_of_audio = int(div.find('td', {'class': lambda x: x and 'audio' in x.split()}).get('data-key'))                 

                # <a class="audio-player audio-player-hover url" href="#"
                #  data-url="https://static.memrise.com/uploads/things/audio/198068865_181115_0557_13.mp3"></a>
                audio_files = []
                for href in div.find_all('a', {'data-url' : lambda x: x }):
                    audio_files.append(href.get('data-url'))

            except:
                print( '\nError. Course seems to have no audio column.')
                return things

            a = MemriseThing()
            a.thing_id = thing_id
            a.audio_files = audio_files
            a.original_word = word
            a.audio_cell_id = column_number_of_audio

            things.append(a)
        return things

    def upload_file_to_server(self, course, thing_info : MemriseThing):
        thing_id = thing_info.thing_id
        cell_id = thing_info.audio_cell_id
        file_name = thing_info.file_name
        original_word = thing_info.original_word

        openfile = open(file_name, 'rb')
        files = {'f': ('ignored.mp3', openfile, 'audio/mp3')}
        csrtoken = requests.utils.dict_from_cookiejar(self.session.cookies)["csrftoken"]

        form_data = {
            "thing_id": thing_id,
            "cell_id": cell_id,
            "cell_type": "column",
            "csrfmiddlewaretoken": csrtoken }
        self.session.headers["referer"] = course
        post_url = base_url_plain + "/ajax/thing/cell/upload_file/"
        r = self.session.post(post_url, files=files, data=form_data, timeout=60)
        openfile.close()
        if r.status_code != requests.codes.ok:
            if (self.debugOutput):
                print(b'Upload for word "' + original_word.encode('utf-8') + b'" failed with error: ' + str(r.status_code).encode('utf-8'))
                print('request headers:')
                print(r.request.headers)
                print('response headers:')
                print(r.headers)
            raise MemriseError('Upload for word "' + original_word + '" failed with error: ' + str(r.status_code))
        else:
            if (self.debugOutput):
                print(b'Upload for word "' + original_word.encode('utf-8') + b'" succeeded')
        

