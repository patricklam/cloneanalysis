#!/usr/bin/env bash

run() {
   mongo ccanalysis --quiet --eval "var project='${1}'" stats_cc.js > results/${1}/stats_cc
   mongo ccanalysis --quiet --eval "var project='${1}'" stats_af.js > results/${1}/stats_af
   mongo ccanalysis --quiet --eval "var project='${1}'" data_af.js > results/${1}/data_af
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
