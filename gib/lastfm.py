import gib
import re
import pylast
import datetime
import sqlite3
import os.path

name = "LastFM"

class LastFM:
  command = ".np"
  help = gib.ircstr("[´I.set´N/´I.unset´N] [´Iuser´N] | Returns last played song of ´Iuser´N (or own nick if none given). IRC nicks can be linked and unlinked with last.fm usernames respectively by calling ´I.np .set ´Blastfm-nick´N and ´I.np .unset´N. After this has been done, the linked IRC nick will not have to specify his last.fm username every time he calls ´I.np´N.")
  shelp = gib.ircstr("[´Iusr´N]")

  userre = re.compile('^[a-zA-Z0-9*_-]{,15}$')
  network = None
  sql = None
  sqlc = None

  def __init__(self):
    self.network = pylast.LastFMNetwork('ID', 'APIKEY')
    try:
      exists = os.path.isfile('lastfm.db')
      self.sql = sqlite3.connect('lastfm.db')
      self.sqlc = self.sql.cursor()
      if not exists:
        self.sqlc.execute('CREATE TABLE nicks (irc varchar(30), lastfm varchar(15));')
        self.sql.commit()
    except: pass

  def main(self, args, env = {}):
    user = ''
    if len(args) and args[0] and self.userre.match(args[0]): user = args[0]
    if not user and 'nick' in env:
      nick = env['nick'].GetNick()
      if len(args) == 2 and args[0] == '.set':
        if self.userre.match(args[1]): return self.set_nick(nick, args[1])
        else: return gib.ircstr('´I{0}´N is not a valid last.fm username.').format(args[1])
      if len(args) == 1 and args[0] == '.unset': return self.unset_nick(nick)
      user = self.get_nick(nick)
      if not user and self.userre.match(nick): user = nick
    if not user: return gib.ircstr("Invalid user ´I{0}´N").format(args[0] if len(args[0]) else env['nick'].GetNick())
    last_track = self.get_last_track(user)
    if 'error' in last_track:
      if last_track['error'] == 'not found': return gib.ircstr("´I{0}´N not found").format(user)
      elif last_track['error'] == 'no records': return gib.ircstr("´I{0}´N never played anything").format(user)
      else: return
    time = last_track['time']
    time = (self.pretty_date(time) + ' ') if time != 0 else ''
    tags = last_track['tags'][:3]
    tags = (gib.ircstr('´C7´B´B') + gib.ircstr('´N, ´C7´B´B').join(tags) + gib.N) if len(tags) else 'no tags'
    loved = gib.ircstr('´C4♥´N ') if last_track['loved'] else ''
    play = self.ordn(last_track['userplaycount'])
    album = (gib.ircstr('[´C13´B´B') + last_track['album'].title + gib.ircstr('´N] ')) if last_track['album'] else ''

    resp = gib.ircstr('´C11{0}´N {1} listening to "´C10´B{2}´N" {3}by ´C12´B{4}´N {5}{6}for the {7} time, {8} plays by {9} listeners. ({10})')
    resp = resp.format(user, 'was' if time != '' else 'is', last_track['track'], loved, last_track['artist'], album, time, play, last_track['globalplaycount'], last_track['listeners'], tags)
#    if type(time) == int and time == 0:
#      resp = gib.ircstr('´C11´I{0}´N is currently listening to "´C10´B{1}´N" by ´C12´I{2}´N{3} {4}for the {5} time, {6} global plays by {7} listeners. ({8})')
#      resp = resp.format(user, last_track['track'], last_track['artist'], album, loved, play, last_track['globalplaycount'], last_track['listeners'], tags)
#    else:
#      resp = gib.ircstr('´C11´I{0}´N was listening to "´C10´B{1}´N" by ´C12´I{2}´N{3} {4}about {5} for the {6} time, {7} global plays by {8} listeners. ({9})')
#      resp = resp.format(user, last_track['track'], last_track['artist'], album, loved, time, play, last_track['globalplaycount'], last_track['listeners'], tags)
    return resp

  def get_last_track(self, user):
    try: track = self.network.get_user(user).get_now_playing()
    except pylast.WSError: return {'error': 'not found'}
    now = True
    time = 0
    if not track:
      now = False
      try: track = self.network.get_user(user).get_recent_tracks()[0]
      except IndexError: return {'error': 'no records'}
      time = int(track.timestamp)
      track = track.track
    album = track.get_album()
    track.username = user
    userloved = track.get_userloved()
    userplays = int(track.get_userplaycount()) + (1 if now else 0)
    plays = int(track.get_playcount())
    listeners = int(track.get_listener_count())
    t1 = track._request('track.getInfo').getElementsByTagName('toptags')
    tags = []
    if len(t1):
      t1 = t1[0].getElementsByTagName('tag')
      for tag in t1:
        tags.append(tag.getElementsByTagName('name')[0].childNodes[0].nodeValue)
    t2 = track.artist._request('artist.getInfo').getElementsByTagName('tags')
    if len(t2):
      t2 = t2[0].getElementsByTagName('tag')
      for tag in t2:
        tags.append(tag.getElementsByTagName('name')[0].childNodes[0].nodeValue)
    return {'track':track.title, 'artist':track.artist, 'album':album, 'time':time, 'loved':userloved, 'userplaycount':userplays, 'globalplaycount':plays, 'listeners':listeners, 'tags':tags}

  def set_nick(self, ircnick, lfmnick):
    if self.sqlc:
      old = self.sqlc.execute('SELECT * FROM nicks WHERE irc = ?', (ircnick,)).fetchall()
      all = self.sqlc.execute('SELECT * FROM nicks WHERE lastfm = ?', (lfmnick,)).fetchall()
      if len(old):
        self.sqlc.execute('UPDATE nicks SET lastfm = ? WHERE irc = ?', (lfmnick, ircnick))
      else:
        self.sqlc.execute('INSERT INTO nicks VALUES (?, ?)', (ircnick, lfmnick))
      self.sql.commit()
      if not (ircnick, lfmnick) in all: all.append((ircnick, lfmnick))
      all = [e[0] for e in all]
      all = gib.ircstr('´N, ´I').join(all)
      return gib.ircstr('´I{0}´N is now linked with ´I{1}´N.').format(lfmnick, all)
    else:
      return ''

  def unset_nick(self, ircnick):
    if self.sqlc:
      irc = self.sqlc.execute('SELECT * FROM nicks WHERE irc = ?', (ircnick,)).fetchall()
      if len(irc):
        self.sqlc.execute('DELETE FROM nicks WHERE irc = ?', (ircnick,))
        self.sql.commit()
        return gib.ircstr('´I{0}´N is not linked with ´I{1}´N anymore.').format(ircnick, irc[0][1])
      else:
        return gib.ircstr('´I{0}´N is not currently linked with any last.fm username.')
    else:
      return ''

  def get_nick(self, ircnick):
    if self.sqlc:
      nick = self.sqlc.execute('SELECT lastfm FROM nicks WHERE irc = ?', (ircnick,)).fetchall()
      if len(nick): return nick[0][0]
      else: return None
    else: return None

  def ordn(self, n):
#    if n <= 10: return ['first', 'second', 'third', 'fourth', 'fifth', 'sixth', 'seventh', 'eighth', 'ninth', 'tenth'][n-1]
#    else: return str(n)+("th" if 4<=n%100<=20 else {1:"st",2:"nd",3:"rd"}.get(n%10, "th"))
    return str(n)+("th" if 4<=n%100<=20 else {1:"st",2:"nd",3:"rd"}.get(n%10, "th"))

  def pretty_date(self, time=False):
    """
    Get a datetime object or a int() Epoch timestamp and return a
    pretty string like 'an hour ago', 'yesterday', '3 months ago',
    'just now', etc
    """
    now = datetime.datetime.now()
    if type(time) is int:
      diff = now - datetime.datetime.fromtimestamp(time)
    elif isinstance(time, datetime.datetime):
      diff = now - time
    elif not time:
      diff = now - now
    second_diff = diff.seconds
    day_diff = diff.days
    if day_diff < 0:
      return ''
    if day_diff == 0:
      if second_diff < 10:
        return "just now"
      if second_diff < 60:
        return str(second_diff) + " seconds ago"
      if second_diff < 120:
        return "a minute ago"
      if second_diff < 3600:
        return str(int(second_diff / 60)) + " minutes ago"
      if second_diff < 7200:
        return "an hour ago"
      if second_diff < 86400:
        return str(int(second_diff / 3600)) + " hours ago"
    if day_diff == 1:
      return "yesterday"
    if day_diff < 7:
      return str(day_diff) + " days ago"
    if day_diff < 31:
      return str(int(day_diff / 7)) + " weeks ago"
    if day_diff < 365:
      return str(int(day_diff / 30)) + " months ago"
    return str(int(day_diff / 365)) + " years ago"

