#!/bin/bash

path_env="data_output/env.txt"
python --version > $path_env
python -c "import scipy as sp; print('scipy', sp.version.full_version)" >> $path_env
python -c "import statsmodels; print('statsmodels', statsmodels.__version__)" >> $path_env
python -c "import sklearn; print('sklearn', sklearn.__version__)" >> $path_env
python -c "import seaborn; print('seaborn', seaborn.__version__)" >> $path_env
