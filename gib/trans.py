import gib
import re
import romkan
import mstranslator

name = "Translator"

class Translator:
  command = ".trans"
  help = gib.ircstr("´Igarbagestring´N [´B.to´N ´Ilangcode´N] [´B.from´N ´Ilangcode´N] [´B.codes´N] | Translates the garbage string of random characters that someone posted before.")
  shelp = gib.ircstr("´Itext´N [´B.to´N ´Ilng´N] [´B.from´N ´Ilgn´N]")

  translator = None
  lang_dict = {'ca':'Catalan', 'ca-es':'Catalan (Spain)', 'da':'Danish', 'da-dk':'Danish (Denmark)', 'de':'German', 'de-de':'German (Germany)', 'en':'English', 'en-au':'English (Australia)', 'en-ca':'English (Canada)', 'en-gb':'English (United Kingdom)', 'en-in':'English (India)', 'en-us':'English (United States)', 'es':'Spanish', 'es-es':'Spanish (Spain)', 'es-mx':'Spanish (Mexico)', 'fi':'Finnish', 'fi-fi':'Finnish (Finland)', 'fr':'French', 'fr-ca':'French (Canada)', 'fr-fr':'French (France)', 'it':'Italian', 'it-it':'Italian (Italy)', 'ja':'Japanese', 'ja-jp':'Japanese (Japan)', 'ko':'Korean', 'ko-kr':'Korean (Korea)', 'nb-no':'Norwegian Bokmål (Norway)', 'nl':'Dutch', 'nl-nl':'Dutch (Netherlands)', 'no':'Norwegian', 'pl':'Polish', 'pl-pl':'Polish (Poland)', 'pt':'Portuguese', 'pt-br':'Portuguese (Brazil)', 'pt-pt':'Portuguese (Portugal)', 'ru':'Russian', 'ru-ru':'Russian (Russia)', 'sv':'Swedish', 'sv-se':'Swedish (Sweden)', 'zh-chs':'Chinese (Simplified)', 'zh-cht':'Chinese (Traditional)', 'zh-cn':'Chinese (S)', 'zh-hk':'Chinese (Hong Kong)', 'zh-tw':'Chinese (T)'}
  lang_str_long = 'ca, ca-es, da, da-dk, de, de-de, en, en-au, en-ca, en-gb, en-in, en-us, es, es-es, es-mx, fi, fi-fi, fr, fr-ca, fr-fr, it, it-it, ja, ja-jp, ko, ko-kr, nb-no, nl, nl-nl, no, pl, pl-pl, pt, pt-br, pt-pt, ru, ru-ru, sv, sv-se, zh-chs, zh-cht, zh-cn, zh-hk, zh-tw'
  lang_str = 'ca da de en es fi fr it ja ko nb-no nl no pl pt ru sv zh-chs zh-cht'

  def __init__(self):
    self.translator = mstranslator.Translator('NAME', 'APIKEY')
    return

  def main(self, args, env = {}):
    if not len(args): return ''
    if args[0] == '.codes': return gib.ircstr("Possible language codes: ´I{0}´N. See also ´Bhttp://msdn.microsoft.com/en-us/library/hh456380.aspx´N").format(self.lang_str_long)
    i = 0
    to_trans = []
    to_lang = 'en'
    from_lang = ''
    while i < len(args):
      if args[i] == '.to':
        if i+1 < len(args): to_lang = args[i+1]
        i += 1
      elif args[i] == '.from':
        if i+1 < len(args): from_lang = args[i+1]
        i += 1
      else:
        to_trans.append(args[i])
      i += 1
    to_trans = ' '.join(to_trans)
    to_lang = to_lang.lower()
    from_lang = from_lang.lower()
    if not to_lang in self.lang_dict:
      return gib.ircstr("Language code '´I{0}´N' not found. Possible: ´I{1}´N. (\"´B.trans .codes´N\" for a full list)").format(to_lang, self.lang_str)
    if len(from_lang) and not from_lang in self.lang_dict:
      return gib.ircstr("Language code '´I{0}´N' not found. Possible: ´I{1}´N. (\"´B.trans .codes´N\" for a full list)").format(from_lang, self.lang_str)
    if from_lang.startswith('ja') and re.match('[a-zA-Z]+', to_trans): to_trans = romkan.to_hiragana(to_trans)
    trans = self.translator.translate(to_trans, lang_from=from_lang, lang_to=to_lang) if len(from_lang) else self.translator.translate(' '.join(args), lang_to=to_lang)
    lang = self.lang_dict[from_lang] if len(from_lang) else self.lang_dict[self.translator.detect_lang(to_trans)]
    if not len(lang): lang = 'n/a'
    return gib.ircstr("´B{0}´N | ´I{1}´N").format(trans, lang)

