API Example
==================

The example below illustrates how to use BugDoc to debug arbitrary computational pipelines. To do that, we need to write two scripts that run in separate parallel processes and communicate with each other through TCP messages.
The *Debugger* script defines the pipeline parameter space, provides an entry point for the pipeline, and calls BugDoc's API.
The second script, *Worker*, is responsible for receiving messages from BugDoc's algorithms and calling the pipeline execution engine to run a pipeline instance and evaluate its output.

