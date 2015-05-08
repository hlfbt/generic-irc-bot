import gib
import wolframalpha
import socket

name = "WAlpha"

class WAlpha:
  command = ".wa"
  help = gib.ircstr("´Iquery´N | Queries WolframAlpha.")
  shelp = gib.ircstr("´Iquery´N")

  client = None

  def __init__(self):
    self.client = wolframalpha.Client("KEY")

  def main(self, args, env = {}):
    if not len(args): return ''
    num = 10 if 'nick' in env and env['nick'].GetHost() == 'Potatoe.Developer.AnimeBytes' else 5
    r = self.query(' '.join(args), num)
    if len(r):
      pods = [gib.ircstr('´C7´B') + r.pop(0)[1] + gib.ircstr('´N :: ')]
      for s in r:
        if len(pods[-1]) + len(s[0]) + len(s[1]) >= 400: pods.append('')
        pods[-1] += gib.ircstr('[ ´C10') + s[0] + gib.ircstr(': ´N') + s[1] + ' ]'
#        if len(pods[-1]) >= 400: pods.append('')
      pods = list(filter(None, pods))
#      if 'nick' in env and env['nick'].GetHost() != 'Potatoe.Developer.AnimeBytes': pods = pods[0:1]
      pods = pods[0:1]
      return pods
    else:
      return 'No results!'

  def query(self, query, num = 5):
    global ret
    res = self.client.query(query)
    ret = []
    for p in res.pods:
      if p.text: ret.append([p.title, ' || '.join([self.clean_wa(c.text) for c in p if c.text])])
      if len(ret) > num: break
#    for r in res.results:
#      if len(ret) == 4: break
#      ret.append(gib.B + r.text + gib.N)
#    if len(ret) < 4:
#      for p in res.pods:
#        if len(ret) == 4: break
#        ret.append(gib.I + p.text + gib.N)
    return ret

  def clean_wa(self, toclean):
    return ' '.join(toclean.replace('\n  | ', ' ').replace('\n', ' - ').split()) \
           .replace(' )', ')').replace('( ', '(').rstrip(' | ').replace(' | ', ', ') \
           .replace(' ~~ ', ' ≒ ').replace('~~ ', '~').replace('>=', '≥').replace('<=', '≤') \
           .replace('=>', '⇒').replace(r'\:2224', '∤').replace('(for all)', ' ∀ ') \
           .replace(' element ', ' ∈ ').replace('(not element)', ' ∉ ') \
           .replace(r'\:2115', 'ℕ').replace(r'\:2124', 'ℤ').replace(r'\:211a', 'ℚ').replace(r'\:211d', 'ℝ').replace(r'\:2102', 'ℂ') \
           .strip()

