import glob, os

def d(x):
    os.unlink(x)

for x in glob.glob('*/*/*.pyc.py'):
    d(x)
    
for x in glob.glob('*/*/*.pyc'):
    d(x)
    
for x in glob.glob('*/*.pyc'):
    d(x)
    