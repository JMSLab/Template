import sys

sys.stdout.buffer.write('Log text: “quoted text\n'.encode('utf-8'))
open('output/utf8_open.txt', 'w').close()
