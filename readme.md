# Data science technical-test for INRIA

## Repository content

* `ds_inria.ipynb`
* Data: 1 file in sql (2 tables exist: the patient table and the pcr table)


## Test guidelines

In this test, we have two tables: the patient information (ID, name, family, address, etc.) and the pcr test (ID and pcr). The pcr table indicates if an ID is COVID positive or negative.
The task is to find the dublicates considering that there might be typos in the data.
There is no constraint in python libraries

## Solution
To solve this problem we compare each of the records with other ones in patient dataframe and if their similarity is high enough (here we considered >90% similarity), then we consider and convert them as one record.

To do so, the fuzzywuzzy similarity is used. This library works fine for strings and it can match the typos. However, the speed of dataframes are the issue. In order to speed up the task we can do:
* use `rapidfuzz` library instead of `fuzzywuzzy` (the result is same but it speedups the task)
* Convert the dataframes to list or array:
** The patient dataframe is converted to list as list is faster for comparison
** The pcr dataframe is converted to dictionary
