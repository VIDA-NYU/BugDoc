# BugDoc [![Build Status](https://travis-ci.org/VIDA-NYU/BugDoc.svg?branch=master)](https://travis-ci.org/VIDA-NYU/BugDoc)

BugDoc is a framework for finding root causes of errors in computational pipelines.

For more detailed information about the framework, please refer to our SIGMOD paper:

[*Algorithms to Debug Computational Processes. Raoni Lourenço, Juliana Freire, and Dennis Shasha. In ACM SIGMOD, 2020.*](https://arxiv.org/abs/2004.06530)


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
