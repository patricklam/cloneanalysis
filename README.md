# Test Method Clone Detector #

This program detects method clones in test suites.
This program is standalone and does not require additional libraries.

### Requirements ###

* Java 1.6 or above.
* MongoDB 2.6 or above
* Benchmark source files
* This program is multi-threaded and may use all cores of your machine.

### How to ###

#### Run ####

* ./run.sh <jdom|jgrapht|jmeter|weka|hsqldb|gvis|poi|jodatime|cc>
* If you want to run other benchmarks, you will have to add settings/<benchmark> setting file. 
  See existing setting files for examples.

#### Stats ####

* ./stats.sh <jdom|jgrapht|jmeter|weka|hsqldb|gvis|poi|jodatime|cc>
* You can run this after ./run.sh which will store the data in MongoDB.

#### Logs ####

* logs/*.logs

#### Settings ####

* settings/<benchmark>

#### Results ####

* results/<benchmark>
