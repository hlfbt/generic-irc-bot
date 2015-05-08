import gib
import re
import zlib
import json
import html.parser
from urllib.parse import quote_plus
from urllib.request import Request, urlopen, HTTPRedirectHandler, build_opener

name = "Google"

class Google:
  command = ".g"
  help = gib.ircstr("´Isearchterm´N | Does a quick google search.")
  shelp = gib.ircstr("´Iquery´N")
  resultre = re.compile('<h3 class="r"[^>]*><a href="([^"]+)"[^>]+>(.+)</a>')
  tire = re.compile('<title>(.*)</title>')
  htmlparser = html.parser.HTMLParser()
  apiKey = ''

  class HTMLStripper(html.parser.HTMLParser):
    class HTMLP(html.parser.HTMLParser):
      _data = ""
      def handle_data(self, data):
        self._data += str(data)
      def r(self):
        self._data = ""
        self.reset()
    htmlp = HTMLP()
    def strip(self, data):
      self.htmlp.feed(str(data))
      self.htmlp.close()
      nudes = self.htmlp._data
      self.htmlp.r()
      return nudes

  htmlstripper = HTMLStripper()

  class RedirectHandler(HTTPRedirectHandler):
    def http_error_403(self, req, fp, code, msg, headers):
      return 0
    def http_error_503(self, req, fp, code, msg, headers):
      return 0
    def http_error_302(self, req, fp, code, msg, headers):
      result = HTTPRedirectHandler.http_error_302(self, req, fp, code, msg, headers)
      result.status = code
      return result
    def http_error_302(self, req, fp, code, msg, headers):
      result = HTTPRedirectHandler.http_error_302(self, req, fp, code, msg, headers)
      result.status = code
      return result

  def main(self, args, env = {}):
    if not len(args): return ''
    link = self.search(args)
    if len(link):
      if len(link[1]): return gib.ircstr("{0} - ´B{1}´N").format(link[0], link[1])
      else: return str(link[0])
    else: return gib.ircstr("'´I{0}´N' did not match any documents.").format(' '.join(args))

  def search(self, query):
    response = self.open_page("http://www.google.com/search?ie=UTF-8&oe=UTF-8&sourceid=navclient&complete=0&hl=en&q={0}".format('+'.join([quote_plus(s) for s in query])))
    link = [response.url, '']
    found = True
    match = ''
    if link[0].find('google.com/search') != -1 or link[0].find('google.de/search') != -1:
      found = False
      pagestr = ''
      for line in iter(response.readline, b''):
        line = line.decode('utf8')
        pagestr += line
        if line.find('<h3 class="r">') != -1:
          match = line.split('</h3>')[0]
          found = True
          break
      if found and len(match):
        match = self.resultre.search(match)
        link[0] = self.htmlparser.unescape(match.group(1))
        link[1] = self.htmlstripper.strip(self.htmlparser.unescape(match.group(2)))
# Since we retrieve the title from Google we don't need to look it up again (with the chance of the page actually blocking us or similar)
#        if len(link[0]) and link[0]!=html.parser.HTMLParser().unescape(match): link[1] = self.get_title(opener.open(Request(link[0], None, {"User-Agent":"Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.2 Safari/537.36"})))
      else: link = [self.shorten(link[0]), self.get_title(pagestr)]
    else: link = [link[0], self.get_title(response)]
    return link

  def shorten(self, longUrl):
    data = "{{'longUrl': '{0}', 'key': '{1}'}}".format(longUrl.replace("'", r"\'"), self.apiKey).encode('utf8')
    headers = {"Content-Length": len(data), "Content-Type": "application/json"}
    req = Request('https://www.googleapis.com/urlshortener/v1/url', data, headers)
    page = urlopen(req)
    page = b''.join(page.readlines()).decode('utf8')
    page = json.loads(page)
    return page["id"] if ("id" in page and page["id"] != "") else longUrl

  def open_page(self, url):
    req = Request(url, None, {"User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.91 Safari/537.36"})
    opener = build_opener(self.RedirectHandler())
    return opener.open(req)

  def get_title(self, page, max_title_length=128):
    err = False
    try:
      page = b''.join(page.readlines())
      try: page = page.decode('utf8')
      except UnicodeDecodeError:
        try: page = zlib.decompress(page, 15+32)
        except zlib.error: err = True
    except:
      if not isinstance(page, str): err = True
    if not err:
      title = self.tire.search(page.replace('\n', ''))
      title = title.groups()[0] if title and len(title.groups()) > 0 else ''
    else: title = ''
    return title if len(title) < max_title_length else title[0:max_title_length-1]

