import gib
import socket
from urllib.request import urlopen, Request
import google

name = "RDNS"

class RDNS:
  command = ".rdns"
  help = gib.ircstr("´Iipaddress´N | Returns the reverse DNS entry for the IP.")
  shelp = gib.ircstr("´Iip´N")

  google = None

  def __init__(self):
    self.google = google.Google()

  def main(self, args, env = {}):
    if not len(args): return ''
    host = socket.gethostbyaddr(args[0])[0]
    if host.find('://') == -1: host = "http://{0}/".format(host)
    page = urlopen(Request(host, None, {'User-Agent':"Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.2 Safari/537.36"}))
    try: title = self.google.get_title(page)
    except: title = gib.ircstr("´ITimeout´N")
    return gib.ircstr("{0} | ´B{1}´N{2}").format(args[0], host, (" - " + title) if len(title) else '')

