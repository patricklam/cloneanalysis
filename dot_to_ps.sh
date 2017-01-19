#!/bin/bash

run() {
   if [ -d "results/${1}/graph" ]; then
      rm -f results/${1}/graph/*.ps

      for i in results/${1}/graph/*.dot
      do
         fdp -Tps $i -o ${i%.*}.ps &
      done
      wait
   fi
}

if [ $# -eq 0 ]
then
   for i in jdom jgrapht jmeter weka jfree gvis hsqldb poi jodatime cc
   do
      run $i
   done
else
   for i
   do
      run $i
   done
fi
