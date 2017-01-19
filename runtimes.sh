rm -f runtimes
touch runtimes;
for i in logs/*.log
do
   echo $i  >> runtimes;
   cat $i | tail -2 >> runtimes;
   echo " " >> runtimes;
   echo " " >> runtimes;
   echo " " >> runtimes;
done
