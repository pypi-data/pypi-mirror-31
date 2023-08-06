=================================================
Mindstrong Health Digital Biomarker Model Fitting
=================================================

This package uses Supervised Kernel Principal Components Analysis with cross validation to fit digital biomarker data to target measurements. The software was written by members of the Mindstrong Health Data Science team:

    * Paul Dagum, MD, PhD
    * Greg Ryslik, PhD, FCAS, MAAA
    * Bob Dougherty, PhD
    * Patrick Staples, PhD

Please contact us at `datascience@mindstronghealth.com <datascience@mindstronghealth.com>`_.

NOTE: If you use this software in your work, please cite the following `paper <https://www.nature.com/articles/s41746-018-0018-4>`_:

    Dagum, P. (2018) Digital biomarkers of cognitive function. npj Digital Medicine, issue 1, article 10. DOI: 10.1038/s41746-018-0018-4.

Installation
------------

The easiest way to install the package is via ``easy_install`` or ``pip``::

    $ pip install mindstrong_biomarker_modelfit

This should also take care of the dependencies (numpy, scipy, pandas, and sklearn).

Usage
-----

Simulated digital biomarker and target measure data are included with the project. To fit a model to these example data::

    import numpy as np
    import pandas as pd
    import os
    from mindstrong import mindstrong_modelfit as mindstrong

    target_file = mindstrong.get_example_data('example_targets.csv')
    feature_file = mindstrong.get_example_data('example_features.csv')
    target_colname = 'target1'

    # Load target data
    target_df = pd.read_csv(target_file)
    target_df.set_index('device_id', inplace=True)

    # Load Feature Data
    feature_df = pd.read_csv(feature_file).set_index(['device_id', 'targetDOY'])

    # Cross Validated supervised kernel PCA model-fitting
    cvdf, best_model = mindstrong.calculateCrossValidatedCorrelation(target_df,
                                                                     feature_df,
                                                                     target_colname,
                                                                     fold_type='n',
                                                                     n_folds=5,
                                                                     kernel_training='linear',
                                                                     kernel_training_param=1,
                                                                     kernel_target='linear',
                                                                     kernel_target_param=1,
                                                                     regularization=0.1)

    # Print the final results
    print(best_model)



Copyright & License
-------------------

Copyright (c) 2018, `Mindstrong Health <http://mindstronghealth.com>`_. GNU Affero General Public License.

