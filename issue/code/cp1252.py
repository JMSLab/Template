import sys

sys.stdout.buffer.write('café “quoted text”\n'.encode('cp1252'))
open('output/cp1252.txt', 'w').close()
