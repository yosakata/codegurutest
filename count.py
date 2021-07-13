#!/bin/python
import re
import sys
import operator

worddict = {}

f = open(sys.argv[1], 'r')

for line in f:
	line = line.replace("\r", "")
	line = line.replace("\n", "")

	if line not in worddict:
		worddict[line] = 1
	else:
		worddict[line] += 1

worddict_view = [ (v,k) for k,v in worddict.iteritems() ]
worddict_view.sort(reverse=True)

for v,k in worddict_view:
    print "%s\t%d" % (k,v)
