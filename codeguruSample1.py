#!/usr/local/bin/python3

import csv

# Case 1
f = open('csvSample.csv')

# Case 2
mycard = '4980 1234 1234 1234'

# Case 3
fruites = ["Apple", "Banana", "Grapes"]
if len(fruites) > 0:
  print("there are fruites")

# Case 4
item = {"sakata", "090-1234-1234" }
if item == None:
  print("Dictionary is empty")


#try:
#  csvfile = csv.reader(f)
#except TypeError as e:
#  print('Catch TypeError:', e)
#finally:
#  f.close()

