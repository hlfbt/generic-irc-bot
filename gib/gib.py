## This module contains some IRC helper-functions
import re

I = chr(29)
B = chr(2)
U = chr(31)
R = chr(22)
N = chr(15)
C = chr(3)

Cre = re.compile('´C[0-9]{1,2}(,[0-9]{1,2})?')
Ore = re.compile('´(I|B|U|R|N)')

ircmode = True  # Set this to False if you want to use the modules outside of an IRC context

def ircstr(str):
  if ircmode:
    return str.replace('´I', I).replace('´B', B).replace('´U', U).replace('´R', R).replace('´N', N).replace('´C', C)
  else:
    return Ore.sub('', Cre.sub('', str))

