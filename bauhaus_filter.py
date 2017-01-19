#!/usr/bin/env python

import sys,re

cases_pattern = re.compile(r'\s+CloneClass\s+(\d+)\s+\(Type (\d+)\)')
clones_pattern = re.compile(r'\((.*?java):(\d+)\)(\d+)')
classes_pattern = re.compile(r'This is for clone class (\d+)')

if __name__ == "__main__":
   stats = """Found %d clones in %d cases.
   Net cloned lines = %d"""

   lines = []
   buffer = []

   input_file = sys.argv[1]

   with open(input_file, 'r') as f:
      case_id = -1
      for line in f:
         m = cases_pattern.match(line)
         if m:
            if len(buffer) > 2 or classes_pattern.match(buffer[-1]):
               lines.extend(buffer)
            del buffer[:]
         elif not clones_pattern.match(line):
            if lines:
               if len(buffer) > 2:
                  lines.extend(buffer)
               del buffer[:]
         buffer.append(line)

   clones = 0
   cases = 0
   linec = 0
   for line in lines:
      if cases_pattern.match(line):
         cases += 1
      else:
         m = clones_pattern.match(line)
         if m:
            clones += 1
            linec += int(m.group(3))

   lines.append(stats % (clones, cases, linec))
   print ''.join(lines)
