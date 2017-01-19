#!/bin/bash

project_dir="${PROJECT_DIR:=$HOME/projects}"

settings_dir="${SETTINGS_DIR:=settings}"

logs_dir=logs

run() {
   echo "Start benchmarking $1"
   if hash time 2>/dev/null; then
      PROJECT_DIR=$project_dir SETTINGS_DIR=$settings_dir time -f '\t%E elapsed' ant main -Dprops=${1} > $logs_dir/${1}.log
   else
      PROJECT_DIR=$project_dir SETTINGS_DIR=$settings_dir ant main -Dprops=${1} > $logs_dir/${1}.log
   fi
}

ant clean

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
