import sys

sys.stdout.buffer.write('Log text: "quoted text"\n'.encode('utf-8'))
open('output/ascii.txt', 'w').close()
