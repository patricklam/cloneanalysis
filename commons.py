#!/usr/bin/env python

benchmarks = ['jdom', 'jgrapht', 'jmeter', 'weka', 'jfree', 'gvis', 'hsqldb', 'poi', 'jodatime', 'cc']

project_dir = '../projects/'

bauhaus_dir = './bauhaus-complete-data/'

dirs = {
      'jdom' :     'jdom',
      'jgrapht' :  'jgrapht',
      'jmeter' :   'jmeter',
      'weka' :     'weka',
      'jfree' :    'jfreechart',
      'gvis' :     'google-visualization',
      'hsqldb' :   'hsqldb',
      'poi' :      'poi',
      'jodatime' : 'joda-time',
      'cc' :       'apache-commons-collections',
}

def af_result_file_name(project):
   return 'results/%s/method_sets_by_assert_flow' % project
def bauhaus_result_file_name(project):
   return '%s.txt' % dirs[project]
