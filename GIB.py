import znc

import sys
import importlib
import os
import socket
import threading
import traceback
import time

import re
import random

filepath = os.path.dirname(os.path.realpath(__file__))
# Waiting is annoying!
socket.setdefaulttimeout(15)

# Logging
try: del sys.modules['gib']
except KeyError: pass
try: del sys.modules['logger']
except KeyError: pass
import gib
import logger
L = logger.Logger()
L.setloglevel(L.INFO)
L.setlogpath(filepath + '/GIB.log')
L.log(L.INFO, 'STARTED')

modules = {'google', 'anidb', 'ann', 'vndb', 'vgmdb', 'mal', 'trans', 'lastfm', 'wa', 'mangaupdates', 'batoto'}
modules = dict.fromkeys(modules, '')
Modules = modules
commands = {}
help = gib.ircstr("´B.help´N [´Icmd´N]")
# So that we can just import them by name of the script
sys.path.append(filepath + '/gib/')
for mod in modules:
  try: del sys.modules[mod]
  except KeyError: pass
  modules[mod] = importlib.import_module(mod)
  try:
    Modules[mod] = getattr(modules[mod], modules[mod].name)()
    help += ', ' + gib.B + Modules[mod].command + gib.N + ' ' + Modules[mod].shelp
    commands[Modules[mod].command] = mod
  except Exception as e:
    L.log(L.ERROR, str(e))


class GLaDOS(znc.Module):
  description = "GIB"  # Generic IRC Bot

  # Users that are allowed to perform actions and are not bound to cooldown
  user_whitelist = ["Potatoe"]
  channel_whitelist = ["#potatoe"]
  use_channel_whitelist = False
  use_user_whitelist = False
  channel_blacklist = ["#linux"]
  use_channel_blacklist = True
  cooldown = [0,0,0,0,0]
  cooluntil = 0

  abure = re.compile('([^\\.]+)\\.[a-zA-Z]+\\.AnimeBytes')
  colorre = re.compile('\x03[0-9]{1,2}(,[0-9]{1,2})?')

  def OnLoad(self, args, message):
    global L
    os.chdir(self.GetSavePath())
    try:
      for mod in modules:
        Modules[mod].__init__()
    except: pass
    # For some dumb reason ZNC likes to reload modules without calling OnLoad every time just randomly
    # So it may forget the logpath, or even forgets some loaded python modules sometimes
    # Just in case, I always specify `self.GetSavePath() + "/modules.log"` anyway every time I log something
    L.setlogpath(self.GetSavePath() + "/modules.log")
    L.log(L.INFO, 'GIB started!')
    return znc.CONTINUE


  # For some reason this isn't always called when an invite happens. Listening to the raw commands for an "INVITE" command is safer.
  def OnInvite(self, nick, channel):  # channel is znc.CString! NOT znc.CChan
    chan = channel.s
    self.put_msg('potatoe', chan)
    global L
    if self.use_channel_blacklist and chan in self.channel_blacklist:
      return znc.CONTINUE
    self.join_channel(chan)
    L.log(L.INFO, 'Invited and joined ' + chan)
    return znc.CONTINUE

  def OnRaw(self, line):
    line = line.s.split(' ')
    if line[1] == "INVITE" \
    and line[2].lower() == self.GetNetwork().GetNick().lower() \
    and len(line[3][1:]) > 0:
      self.join_channel(line[3][1:])
    return znc.CONTINUE


  def OnChanMsg(self, nick, channel, message):
    global L, modules, Modules, commands, help

    # Get some basic stuff
    net = self.GetNetwork()
    me = net.GetNick()
    msg = message.s
    msglst = msg.split()
    nik = nick.GetNick()
    try:  # It's either a znc.CChan or a znc.CNick, everything else we just don't accept
      chan = channel.GetName() if type(channel) is znc.CChan else channel.GetNick()
    except Exception:
      return znc.CONTINUE

    if nik == "Satsuki":
      return znc.CONTINUE
    if (self.use_channel_blacklist and chan in self.channel_blacklist) \
    or (self.use_channel_whitelist and not chan in self.channel_whitelist):
      return znc.CONTINUE

    # Some anti-flooding procedures. Not the best, but it works vOv
    if msglst[0] in commands:
      #if not (nik in self.user_whitelist
      permstr = channel.FindNick(nik).GetPermStr() if type(channel) is znc.CChan else ''
      if not (self.abure.sub('\\1', nick.GetHost()) in self.user_whitelist or nik in self.user_whitelist) \
      and all(permstr.find(p) < 0 for p in ['~', '&', '@', '%']):
        if use_user_whitelist:
          return znc.CONTINUE
        currenttime = time.mktime(time.gmtime())
        if currenttime-self.cooldown[0] < 90:
          return znc.CONTINUE
        if currenttime-self.cooldown[-1] < 5:
          return znc.CONTINUE
        if currenttime <= self.cooluntil:
          return znc.CONTINUE
        if all(t >= currenttime-45 for t in self.cooldown):
          self.cooluntil = currenttime + 300
          self.put_msg(chan, 'Yamete! >///<')
          L.log(L.INFO, chan + " flooded by " + nik + ", msg: " + msg, self.GetSavePath() + "/modules.log")
        self.cooldown.append(currenttime)
        if len(self.cooldown) > 5:
          self.cooldown.pop(0)
        if self.cooluntil > currenttime:
          return znc.CONTINUE
        if currenttime-self.cooldown[0] < 90:
          self.put_msg(chan, 'Yamete! >///<')
        if currenttime-self.cooldown[-1] < 5:
          self.put_msg(chan, 'Yamete! >///<')

    if msglst[0] == '.help' \
    or (msglst[0].lower() in [me.lower(), 'sawako', 'sadako'] and msglst[1].lower() == 'help') \
    or (msglst[0].lower() in ['hi', 'hello', 'yo', 'hey'] and msglst[1].lower() in [me.lower(), 'sawako', 'sadako']):
      if msglst[0].lower() in ['hi', 'hello', 'yo', 'hey']:
        greeting = random.choice(['Hi', 'Hello', '今日は', 'Konnichiwa'])
        self.put_msg(channel.GetName(), greeting + ' ' + nik + '!')
      if msglst[0] == '.help':
        args = msglst[1:]
      else:
        args = msglst[2:]
      if not len(args):
        self.put_notice(nik, 'Possible commands: ' + help)
        self.put_notice(nik, gib.ircstr('For more details: ´B/msg ' + me + ' help´N'))
        return znc.CONTINUE
      if args[0] in commands:
        mod = Modules[commands[args[0]]]
        self.put_notice(nik, gib.B + mod.command + gib.N + ' ' + mod.help)
        return znc.CONTINUE

    if msglst[0] in commands:
      cmd = msglst[0]
      mod = commands[cmd]
      mod = Modules[mod]
      args = msglst[1:]
      now = time.time()
      ret = ''
      chan = channel.GetName()
      chan = (chan[:12] + (chan[12:] and '..')).ljust(14)
      L.log(L.INFO, chan + " call: " + cmd + ", args: " + str(args), self.GetSavePath() + "/modules.log")
      try:
        env = {'nick': nick, 'channel': channel, 'self': self}
        ret = mod.main(args, env)
        if len(ret):
          if 'c' in str(channel.GetModeString()):
            ret = self.colorre.sub('', ret)
          self.put_msg(channel, ret)
      except Exception as e:
        L.log(L.ERROR, chan + " error: " + str(e), self.GetSavePath() + "/modules.log")
        traceback.print_exc(file = open(self.GetSavePath() + "/traceback.log", "a"))
      L.log(L.INFO, chan + " finish: " + cmd + ", (" + str(int((time.time() - now) * 1000)) + "ms)", self.GetSavePath() + "/modules.log")
      return znc.CONTINUE

    return znc.CONTINUE


  # There're barely any actual commands yet. Calling OnChanMsg inside this is more of an easy hack to allow for command usage via pm as well.
  def OnPrivMsg(self, nick, message):
    global modules, Modules
    msg = message.s
    msglst = msg.split()
    ## Uncomment the following if you comment out or remove the OnChanMsg hack:
    #if msglst[0] in ['.help', 'hello', 'help']:
    #  for mod in modules:
    #    Mod = Modules[mod]
    #    self.put_msg(nick, gib.B + Mod.command + gib.N + ' ' + Mod.help)
    if 'Potatoe.Developer.AnimeBytes' == nick.GetHost():
      if msglst[0] == 'loadmod' or msglst[0] == 'reloadmod':
        if self.reloadmod(msglst[1]):
          self.put_msg(nick, "Mod " + msglst[1] + " succesfully (re)loaded!")
        else:
          self.put_msg(nick, "Error (re)loading mod " + msglst[1] + ".")
        return znc.CONTINUE
      if msglst[0] == 'unloadmod':
        if self.unloadmod(msglst[1]):
          self.put_msg(nick, "Mod " + msglst[1] + " succesfully unloaded!")
        else:
          self.put_msg(nick, "Mod " + msglst[1] + " is not loaded.")
        return znc.CONTINUE
    self.OnChanMsg(nick, nick, message)
    return znc.CONTINUE


  def put_com(self, com, target, msg):
    if len(msg) < 1 \
    or len(com) < 1 \
    or type(com) is not str:
      return
    if not (type(target) is str or type(msg) is dict):
      if type(target) is znc.CChan:
        target = target.GetName()
      elif type(target) is znc.CNick:
        target = target.GetNick()
      elif type(target) is znc.CString:
        target = target.s
      else:
        return
    if type(msg) is str:
      self.PutIRC("{0} {1} :{2}".format(com, target, msg))
    elif type(msg) is list:
      for m in msg:
        self.PutIRC("{0} {1} :{2}".format(com, target, m))
    elif type(msg) is dict:
      for t in msg:
        if type(msg[t]) is str:
          self.PutIRC("{0} {1} :{2}".format(com, t, msg[t]))
        elif type(msg[t]) is list:
          for m in msg[t]:
            self.PutIRC("{0} {1} :{2}".format(com, t, m))
    return

  def put_msg(self, target, msg):
    self.put_com("PRIVMSG", target, msg)

  def put_notice(self, target, msg):
    self.put_com("NOTICE", target, msg)

  def join_channel(self, channel):
    if type(channel) != str:
      channel = channel.GetName()
    self.PutIRC("JOIN " + channel)
    return


  def unloadmod(self, mod):
    global L, modules, Modules
    try:
      if not mod in sys.modules and not mod in modules:
        return False
      try:
        del sys.modules[mod]
        del modules[mod]
      except KeyError:
        pass
      self.rebuildindices()
      L.log(L.WARN, "Module '" + mod + "' was unloaded.", self.GetSavePath() + "/modules.log")
      return True
    except Exception as e:
      L.log(L.ERROR, "Exception unloading " + mod + " (" + modules[mod].name + "): " + str(e), self.GetSavePath() + "/modules.log")
      traceback.print_exc(file = open(self.GetSavePath() + "/traceback.log", "a"))
      self.rebuildindices()
      return True

  def reloadmod(self, mod):
    global L, modules, Modules
    try:
      r = True if mod in sys.modules else False
      try:
        del sys.modules[mod]
      except KeyError:
        pass
      modules[mod] = importlib.import_module(mod)
      try:
        Modules[mod] = getattr(modules[mod], modules[mod].name)()
      except Exception as e:
        L.log(L.ERROR, "Exception instanciating " + modules[mod].name + ": " + str(e), self.GetSavePath() + "/modules.log")
        traceback.print_exc(file = open(self.GetSavePath() + "/traceback.log", "a"))
        return False
      self.rebuildindices()
      L.log(L.WARN, "Module '" + mod + "' was " + ("re" if r else '') + "loaded.", self.GetSavePath() + "/modules.log")
      return True
    except Exception as e:
      L.log(L.ERROR, "Catastrophical error at " + mod + ": " + str(e), self.GetSavePath() + "/modules.log")
      traceback.print_exc(file = open(self.GetSavePath() + "/traceback.log", "a"))
      return False

## This should be done by rebuildindices now
#  def rebuildhelp(self):
#    global help
#    help = ".help [<cmd>]"
#    for mod in modules:
#      try: help += ", " + modules[mod].shelp
#      except: pass
#    return

  def rebuildindices(self):
    global L, modules, Modules, commands, help
    commands = {}
    help = gib.ircstr("´B.help´N [´Icmd´N]")
    for mod in modules:
      try:
        help += ', ' + gib.B + Modules[mod].command + gib.N + ' ' + Modules[mod].shelp
        commands[Modules[mod].command] = mod
      except Exception as e:
        L.log(L.ERROR, "Exception rebuilding indices for " + mod + ": " + str(e), self.GetSavePath() + "/modules.log")
        traceback.print_exc(file = open(self.GetSavePath() + "/traceback.log", "a"))
        pass

