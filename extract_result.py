#!/usr/bin/env python

from __future__ import print_function
import sys,re,os.path,subprocess
from commons import *

DEBUG = False

FOUND_CLONE, FOUND_METHOD, NULL = range(3)
FOUND_SIGNATURE, FOUND_BODY, NULL = range(3)

script_dir = os.path.realpath(os.path.dirname(__file__)) + '/'

file_extension = '.java'

set_pattern = re.compile(r'\[(\d+)\] Set.*')
method_pattern = re.compile(r'Methods \((\d+)\).*')
signature_pattern = re.compile(r'\s+\<(?P<full_class_name>.+?): (?P<return_type>.+?) (?P<method_name>.+?)\((?P<parameters>.*?)\)\>')
rel_clone_sets_pattern = re.compile(r'Relevant Assertion clone sets \((\d+)\).*')

def format_paramter_regex(parameter):
   return parameter if '\[\]' not in parameter else parameter.replace('\[\]', '(\[\]|\.\.\.)')

def format_type_regex(type):
   return ''.join(['(\w+\s+)*', re.escape(re.split('\.|\$', type.strip())[-1]), '(<.*?>)?'])

def find_file_path(project, full_class_name, file_path_cache):
   file_path = ''
   if full_class_name in file_path_cache:
      file_path = file_path_cache[full_class_name]
   else:
      file_name = ''.join(['/'.join(full_class_name.split('.')).split('$')[0], file_extension])
      path_dir = ''.join([script_dir, project_dir, dirs[project]])
      if not os.path.exists(path_dir):
         print ('Looking for', path_dir, ', but it does not exist!', file=sys.stderr)
         sys.exit(1)
      file_paths = [line for line in subprocess.check_output("find %s -type f -wholename '*/%s' 2>/dev/null" % (path_dir, file_name), shell=True).splitlines()]
      if not file_paths:
         print ('Looking for', file_name, 'in', path_dir, ', but it does not exist!', file=sys.stderr)
         sys.exit(1)
      file_path = file_path_cache[full_class_name] = file_paths[0]
   return file_path

def construct_method_body_patterns(return_type, method_name, parameters):
   parameter_str = parameters.strip()
   if parameter_str:
      parameter_template = r'\s*%s\s+\w+\s*'
      parameter_str = ','.join([ parameter_template % format_paramter_regex(format_type_regex(p)) for p in parameters.split(',') ])
   else:
      parameter_str = r'\s*'
   method_body_template = r'%s\s+%s\s*\(%s'
   escaped_return_type = format_type_regex(return_type)
   method_body_rough_pattern = re.compile(method_body_template % (escaped_return_type, method_name, '.*?'))
   method_body_precise_pattern = re.compile(method_body_template % (escaped_return_type, method_name, parameter_str + r'\)[\w\s,]*?{'))

   return (method_body_rough_pattern, method_body_precise_pattern)

def extract_method_body(project, full_class_name, return_type, method_name, parameters, file_path_cache):
   file_path = find_file_path(project, full_class_name, file_path_cache)

   (method_body_rough_pattern, method_body_precise_pattern) = construct_method_body_patterns(return_type, method_name, parameters)

   state = NULL
   body = []
   count = 0

   if DEBUG:
      print (file_path)
      print (method_body_rough_pattern.pattern)
      print (method_body_precise_pattern.pattern)
   with open(file_path, 'r') as f:
      for line in f:
         if state == NULL:
            if method_body_rough_pattern.search(line):
               state = FOUND_SIGNATURE
         if state == FOUND_SIGNATURE:
            body.append(line)
            count += line.count('{')
            if count:
               if method_body_precise_pattern.search(''.join(body)):
                  state = FOUND_BODY
               else:
                  del body[:]
                  count = 0
                  state = NULL
               continue
         if state == FOUND_BODY:
            body.append(line)
            count += line.count('{')
            count -= line.count('}')
            if not count:
               return ''.join(body)
   return ''

def extract_result(project, set_id):
   file_path_cache = {}
   input_file = ''.join([ script_dir, af_result_file_name(project) ])
   state = NULL
   method_count = -1
   method_bodies = []

   if not os.path.isfile(input_file):
      print ('Looking for', input_file, ', but it is not a file or does not exist!', file=sys.stderr)
      sys.exit(1)

   with open(input_file, 'r') as f:
      for line in f:
         if state == NULL:
            m = set_pattern.match(line)
            if m and m.group(1) == set_id:
               state = FOUND_CLONE
               method_bodies.append(line)
         elif state == FOUND_CLONE:
            m = method_pattern.match(line)
            if m:
               method_count = m.group(1)
               state = FOUND_METHOD
               method_bodies.append(line)
         elif state == FOUND_METHOD:
            m = signature_pattern.match(line)
            if m:
               method_bodies.append(''.join([line.strip(), '\n', extract_method_body(project=project, file_path_cache=file_path_cache, **m.groupdict())]))
            else:
               m = rel_clone_sets_pattern.match(line)
               if m:
                  return method_bodies
   return method_bodies

if __name__ == "__main__":
   print ('\n'.join(extract_result(sys.argv[1], sys.argv[2])))
