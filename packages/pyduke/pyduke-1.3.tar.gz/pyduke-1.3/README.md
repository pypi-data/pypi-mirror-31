# Introduction

The project pyduke (Python Duke) consists of generic and machine learning utility modules. The package details are as follows

| Module                          | Description                                                  |
| ------------------------------- | ------------------------------------------------------------ |
| pyduke.common.core_util.py      | Core language utilities                                      |
| pyduke.common.data_util.py      | Machine learning data cleaning utilities                     |
| pyduke.mlutil.data_processor.py | Contains several classes (Estimators) that extend [BaseEstimator](http://scikit-learn.org/stable/modules/generated/sklearn.base.BaseEstimator.html) and [TransformerMixin](http://scikit-learn.org/stable/modules/generated/sklearn.base.TransformerMixin.html). These classes can be used together with [SciKit Learn](http://scikit-learn.org/stable/documentation.html) classes in data cleaning [Pipeline](http://scikit-learn.org/stable/modules/generated/sklearn.pipeline.Pipeline.html). |

# Data Processor Classes

The following classes belong to `pyduke.mlutil.data_processor` module. All classses extend  [BaseEstimator](http://scikit-learn.org/stable/modules/generated/sklearn.base.BaseEstimator.html) and [TransformerMixin](http://scikit-learn.org/stable/modules/generated/sklearn.base.TransformerMixin.html) similar to SciKit Learn classes like [Imputer](http://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.Imputer.html). Input to `fit` and `transform` methods must be a panda [DataFrame](https://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.html)

|  Sl  | Class                     | Description                                                  |
| :--: | ------------------------- | ------------------------------------------------------------ |
|  1   | AddColumn                 | Add new column(s) by invoking corresponding handler(s). The handler should accept a panda [DataFrame](https://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.html) and return a panda [Series](https://pandas.pydata.org/pandas-docs/stable/generated/pandas.Series.html). |
|  2   | RemoveColumn              | Remove list of column(s)                                     |
|  3   | IndependentColumnImputer  | Replace `NaN` in specified column(s) with corresponding strategy (mean|median|mode). Few columns can be selected for `mean` and few others for `mode` and the `NaN` replacement can be done in one transformation. Here, the strategy to replace `NaN` in a column is independent of other columns. |
|  4   | DependentColumnImputer    | An imputer to be used when empty cells (`NaN`) of a column are to be derived from other column(s). Handler associated with each column is invoked.  The handler is expected to accept a panda [DataFrame](https://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.html) and return a panda [Series](https://pandas.pydata.org/pandas-docs/stable/generated/pandas.Series.html). Only `NaN` are replaced from the [Series](https://pandas.pydata.org/pandas-docs/stable/generated/pandas.Series.html). |
|  5   | Mapper                    | Process each cell of given column(s) with corresponding handler and create/replace the cell value with the one returned by the handler. A Mapper maps each cell of a column to another. Thus a new column is created. Optionally the original column may be deleted. |
|  6   | StringToCategoryConverter | Convert column(s) to panda [category](https://pandas.pydata.org/pandas-docs/stable/categorical.html) data type. A category type is more useful for visualizations. Eventually a category can be label encoded, weight encoded or one-hot encoded. This class also adds null types like empty string, `'N/A'`, `'null'` `'none'` into a category 'NULL' (By defaults, customizable using option category_of_empty) |
|  7   | RangeToCategoryConverter  | Classify various numeric ranges into categories. The numerical value of a column may indicate a category. Using the exact value may result in overfitting the model. RangeToCategoryConverter fits the purpose by  associating each range with a category label. |
|  8   | CategoryToWeightEncoder   | Encode category column(s) with corresponding weights.        |
|  9   | CategoryToOneHotEncoder   | Convert category column(s) to one-hot encoded format. Thus adding more features. Note that by default, one of the dummy column is dropped to prevent *dummy variable trap* |
|  10  | Scaler                    | Scale column(s) using a scaler of type specified by `scaler_type`. Currenty, [Standard](http://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.StandardScaler.html) and [MinMax](http://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.MinMaxScaler.html) scalers from SciKit learn are used. Note that the Scaler like all other classes operates on [DataFrame](https://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.html) |

# Example

Taking an example of [Kaggle Titanic Dataset](https://www.kaggle.com/c/titanic/data), the above data processing classes can be used as follows.

```python
import re
import pandas as pd
import pyduke.common.core_util as cu
import pyduke.common.data_util as du
import pyduke.mlutil.data_processor as dp

# Dataset
# -------
X             = pd.read_csv(PROJECT_ROOT + '/dataset/train.csv')
X_final_test  = pd.read_csv(PROJECT_ROOT + '/dataset/test.csv')
y             = X.pop('Survived')


# Handlers
# --------
def convert_name_to_prefix (name):
    # Name format: <lastname> <lastname>, <prefix> <firstname> <middlename>
    # Note <prefix> may have '.' as in 'Mr.' or 'Miss.'
    token = re.sub('\s+', ' ', name).split(',')
    token = token[1].split() if len(token) >= 2 else ['Dear']
    token = token[0].replace('.', '') if len(token) >= 2 else 'Dear'
    return token.upper()

def process_empty_fare(df):
    # Group the entire dataset by column
    grouped = df.groupby('Pclass')    
    series_class_to_fare = grouped['Fare'].agg(np.mean)    
    series_fare = df['Pclass'].apply(lambda x: series_class_to_fare[x])
    return series_fare

def process_sibling_parent (df):
    return df['SibSp'] + df['Parch']   


tuple_age_range = (
    [-1,    3,      12,     19,      39,       59,       79,   120],
    ['INFANT', 'CHILD', 'TEEN', 'YOUTH', 'MIDDLE', 'SENIOR', 'OLD']
)

map_column_category_weight = {
    'Sex':{ 'FEMALE':0, 'MALE':1 },
    'Age':{ 'INFANT':1, 'CHILD':2, 'TEEN':3, 'YOUTH':4, 'MIDDLE':5, 'SENIOR':6, 'OLD':7  }
}

pileline = Pipeline([
    # Remove columns
    ('rm_column'           , dp.RemoveColumn(column=['PassengerId', 'Cabin', 'Ticket'])),
    
    # Impute certain columns based on median and certain others on mode
    ('fill_nan_stats'      , dp.IndependentColumnImputer(
                                 column_median=['Age'], 
                                 column_mode= ['Pclass', 'SibSp', 'Parch', 'Embarked'])),
    
    # Fill empty fare cells based on hander 'process_empty_fare'
    ('fill_empty_fare'     , dp.DependentColumnImputer({'Fare':process_empty_fare})),
    
    # For each cell having the name, the prefix (like Mr, Ms, Sir etc) is extracted 
    # and a new column 'NamePrefix' is created. The original 'Name' column is removed.
    ('add_name_prefix'     , dp.Mapper(
        						{'Name':convert_name_to_prefix}, 
                                  map_column_to_new={'Name':'NamePrefix'},
                                  remove_original=True)),
    
    # A new column is added based on Series returned by handler
    ('add_family_weight'   , dp.AddColumn({'FamilyTotal':process_sibling_parent})),
    
    # Based on age groups, age can be converted into categorical data
    ('age_to_category'     , dp.RangeToCategoryConverter({ 'Age':tuple_age_range })),
    
    # Convert all the columns into a categorical data. This is easier for further analysis.
    ('string_to_category'  , dp.StringToCategoryConverter(['Sex', 'Embarked', 'NamePrefix'])),
    
    # Based on the analysis associate Age and Sex category columns with corresponding weights
    ('category_to_weight'  , dp.CategoryToWeightEncoder(map_column_category_weight)),
    
    # Convert categories to one-hot encoding
    ('category_to_onehot'  , dp.CategoryToOneHotEncoder(['Embarked', 'NamePrefix'])),
    
    # Scale all columns using the default Standard scaler
    ('scale'               , dp.Scaler())
])
X = pileline.fit_transform(X)
X_final_test = pileline.transform(X_final_test)
print ("X.shape={}, X_final_test.shape={}".format(X.shape, X_final_test.shape))

# Return a stratified shuffle split
X_train, y_train, X_test, y_test = du.get_stratified_shuffle_split(X, y, test_size=141)

# Shapes
m, n = X_train.shape
```

