import time


def execute_pipeline(configuration):
    time.sleep(.5)
    return not('script2' in configuration['operator1_script'])

def evaluate_pipeline_output(output):
    return output