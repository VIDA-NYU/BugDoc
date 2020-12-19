# BugDoc [![Build Status](https://travis-ci.org/VIDA-NYU/BugDoc.svg?branch=master)](https://travis-ci.org/VIDA-NYU/BugDoc)

BugDoc is a framework for finding root causes of errors in computational pipelines.

For more detailed information about the framework, please refer to our SIGMOD paper:

[*BugDoc: Algorithms to Debug Computational Processes. Raoni Lourenço, Juliana Freire, and Dennis Shasha. In ACM SIGMOD, 2020.*](https://arxiv.org/abs/2004.06530)


# Mission, Vision and Problem Statements

Our mission is to improve the quality of science in general by alleviating the burden of debugging computational
pipelines manually. 

BugDoc will be a must-have item in the computational pipeline designer's toolkit. It will be always
open and customizable to adhere to any workflow system.

Given a set of computational pipeline instances, some of which led to bad or questionable results, our goal is to find the root causes of failures, possibly by creating and executing new pipeline instances.



# Team
* [Raoni Lourenço][rl] (New York University)
* [Juliana Freire][jf] (New York University)
* [Dennis Shasha][ds] (New York University)

[rl]: https://engineering.nyu.edu/raoni-lourenco
[jf]: http://vgc.poly.edu/~juliana/
[ds]: http://cs.nyu.edu/shasha/

# Contributions

We are currently managing contributions by [issues](https://github.com/VIDA-NYU/BugDoc/issues), more detailed procedure 
will be included soon.

## 1. How To Build

To install latest development version:

    $ pip install -e bugdoc_api
    
## 2. Experiments

In this branch, we show how to reproduce the results of our SIGMOD'20 paper.

We provide the following script to make it easier for re-running our experiments (these must be run from the [``sigmod20/``](sigmod20) directory):

* [``prepareSoftware.sh``](sigmod20/prepareSoftware.sh) Install the necessary python libraries
* [``runExperiments.sh``](sigmod20/runExperiments.sh) creates the synthetic pipelines and runs all the experiments (including the generation of the plots), except for the real-world experiment, since this one depends on installing some additional dependencies and configuring a Cluster. For more information about this experiment, please see its corresponding section].

It is important to note that, since the pipelines are generated randomly, the performance results and plots will be consistent but visually different than the ones published on the paper.

Alternatively, we provide [ReproZip](https://vida-nyu.github.io/reprozip/) packages for the original plots published in the paper, where you can obtain the original performance results. The ReproZip packages were mostly created on a Ubuntu 16.04 LTS machine, having the same versions for Python, matplotlib, and Postgres.

More detailed information about our experiments can be found in the following sections.

### 2.1. Machine Configuration

The experiments were executed on a MacBook Pro, running macOS Catalina version 10.15.7, and having an 2.2 GHz Quad-Core Intel Core i7 and 16 of RAM. The installed software is the following:

* Java 1.8.0_144
* PostgresSQL 11
* Python 3.6

All the files related to the experiments are located under [``sigmod20/``](sigmod20). All the scripts assume that these softwares are properly installed and that there is a database instance with the following [configuration](sigmod20/experiments/db.conf).
