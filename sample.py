#!/usr/bin/env python

import sys,re,random,os.path
from commons import *

USE_CUSTOM_SAMPLE_SIZE = True
CUSTOM_SAMPLE_SIZE = 20

script_dir = os.path.realpath(os.path.dirname(__file__)) + '/'

projects = sys.argv[1:] if len(sys.argv) > 1 else benchmarks

pattern = re.compile(r'\[\d+\].*?isHighPriority: true.*')
output_file_template = 'results/%s/sample_indices'

population_sizes = {}
sample_sizes = {}

for project in projects:
   input_file = ''.join([script_dir, af_result_file_name(project)])
   population_sizes[project] = 0
   with open(input_file, 'r') as f:
      for line in f:
         if pattern.match(line):
            population_sizes[project] += 1

if USE_CUSTOM_SAMPLE_SIZE:
   for project in projects:
      sample_sizes[project] = min(CUSTOM_SAMPLE_SIZE, population_sizes[project])
else:
   ss = min(population_sizes.itervalues())
   for project in projects:
      sample_sizes[project] = ss

for project in projects:
   output_file = ''.join([script_dir, output_file_template % project])
   with open(output_file, 'w') as f:
      f.writelines( ( '%d\n\n' % (i+1) for i in sorted(random.sample(xrange(population_sizes[project]), sample_sizes[project])) ) )
