from panda3d.core import *
import string
import types
try:
    language = getConfigExpress().GetString('language', 'english')
    checkLanguage = getConfigExpress().GetBool('check-language', 0)
except:
    language = simbase.config.GetString('language', 'english')
    checkLanguage = simbase.config.GetBool('check-language', 0)

def getLanguage():
    return language


print 'TTLocalizer: Running in language: %s' % language
if language == 'english':
    _languageModule = 'toontown.toonbase.TTLocalizer' + language.capitalize()
else:
    checkLanguage = 1
    _languageModule = 'toontown.toonbase.TTLocalizer_' + language

m = __import__(_languageModule, {}, {}, ['toontown.toonbase'])
globals().update(m.__dict__)
    
if checkLanguage:
    l = {}
    g = {}
    englishModule = __import__('toontown.toonbase.TTLocalizerEnglish', g, l, ['toontown.toonbase'])
    foreignModule = __import__(_languageModule, g, l, ['toontown.toonbase'])
    for key, val in englishModule.__dict__.items():
        if not foreignModule.__dict__.has_key(key):
            print 'WARNING: Foreign module: %s missing key: %s' % (_languageModule, key)
            locals()[key] = val
        elif isinstance(val, types.DictType):
            fval = foreignModule.__dict__.get(key)
            for dkey, dval in val.items():
                if not fval.has_key(dkey):
                    print 'WARNING: Foreign module: %s missing dict key: %s.%s' % (_languageModule, key, dkey)
                    fval[dkey] = dval

            for dkey in fval.keys():
                if not val.has_key(dkey):
                    print 'WARNING: Foreign module: %s extra dict key: %s.%s' % (_languageModule, key, dkey)

import LocalizerAgent
LocalizerAgent.install(getLanguage())
