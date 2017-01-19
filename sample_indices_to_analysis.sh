#!/bin/bash

run() {
   cp "results/${i}/sample_indices" "results/${i}/sample_analysis"
}

if [ $# -eq 0 ]
then
   for i in jdom jgrapht jmeter weka jfree gvis hsqldb poi jodatime cc
   do
      if [ -d "results/${i}" ]; then
         run $i &
      fi
   done
   wait
else
   for i
   do
      if [ -d "results/${i}" ]; then
         run $i &
      fi
   done
   wait
fi
