#!/usr/bin/env python

import sys,json,numpy,random,os,os.path
import scipy.stats
from scipy.stats import norm,t
from commons import *

script_dir = os.path.realpath(os.path.dirname(__file__)) + '/'

numpy.seterr(all='raise')

def format_floats(num):
   return '%.1f' % num

confidence_level = .95
half_alpha = (1 - confidence_level)/2.0
def confInt(ss, pop, rate):
   return (t.ppf(1-half_alpha, ss-1) if ss < 30 else norm.ppf(1-half_alpha))*numpy.sqrt(rate*(1-rate)/float(ss)*(pop-ss)/(pop-1))

template = """
\\notslides{
\\begin{table*}[t]
   \\caption{\\label{tab:%s}%s}
}
   {
%s
      \\begin{tabular}{%s}
%s
      \\end{tabular}
%s
   }
\\notslides{\\end{table*}}
"""

projects = sys.argv[1:] if len(sys.argv) > 1 else benchmarks

project_names = {
      'jdom' : 'JDOM',
      'jgrapht' : 'JGraphT',
      'jmeter' : 'JMeter',
      'weka' : 'Weka',
      'jfree' : 'JFreeChart',
      'gvis' : 'Google Visualization',
      'hsqldb' : 'HSQLDB',
      'poi' : 'Apache POI',
      'jodatime' : 'Joda-Time',
      'cc' : 'Commons Collections'
}

tables = ('clones', 'asserts', 'samples', 'filters', 'compares_af', 'compares_bauhaus')

#data
samples = {
   'size' : {
      'jdom' :     20,
      'jgrapht' :  11,
      'jmeter' :   20,
      'weka' :     20,
      'jfree' :    20,
      'gvis' :     20,
      'hsqldb' :   20,
      'poi' :      20,
      'jodatime' : 20,
      'cc' :       20
   },
   'true' : {
         'jdom' :     17,
         'jgrapht' :  11,
         'jmeter' :   17,
         'weka' :     16,
         'jfree' :    14,
         'gvis' :     12,
         'hsqldb' :   15,
         'poi' :      6,
         'jodatime' : 19,
         'cc' :       17
   },
   'false' : {
         'jdom' :     0,
         'jgrapht' :  0,
         'jmeter' :   0,
         'weka' :     1,
         'jfree' :    3,
         'gvis' :     1,
         'hsqldb' :   2,
         'poi' :      11,
         'jodatime' : 0,
         'cc' :       1
   }
}

filters = {
   'size' : {
   },
   'true' : {
   },
   'false' : {
   }
}

#templates
clones_template = template % (\
      'stats_clones',
      'Statistics of detected clones plaguing 44\\%% methods in test suites and showing clone sets tend to have few methods~(3), classes~(2), and packages~(1).',
      """
      \\thesis{\\scriptsize}
      \\thesis{\\begin{adjustwidth}{-85pt}{}}
      \\paper{\\small}
      \\paper{\\begin{adjustwidth}{-55pt}{}}
      """,
      """r@{\quad}
         r
         r
         r
         |rrr|
         r
         |rrr|
         r
         |rrr
      """,
      """
         & \\multirow{2}{*}{\\begin{minipage}{3em}\\begin{flushright} Clone\\\\ Sets\\end{flushright}\\end{minipage}}
         & \\multirow{2}{*}{Methods}
         & \\multirow{2}{*}{\\begin{minipage}{6em}\\begin{flushright} \\%% Methods\\\\ in Clone Sets \\end{flushright}\\end{minipage}}
         & \\multicolumn{3}{c|}{Methods/Set}
         & \\multirow{2}{*}{Classes}
         & \\multicolumn{3}{c|}{Classes/Set}
         & \\multirow{2}{*}{Packages}
         & \\multicolumn{3}{c}{Packages/Set}
         \\\\
         &
         &
         &
         & Median & Mean & $\\sigma$
         &
         & Median & Mean & $\\sigma$
         &
         & Median & Mean & $\\sigma$
         \\\\
         &
         &
         &
         & & &
         &
         & & &
         &
         & & &
         \\\\
         %s
         """,
      """
      \\thesis{\\end{adjustwidth}}
      \\paper{\\end{adjustwidth}}
      """,
         )

asserts_template = template % (\
      'stats_asserts',
      'Counts of assertions in clone sets. The median clone set contains 4 assertions.',
      """\\centering""",
      """r@{\quad}
         r
         r
         r
         |rrr
      """,
      """
         & \\multirow{2}{*}{\\begin{minipage}{3em}\\begin{flushright} Clone\\\\ Sets\\end{flushright}\\end{minipage}}
         & \\multirow{2}{*}{Assertions}
         & \\multirow{2}{*}{\\begin{minipage}{6em}\\begin{flushright} \\%% Assertions\\\\ in Clone Sets \\end{flushright}\\end{minipage}}
         & \\multicolumn{3}{c}{Assertions/Set}
         \\\\
         &
         &
         &
         & Median & Mean & $\\sigma$
         \\\\
         &
         &
         &
         & & &
         \\\\
         %s
         """,
      '',
         )

samples_template = template % (\
      'stats_samples',
      'Sampling-based investigation shows that 75\\%% of the reported clone sets are true positives. Confidence intervals included for 95\\%% confidence level.',
      """
\\centering
\\thesis{\\scriptsize}
""",
      """r@{\quad}
         r
         r
         r
         r
         r
         r
         """,
      """
         & {\\begin{minipage}{3em}\\begin{flushright} Clone\\\\ Sets\\end{flushright}\\end{minipage}}
         & {\\begin{minipage}{3em}\\begin{flushright} Sample\\\\ Size\\end{flushright}\\end{minipage}}
         & {\\begin{minipage}{8em}\\begin{flushright} \\%% True Positives\\\\ in Samples \\end{flushright}\\end{minipage}}
         & {\\begin{minipage}{10em}\\begin{flushright} \\%% Fragmented True \\\\Positives in Samples \\end{flushright}\\end{minipage}}
         & {\\begin{minipage}{8em}\\begin{flushright} \\%% False Positives\\\\ in Samples \\end{flushright}\\end{minipage}}
         & {\\begin{minipage}{7em}\\begin{flushright} Confidence\\\\ Interval (\\%%)\\end{flushright}\\end{minipage}}
         \\\\
         &
         &
         &
         &
         &
         &
         \\\\
         %s
         """,
      '',
         )

filters_template = template % (\
      'stats_filters',
      'Filtering is effective---87\\%% of filtered-out clone sets are either false positives or fragmented true positives.',
      """
\\centering
\\thesis{\\scriptsize}
""",
      """r@{\quad}
         r
         r
         r
         r
      """,
      """
         & {\\begin{minipage}{10em}\\begin{flushright} Clone Sets\\\\ Removed by Filter\\end{flushright}\\end{minipage}}
         & {\\begin{minipage}{10em}\\begin{flushright} \\%% False Positives\\\\ Removed  \\end{flushright}\\end{minipage}}
         & {\\begin{minipage}{10em}\\begin{flushright} \\%% Fragmented True \\\\Positives Removed  \\end{flushright}\\end{minipage}}
         & {\\begin{minipage}{10em}\\begin{flushright} \\%% True Positives\\\\ Removed \\end{flushright}\\end{minipage}}
         \\\\
         &
         &
         &
         &
         \\\\
         %s
         """,
      '',
         )

compares_af_template = template % (\
      'stats_compares_af',
      'How Bauhaus performed against Assertion Fingerprints---45\\%% of clone sets from Assertion Fingerprints were not detected by Bauhaus.',
      """
\\thesis{\\begin{adjustwidth}{-15pt}{}}
\\paper{\\begin{adjustwidth}{-15pt}{}}
""",
      """r@{\quad}
         rrrr|
         r
      """,
      """
         & \\multicolumn{4}{c|}{Clone sets also detected by Bauhaus}
         & \\multirow{2}{*}{\\begin{minipage}{10em}\\begin{flushright}Clone sets not\\\\detected by Bauhaus\\end{flushright}\\end{minipage}}
         \\\\
         & Type~1 & Type~2 & Type~3 & Total
         &
         \\\\
         & & & &
         &
         \\\\
         %s
         """,
      """
      \\thesis{\\end{adjustwidth}}
      \\paper{\\end{adjustwidth}}
      """,
         )

compares_bauhaus_template = template % (\
      'stats_compares_bauhaus',
      'How Assertion Fingerprints performed against Bauhaus---Assertion Fingerprints found 49\\%% of clone sets detected by Bauhaus.',
      """
\\thesis{\\begin{adjustwidth}{-35pt}{}}
\\paper{\\begin{adjustwidth}{-35pt}{}}
""",
      """r@{\quad}
         rrrr|
         rrrr
      """,
      """
         & \\multicolumn{4}{c|}{Clone sets also detected by A.F.}
         & \\multicolumn{4}{c}{Clone sets not detected by A.F.}
         \\\\
         & Type~1 & Type~2 & Type~3 & Total
         & Type~1 & Type~2 & Type~3 & Total
         \\\\
         & & & &
         & & & &
         \\\\
         %s
         """,
      """
      \\thesis{\\end{adjustwidth}}
      \\paper{\\end{adjustwidth}}
      """,
         )

#table rows
clones_table_rows = []
clones_row_template = '         %s \
& %d \
& %d \
& %d \
& %d & %s & %s \
& %d \
& %d & %s & %s \
& %d \
& %d & %s & %s \
%s\\\\'

asserts_table_rows = []
asserts_row_template = '         %s \
& %d \
& %d \
& %d \
& %d & %s & %s \
%s\\\\'

samples_table_rows = []
samples_row_template = '         %s \
& %d \
& %d \
& %d \
& %d \
& %d \
& %d \
%s\\\\'

filters_table_rows = []
filters_row_template = '         %s \
& %d \
& %d \
& %d \
& %d \
%s\\\\'

compares_af_table_rows = []
compares_af_row_template = '         %s \
& %d \
& %d \
& %d \
& %d \
& %d \
%s\\\\'

compares_bauhaus_table_rows = []
compares_bauhaus_row_template = '         %s \
& %d \
& %d \
& %d \
& %d \
& %d \
& %d \
& %d \
& %d \
%s\\\\'

#stats
stats = {}

total_stats = {
      'sets' : [],
      'not_sets' : [],
      'methods' : [],
      'packages' : [],
      'classes' : [],
      'asserts' : [],
      'assertsPerMethod' : [],
      'totalStaticCalls' : [],
      'totalMethods' : [],
      'relevantCloneSets' : [],
      'n/a' : [0]
}

compares_stats = {
}

#process
count = 0
with open(''.join([script_dir, 'results/compare_results.json']), 'r') as compare_results_file:
   compare_results = json.load(compare_results_file)
   with open(''.join([script_dir, 'results/filtered_sets.json']), 'r') as filtered_sets_file:
      filtered_sets = json.load(filtered_sets_file)
      for project in sorted(projects, key=lambda project: project_names[project].upper()):
         count += 1
         for i in ('true', 'false'):
            filters[i][project] = len(filtered_sets[project][i])
         with open(''.join([script_dir, 'results/', project, '/stats_af']), 'r') as stats_af_file:
            stats_af = json.load(stats_af_file)

            total_stats['totalStaticCalls'].append(stats_af['others']['totalStaticCalls'])
            total_stats['totalMethods'].append(stats_af['others']['totalMethods'])
            total_stats['sets'].append(stats_af['detail']['sets']['hist'][0]['count'])
            filters['size'][project] = stats_af['detail']['sets']['hist'][1]['count']

            for i in ('samples', 'filters'):
               for j in ('size', 'true', 'false'):
                  key = ''.join([i, '_', j])
                  if key not in total_stats:
                     total_stats[key] = []
                  total_stats[key].append(globals()[i][j][project])

            stats[project] = {}

            for i in stats_af['detail']['relevantCloneSets']['hist']:
               if i['_id']:
                  stats[project]['relevantCloneSets'] = i['count']
            if 'relevantCloneSets' not in stats[project]:
               stats[project]['relevantCloneSets'] = 0
            total_stats['relevantCloneSets'].append(stats[project]['relevantCloneSets']);

            for k in ('methods', 'packages', 'classes', 'asserts', 'assertsPerMethod'):
               if k not in stats[project]:
                  stats[project][k] = { 'list' : [] }
               for hist in stats_af['detail'][k]['hist']:
                  stats[project][k]['list'].extend([hist['_id']]*hist['count'])

               for f in ('sum', 'median', 'mean', 'std'):
                  stats[project][k][f] = getattr(numpy, f)(stats[project][k]['list'])

               total_stats[k].extend(stats[project][k]['list'])


            clones_row = clones_row_template % (\
                  project_names[project],

                  stats_af['detail']['sets']['hist'][0]['count'],

                  stats[project]['methods']['sum'],
                  round(stats[project]['methods']['sum']/float(stats_af['others']['totalMethods'])*100),

                  stats[project]['methods']['median'],
                  format_floats(stats[project]['methods']['mean']),
                  format_floats(stats[project]['methods']['std']),

                  stats[project]['classes']['sum'],
                  stats[project]['classes']['median'],
                  format_floats(stats[project]['classes']['mean']),
                  format_floats(stats[project]['classes']['std']),

                  stats[project]['packages']['sum'],
                  stats[project]['packages']['median'],
                  format_floats(stats[project]['packages']['mean']),
                  format_floats(stats[project]['packages']['std']),

                  ''
                  )

            asserts_row = asserts_row_template % (\
                  project_names[project],

                  stats_af['detail']['sets']['hist'][0]['count'],

                  stats[project]['asserts']['sum'],

                  round(stats[project]['assertsPerMethod']['sum']/float(stats_af['others']['totalStaticCalls'])*100),

                  stats[project]['asserts']['median'],
                  format_floats(stats[project]['asserts']['mean']),
                  format_floats(stats[project]['asserts']['std']),
                  ''
                  )

            samples_row = samples_row_template % (\
                  project_names[project],

                  stats_af['detail']['sets']['hist'][0]['count'],

                  samples['size'][project],
                  round(samples['true'][project]/float(samples['size'][project])*100),
                  round((samples['size'][project]-samples['true'][project]-samples['false'][project])/float(samples['size'][project])*100),
                  round(samples['false'][project]/float(samples['size'][project])*100),
                  round(confInt(samples['size'][project], stats_af['detail']['sets']['hist'][0]['count'], samples['true'][project]/float(samples['size'][project]))*100),

                  ''
                  )

            filters_row = filters_row_template % (\
                  project_names[project],

                  filters['size'][project],

                  round(filters['false'][project]/float(filters['size'][project])*100),
                  round((filters['size'][project]-filters['true'][project]-filters['false'][project])/float(filters['size'][project])*100),
                  round(filters['true'][project]/float(filters['size'][project])*100),

                  ''
                  )

            compares_stats[project] = {
                  'bauhaus' : {
                     'true' : {
                        '1' : set(),
                        '2' : set(),
                        '3' : set()
                        },
                     'false' : {
                        '1' : set(),
                        '2' : set(),
                        '3' : set()
                        }
                     },
                  'af' : {
                     'true' : {
                        '1' : set(),
                        '2' : set(),
                        '3' : set()
                        },
                     'false' : {
                        }
                     },
                  }

            for common in compare_results['common'][project]:
               for ac in common['af']:
                  compares_stats[project]['af']['true'][common['bauhaus'][-1]['type']].add(ac['id'])
               for bc in common['bauhaus']:
                  compares_stats[project]['bauhaus']['true'][bc['type']].add(bc['id'])

            for bk, bv in compare_results['bauhaus'][project].iteritems():
               compares_stats[project]['bauhaus']['false'][bv['type']].add(bk)

            for compare_t in ('bauhaus', 'af'):
               for compare_c in ('true', 'false'):
                  if '1' in compares_stats[project][compare_t][compare_c]:
                     compares_stats[project][compare_t][compare_c]['1'].difference_update(compares_stats[project][compare_t][compare_c]['2'])
                     compares_stats[project][compare_t][compare_c]['1'].difference_update(compares_stats[project][compare_t][compare_c]['3'])
                     compares_stats[project][compare_t][compare_c]['2'].difference_update(compares_stats[project][compare_t][compare_c]['3'])
                     for compare_n in compares_stats[project][compare_t][compare_c].iterkeys():
                        #if compare_t == 'af':
                        #   print (project, compare_t, compare_c, compare_n, compares_stats[project][compare_t][compare_c][compare_n])
                        compares_stats[project][compare_t][compare_c][compare_n] = len(compares_stats[project][compare_t][compare_c][compare_n])

            #print (project, 'af', 'false', 0, compare_results['af'][project].keys())

            compares_stats[project]['bauhaus']['true']['total'] = sum(compares_stats[project]['bauhaus']['true'].values())
            compares_stats[project]['bauhaus']['false']['total'] = sum(compares_stats[project]['bauhaus']['false'].values())
            compares_stats[project]['af']['true']['total'] = sum(compares_stats[project]['af']['true'].values())
            compares_stats[project]['af']['false']['total'] = len(compare_results['af'][project])

            compares_af_row = compares_af_row_template % (\
                  project_names[project],

                  compares_stats[project]['af']['true']['1'],
                  compares_stats[project]['af']['true']['2'],
                  compares_stats[project]['af']['true']['3'],
                  compares_stats[project]['af']['true']['total'],

                  compares_stats[project]['af']['false']['total'],

                  ''
                  )

            compares_bauhaus_row = compares_bauhaus_row_template % (\
                  project_names[project],

                  compares_stats[project]['bauhaus']['true']['1'],
                  compares_stats[project]['bauhaus']['true']['2'],
                  compares_stats[project]['bauhaus']['true']['3'],
                  compares_stats[project]['bauhaus']['true']['total'],

                  compares_stats[project]['bauhaus']['false']['1'],
                  compares_stats[project]['bauhaus']['false']['2'],
                  compares_stats[project]['bauhaus']['false']['3'],
                  compares_stats[project]['bauhaus']['false']['total'],

                  ''
                  )

            line_dist = '[0.5em]'
            for name in tables:
               if count % 4 == 0:
                  locals()[name+'_row'] += line_dist
               globals()[name+'_table_rows'].append(locals()[name+'_row'])


for name in tables:
   globals()[name+'_table_rows'][-1] += '[0.7em]'

total_stats_sum = {}
for k, v in total_stats.iteritems():
   total_stats_sum[k] = float(numpy.sum(v))

clones_row = clones_row_template % (\
      '{\\bf Total}',

      total_stats_sum['sets'],

      total_stats_sum['methods'],
      round(total_stats_sum['methods']/float(total_stats_sum['totalMethods'])*100),
      numpy.median(total_stats['methods']),
      format_floats(numpy.mean(total_stats['methods'])),
      format_floats(numpy.std(total_stats['methods'])),

      total_stats_sum['classes'],
      numpy.median(total_stats['classes']),
      format_floats(numpy.mean(total_stats['classes'])),
      format_floats(numpy.std(total_stats['classes'])),

      total_stats_sum['packages'],
      numpy.median(total_stats['packages']),
      format_floats(numpy.mean(total_stats['packages'])),
      format_floats(numpy.std(total_stats['packages'])),

      ''
      )

asserts_row = asserts_row_template % (\
      '{\\bf Total}',

      total_stats_sum['sets'],

      total_stats_sum['assertsPerMethod'],
      round(total_stats_sum['assertsPerMethod']/float(total_stats_sum['totalStaticCalls'])*100),

      numpy.median(total_stats['asserts']),
      format_floats(numpy.mean(total_stats['asserts'])),
      format_floats(numpy.std(total_stats['asserts'])),

      ''
      )

samples_row = samples_row_template % (\
      '{\\bf Total}',

      total_stats_sum['sets'],

      total_stats_sum['samples_size'],
      round(total_stats_sum['samples_true']/total_stats_sum['samples_size']*100),
      round((total_stats_sum['samples_size']-total_stats_sum['samples_false']-total_stats_sum['samples_true'])/total_stats_sum['samples_size']*100),
      round(total_stats_sum['samples_false']/total_stats_sum['samples_size']*100),
      round(confInt(total_stats_sum['samples_size'], total_stats_sum['sets'], total_stats_sum['samples_true']/total_stats_sum['samples_size'])*100),
      ''
      )

filters_row = filters_row_template % (\
      '{\\bf Total}',

      total_stats_sum['filters_size'],
      round(total_stats_sum['filters_false']/float(total_stats_sum['filters_size'])*100),
      round((total_stats_sum['filters_size']-total_stats_sum['filters_false']-total_stats_sum['filters_true'])/float(total_stats_sum['filters_size'])*100),
      round(total_stats_sum['filters_true']/float(total_stats_sum['filters_size'])*100),
      ''
      )

compares_af_row = compares_af_row_template % (\
      '{\\bf Total}',

      sum([compares_stats[project]['af']['true']['1'] for project in projects]),
      sum([compares_stats[project]['af']['true']['2'] for project in projects]),
      sum([compares_stats[project]['af']['true']['3'] for project in projects]),
      sum([compares_stats[project]['af']['true']['total'] for project in projects]),

      sum([compares_stats[project]['af']['false']['total'] for project in projects]),

      ''
      )

compares_bauhaus_row = compares_bauhaus_row_template % (\
      '{\\bf Total}',

      sum([compares_stats[project]['bauhaus']['true']['1'] for project in projects]),
      sum([compares_stats[project]['bauhaus']['true']['2'] for project in projects]),
      sum([compares_stats[project]['bauhaus']['true']['3'] for project in projects]),
      sum([compares_stats[project]['bauhaus']['true']['total'] for project in projects]),

      sum([compares_stats[project]['bauhaus']['false']['1'] for project in projects]),
      sum([compares_stats[project]['bauhaus']['false']['2'] for project in projects]),
      sum([compares_stats[project]['bauhaus']['false']['3'] for project in projects]),
      sum([compares_stats[project]['bauhaus']['false']['total'] for project in projects]),

      ''
      )

items = ('methods', 'classes', 'packages', 'asserts')

output_file_template = 'table_%s.tex'
with open('table_notes', 'w') as f:
   f.write(''.join([ '%', \
   ', '.join(['%s range [%d, %d]' % (i, min(total_stats[i]), max(total_stats[i])) \
   for i in items]) ]))
   f.write('\n')
   f.write(''.join([ '%', \
      ', '.join(['%s skewness (%.2f)' % (i, scipy.stats.skew(total_stats[i])) \
      for i in items]) ]))

for name in tables:
   globals()[name+'_table_rows'].append(globals()[name+'_row'])
   with open(output_file_template % name, 'w') as f:
      f.write(globals()[name+'_template'] % '\n'.join(globals()[name+'_table_rows']))
