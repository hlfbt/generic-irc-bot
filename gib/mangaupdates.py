import gib
import google
import lxml.html
import html.parser

name = "BakaUpdates"

class BakaUpdates:
  command = ".mu"
  help = gib.ircstr("´Isearchterm´N | Searches manga on Baka-Updates.")
  shelp = gib.ircstr("´Iquery´N")

  google = None

  class HTMLStripper(html.parser.HTMLParser):
    class HTMLP(html.parser.HTMLParser):
      _data = ""
      def handle_starttag(self, tag, attrs):
        if tag == "br":
          if self._data[-1] != " ":
            self._data += " "
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

  def __init__(self):
    self.google = google.Google()

  def main(self, args, env = {}):
    if not len(args): return ''
    link = self.google.search(args + ['site:mangaupdates.com/series.html'])
    if len(link):
      page = self.google.open_page(link[0])
      page = b''.join(page.readlines()).decode('utf-8', 'ignore')
      html = lxml.html.document_fromstring(page)
      rating = self.get_rating(html)
      volumes = self.get_volumes(html)
      description = self.get_description(html)
      name = [str(link[0])]
      if not volumes in (None, ""): name.append(gib.ircstr('´C6´B´B' + volumes + '´N'))
      if not rating in (None, ""): name.append(gib.ircstr('´C7´B´B' + rating + '´N'))
      if not link[1] in (None, ""): name.append(gib.ircstr('´B' + link[1].replace('Baka-Updates Manga - ', '') + '´N'))
      name = ' :: '.join(name)
      if not description in (None, ""): name = [name, description]
      return name
    else: return gib.ircstr("'´I{0}´N' did not return anything.").format(' '.join(args))

  def get_description(self, html):
    if not html: return ''
    description = html.xpath('//div[@class="sCat"]/b[text()="Description"]/../following-sibling::div[@class="sContent"][1]')
    if len(description) > 0:
      description = self.htmlstripper.strip(lxml.html.tostring(description[0]).decode('utf8').strip(' \n\t\r')).replace('\n', '').replace('\r', '')
      #description = description[0].text_content().strip(' \n\t\r')
      return description if len(description) < 455 else (description[:450] + ' ...')
    else: return ''

  def get_rating(self, html):
    if not html: return ''
    rating = html.xpath('//div[@class="sCat"]/b[text()="User Rating"]/../following-sibling::div[@class="sContent"][1]')
    if len(rating) > 0:
      rating = rating[0].text_content().split(' votes)')[0].split('\r')[0].replace('Average: ', '').replace(' / 10.0 (', ' - ') + ' votes'
      return rating
    else: return ''

  def get_volumes(self, html):
    if not html: return ''
    volumes = html.xpath('//div[@class="sCat"]/b[text()="Status in Country of Origin"]/../following-sibling::div[@class="sContent"][1]')
    if len(volumes) > 0:
      volumes = volumes[0].text_content().strip(' \n\t\r')
      return volumes
    else: return ''

