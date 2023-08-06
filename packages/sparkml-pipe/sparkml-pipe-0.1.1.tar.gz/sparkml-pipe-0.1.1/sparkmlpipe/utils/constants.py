# -*- encoding: utf-8 -*-
from os.path import dirname

LOGGING_CONF = 'conf/logging.yaml'
CONFIG_REGRESSOR_LINEAR_FILE = 'conf/conf_regressor_linear.yaml'
CONFIG_CLASSIFY_LOG_FILE = 'conf/conf_classify_log.yaml'
CONFIG_REGRESSOR_RF_FILE = 'conf/conf_regressor_rf.yaml'
CONFIG_CLASSIFY_RF_FILE = 'conf/conf_classify_rf.yaml'
CONFIG_CORR_FILE = 'conf/conf_corr.yaml'


ROOT_PATH = dirname(dirname(dirname(__file__)))
APP_PATH = dirname(dirname(__file__))

STRING_TYPE = 'string'
NUM_TYPE = 'numeric'

# scale types
MIN_MAX_SCALER_TYPE = 1
STANDARD_SCALER_TYPE = 2
MAXABS_SCALER_TYPE = 3

# impute types
MEAN_IMPUTER_TYPE = 1
MEDIAN_IMPUTER_TYPE = 2

# feature prep types
CHISQ_FEAT_TYPE = 1
PCA_FEAT_TYPE = 2

# pipe type
CLASSIFICATION = 1
REGRESSION = 2
CORRELATION = 3

# classifier types
LOGISTIC_REGRESSION_CLASSIFIER = 1
RANDOM_FOREST_CLASSIFIER = 2

# regressor types
LINEAR_REGRESSION_REGRESSOR = 1
RANDOM_FOREST_REGRESSOR = 2

# correlation methods
PEARSON_CORR = 'pearson'
SPEARMAN_CORR = 'spearman'
