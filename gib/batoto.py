import gib
import google
import lxml.html
import zlib

name = "Batoto"

class Batoto:
  command = ".btt"
  help = gib.ircstr("´Isearchterm´N | Searches on Bato.to.")
  shelp = gib.ircstr("´Iquery´N")

  google = None

  def __init__(self):
    self.google = google.Google()

  def main(self, args, env = {}):
    if not len(args): return ''
    link = self.google.search(args + ['site:bato.to'])
    if len(link):
      rating = self.get_rating(link[0])
      name = [str(link[0])]
      if len(rating): name.append(gib.ircstr('´C7´B´B' + rating + '´N'))
      if len(link[1]): name.append(gib.ircstr('´B' + link[1].split('- Scanlations ')[0].split(' - Comic ')[0] + '´N'))
      name = ' :: '.join(name)
      return name
    else: return gib.ircstr("'´I{0}´N' did not return anything.").format(' '.join(args))

  def get_rating(self, url):
    if not len(url): return ''
    page = self.google.open_page(url)
    page = b''.join(page.readlines())
    try: page = page.decode('utf8')
    except UnicodeDecodeError:
      try: page = zlib.decompress(page, 15+32)
      except: return ''
    html = lxml.html.document_fromstring(page)
    rating = html.xpath('//div[contains(@class, "rating")]')
    if len(rating) > 0:
      rating = rating[0].text_content().split('(')[1].split('votes')[0] + ' votes'
      return rating
    else: return ''

