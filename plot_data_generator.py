#!/usr/bin/env python

import sys,json,operator,os.path
from collections import namedtuple
from commons import *

script_dir = os.path.realpath(os.path.dirname(__file__)) + '/'

LABEL_BY_PROJECT, LABEL_BY_COUNT = range(0, 2)

ASSERT_THRESHOLD = 40
METHOD_THRESHOLD = 50

plot = LABEL_BY_PROJECT
#plot = LABEL_BY_COUNT
HEAT_MAP = False

Point = namedtuple('Point', ['x', 'y'])

data_format = '%-6d %-6d %-6d'
header = '%-6s %-6s %-6s' % ('x', 'y', 'z')

asserts_methods_data = []

projects = sys.argv[1:] if len(sys.argv) > 1 else benchmarks

def print_heat_map_table(data):
   SEP=','
   XSCALE=10
   YSCALE=20
   xmax=max([p.x for p in data.iterkeys()])
   ymax=max([p.y for p in data.iterkeys()])
   xsize = xmax/XSCALE+1
   ysize = ymax/YSCALE+1
   #header_row = []
   #for i in xrange(xsize):
   #   if XSCALE > 1:
   #      header_row.append(('%d-%d' % (i * XSCALE, i * XSCALE + XSCALE -1)))
   #   else:
   #      header_row.append(i)
   #matrix = [header_row]
   matrix = []
   for i in xrange(ysize):
      matrix.append(xsize*[0])
   for k, v in data.iteritems():
      matrix[ysize-1-k.y/YSCALE][k.x/XSCALE] += v
   print '\n'.join([SEP.join(str(x) if x > 0 else '' for x in row) for row in matrix])

data = []
for project in projects:
   with open(''.join([script_dir, 'results/', project, '/data_af']), 'r') as data_af_file:
      data_af = json.load(data_af_file)
      data.append(data_af['data'])

if plot == LABEL_BY_PROJECT:
   data = sorted(data, key=lambda datum: len(datum), reverse=True)
   data_of_interest = 0
   total_data = 0
   for i in xrange(len(data)):
      scatter = [ data_format % (datum['asserts'], datum['methods'], i) for datum in data[i]]
      asserts_methods_data.append( '\n'.join(scatter) )
      data_of_interest += len([None for datum in data[i] if datum['asserts'] < ASSERT_THRESHOLD and datum['methods'] < METHOD_THRESHOLD])
      total_data += len(scatter)
   print '%', data_of_interest/float(total_data)*100, '% of clone sets has asserts no more than', ASSERT_THRESHOLD, 'and methods no more than', METHOD_THRESHOLD
elif plot == LABEL_BY_COUNT:
   data_ = {}
   for i in data:
      for datum in i:
         point = Point(x=datum['asserts'], y=datum['methods'])
         if point not in data_:
            data_[point] = 1
         else:
            data_[point] += 1
   if HEAT_MAP:
      print_heat_map_table(data_)
      sys.exit(0)
   else:
      for k, v in sorted(data_.iteritems(), key=operator.itemgetter(1)):
         asserts_methods_data.append( data_format % ( k.x, k.y, v ) )

print '\n'.join([ header , '\n'.join(asserts_methods_data) ])
