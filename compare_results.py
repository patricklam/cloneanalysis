#!/usr/bin/env python

from __future__ import print_function
from extract_result import *
from bauhaus_filter import *
from commons import *
import json,Queue
from multiprocessing.pool import ThreadPool as Pool

queue = Queue.Queue()

pool = Pool()

script_dir = os.path.realpath(os.path.dirname(__file__)) + '/'

af_results = {}
bauhaus_results = {}
common_results = {}

def extract_bauhaus_method_lines(project, file_path, start, lines):
   return { 'file' : ''.join([script_dir, project_dir, dirs[project], '/', file_path]), 'start' : start, 'end' : start + lines }

def extract_bauhaus_result(project):
   bauhaus_results[project] = {}
   input_file = ''.join([ script_dir, bauhaus_dir, bauhaus_result_file_name(project) ])

   if not os.path.isfile(input_file):
      print ('Looking for', input_file, ', but it is not a file or does not exist!', file=sys.stderr)
      sys.exit(1)

   with open(input_file, 'r') as f:
      case_id = -1
      type = -1
      for line in f:
         m = cases_pattern.match(line)
         if m:
            case_id, type = m.groups()
            case_id = int(case_id)
            if case_id not in bauhaus_results[project]:
               bauhaus_results[project][case_id] = { 'type' : type, 'clones' : [] }
         else:
            m = clones_pattern.match(line)
            if m:
               bauhaus_results[project][case_id]['clones'].append(extract_bauhaus_method_lines(project, m.group(1), int(m.group(2)), int(m.group(3))))

def extract_af_method_lines(project, full_class_name, return_type, method_name, parameters, file_path_cache):
   file_path = find_file_path(project, full_class_name, file_path_cache)

   (method_body_rough_pattern, method_body_precise_pattern) = construct_method_body_patterns(return_type, method_name, parameters)

   state = NULL
   body = []
   count = 0

   result = { 'file' : file_path, 'start' : -1, 'end' : -1 }

   with open(file_path, 'r') as f:
      linenum = 0
      for line in f:
         linenum += 1
         if state == NULL:
            if method_body_rough_pattern.search(line):
               state = FOUND_SIGNATURE
         if state == FOUND_SIGNATURE:
            body.append(line)
            count += line.count('{')
            if count:
               if method_body_precise_pattern.search(''.join(body)):
                  state = FOUND_BODY
                  result['start'] = linenum - len(body) + 1
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
               result['end'] = linenum
               return result
   return result


set_pattern = re.compile(r'\[(\d+)\] Set.*?isHighPriority: true')
def extract_af_result(project):
   af_results[project] = {}
   file_path_cache = {}
   input_file = ''.join([ script_dir, af_result_file_name(project) ])
   state = NULL

   if not os.path.isfile(input_file):
      print ('Looking for', input_file, ', but it is not a file or does not exist!', file=sys.stderr)
      sys.exit(1)

   with open(input_file, 'r') as f:
      set_id = -1
      for line in f:
         if state == NULL:
            m = set_pattern.match(line)
            if m:
               set_id = int(m.group(1))
               if set_id not in af_results[project]:
                  af_results[project][set_id] = { 'clones' : [] }
               state = FOUND_CLONE
         elif state == FOUND_CLONE:
            m = method_pattern.match(line)
            if m:
               state = FOUND_METHOD
         elif state == FOUND_METHOD:
            m = signature_pattern.match(line)
            if m:
               af_results[project][set_id]['clones'].append(extract_af_method_lines(project=project, file_path_cache=file_path_cache, **m.groupdict()))
            elif rel_clone_sets_pattern.match(line):
               state = NULL

def compare(payload):
   for bc in payload['bauhaus']['clones']:
      for ac in payload['af']['clones']:
         if bc['file'] == ac['file'] and bc['start'] <= ac['end'] and ac['start'] <= bc['end']:
            queue.put(payload)
            return

result_src = ('bauhaus', 'af')

def format_common(project):
   dataset = []
   for i in common_results[project].itervalues():
      for j in i.itervalues():
         if j not in dataset:
            j['bauhaus'] = sorted(j['bauhaus'], key=lambda c: (c['type'], c['id']))
            j['af'] = sorted(j['af'], key=lambda c:  c['id'])
            dataset.append(j)
   common_results[project] = dataset

if __name__ == "__main__":
   projects = sys.argv[1:] if len(sys.argv) > 1 else benchmarks

   pool.map(extract_bauhaus_result, projects)
   projects = sorted(projects, key=lambda p:len(bauhaus_results[p].keys()), reverse=True)
   pool.map(extract_af_result, projects)
   for p in projects:
      common_results[p] = { 'af' : {}, 'bauhaus' : {} }
      for bk, bv in bauhaus_results[p].iteritems():
         for ak, av in af_results[p].iteritems():
            payload = { 'project' : p,
                  'bauhaus' : { 'id' : bk, 'clones' : bv['clones'], 'type' : bv['type'] },
                  'af' : { 'id' : ak, 'clones' : av['clones'] }
            }
            pool.apply_async(compare, args=(payload,))
   pool.close()
   pool.join()

   while not queue.empty():
      result = queue.get()
      c = 0
      for r in result_src:
         if result[r]['id'] in common_results[result['project']][r]:
            common_results[result['project']][r][result[r]['id']][result_src[c^1]].append(result[result_src[c^1]])
            common_results[result['project']][result_src[c^1]][result[result_src[c^1]]['id']] = \
                  common_results[result['project']][r][result[r]['id']]
            break
         c += 1
      else:
         data = { 'bauhaus' : [], 'af' : [] }
         for r in result_src:
            data[r].append(result[r])
         for r in result_src:
            common_results[result['project']][r][result[r]['id']] = data

   for p in projects:
      for r in result_src:
         for k in common_results[p][r].iterkeys():
            del globals()[r+'_results'][p][k]

   pool = Pool()
   pool.map(format_common, projects)

   print(json.dumps({ 'common' : common_results, 'bauhaus' : bauhaus_results, 'af' : af_results },
      sort_keys=True, indent=3, separators=(',', ' : ')))
