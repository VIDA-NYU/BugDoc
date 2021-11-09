import numpy as np
import os
import pandas as pd
import traceback
from sklearn.ensemble import IsolationForest
from sklearn.covariance import EllipticEnvelope
from sklearn.preprocessing import LabelEncoder

detectors = {"if":IsolationForest, "ee":EllipticEnvelope}
def execute(experiements_path):
    experiments_list_path = os.path.join(experiements_path, 'list.txt')
    fileicareabout = open(experiments_list_path, "r")
    alllines = fileicareabout.readlines()
    fileicareabout.close()
    rng = np.random.RandomState(42)
    for experiment in alllines:
        experiment_name = os.path.join(experiements_path, experiment[:-1])
        # data_train = pd.read_csv(os.path.join(experiment_name, "pass.csv"))
        data_test = pd.read_csv(os.path.join(experiment_name, "fail.csv"))
        for detector in detectors:
            output_name = os.path.join(experiment_name, detector + ".res")
            if os.path.exists(output_name):
                os.remove(output_name)
            f = open(output_name, "a")
            for contamination in [2,4,8,16,32,64]:
                try:
                    #for column in data_train.columns:
                    clf = detectors[detector](random_state=rng, contamination=float(contamination)/100.0)#float(experiment_name.split("_")[-4]) / 100.0)
                        # clf.fit(data_train[column].values.reshape(-1, 1))
                        # predictions = clf.predict(data_test[column].values.reshape(-1, 1))
                    #clf.fit(data_train)
                    predictions = clf.fit_predict(data_test)
                    print(predictions)
                    outliers = []

                    for i in range(len(predictions)):
                        if predictions[i] == -1:
                            outliers.append(i)

                    f.write(str(outliers) + '\n')


                except:
                    pass
                    traceback.print_exc()
                    output_name = os.path.join(experiment_name, detector+".res")
                    f.write("FAIL")
            f.close()


