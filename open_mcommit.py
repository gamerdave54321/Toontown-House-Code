'''
Special "mini commit" prototype for Unior's slow connection
Made by Unior for Unior
If Unior's had asked you to push his mini commit, just run this file and push :)
'''

import zlib, cPickle

name = raw_input('Mini Commit name (not .extension): ')
commit = open(name+'.minicommit', 'rb').read()
fromZlib = zlib.decompress(commit)
fromPickle = cPickle.loads(fromZlib)
debugExtraRoot = ''
for f in fromPickle:
    f = zlib.decompress(f)
    lines = f.split('\n')
    fileName = lines[0].split('#')[1]
    nf = open(debugExtraRoot + fileName, 'w')
    nf.write(f)
    nf.close()
    
