import gib
import google

name = "VGMDB"

class VGMDB:
  command = ".vgmdb"
  help = gib.ircstr("´Isearchterm´N | Searches on VGMDB.")
  shelp = gib.ircstr("´Iquery´N")

  google = None

  def __init__(self):
    self.google = google.Google()

  def main(self, args, env = {}):
    if not len(args): return ''
    link = self.google.search(args + ['site:vgmdb.net'])
    if len(link):
      if len(link[1]): return gib.ircstr("{0} - ´B{1}´N").format(link[0], link[1].replace(' - VGMdb', ''))
      else: return str(link[0])
    else: return "'´I{0}´N' did not return anything.".format(' '.join(args))

