import pandas as pd
import numpy as np
import sys

from sklearn.datasets import fetch_california_housing

from evidently import ColumnMapping

from evidently.report import Report
from evidently.metrics.base_metric import generate_column_metrics
from evidently.metric_preset import DataDriftPreset, TargetDriftPreset
from evidently.metrics import *

from evidently.test_suite import TestSuite
from evidently.tests.base_test import generate_column_tests
from evidently.test_preset import DataStabilityTestPreset, NoTargetPerformanceTestPreset
from evidently.tests import *

def main():
    reference = pd.read_csv("./data/processed/reference_data.csv")
    current = pd.read_csv("./data/processed/current_data.csv")
    
    report = Report(metrics=[DataDriftPreset()])
    report.run(reference_data=reference, current_data=current)
    report.save('./reports/testing_data/data_drift.json')

    tests = TestSuite(tests=[
        TestNumberOfConstantColumns(),
        TestNumberOfDuplicatedRows(),
        TestNumberOfDuplicatedColumns(),
        TestColumnsType(),
        TestNumberOfDriftedColumns(),
    ])

    tests.run(reference_data=reference, current_data=current)
    test_results = tests.as_dict()

    # Check if any test failed
    if test_results['summary']['failed_tests'] > 0:
        print("Some tests failed:")
        print(test_results['summary'])
        

        sys.exit(1)
    else:
        print("All tests passed!")




    tests.save_html("reports/sites/index.html")

if __name__ == "__main__":
    main()
