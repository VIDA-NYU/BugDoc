Definitions
============

Computational Pipeline
-----------------------
A computational pipeline *CP* is a procedure consisting of a set of parameters *P*,
we denote *i*  an instance of *CP* that defines values for the parameters for a particular run of *CP*.

Pipeline Parameter
-------------------

Any property that changes among distinct execution of a computational pipeline is considered a parameter. For instance, parameters may represent data sources, operations, algorithms, machine learning hyperparameters, and so on.
In BugDoc, we can assign numerical or categorical values to a parameter.


Pipeline Instance
------------------

A pipeline instance *i* is a set of parameter-value pairs, also called configurations, associated to an evaluation result.

Evaluation Function
--------------------

Let *E* be a procedure that evaluates the results of a pipeline instance such that: *E(i)= success* if the results are acceptable, and
*E(i)= failure* otherwise.


Root Cause
-----------

A root cause is a set *R* consisting of Boolean conjunctions of parameter-comparator-value triples (e.g., A > 5 and B = 7) that represent a sufficient condition for a pipeline to fail.

Hence, if the parameter-value pairs of an instance *i*, *(p,v) ∈ i* , satisfy *R* , we have:
*E(i) = failure*.

