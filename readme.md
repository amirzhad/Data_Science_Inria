# Data science technical-test for INRIA

## Repository content

* `ds_inria_main.ipynb`
* Data: 1 file in sql (2 tables exist: the patient table and the pcr table)


## Test guidelines

In this test, we have two tables: the patient information (ID, name, family, address, etc.) and the pcr test (ID and pcr). The pcr table indicates if an ID is COVID positive or negative.
The task is to find the dublicates considering that there might be typos in the data. Also, visualizing the positive cases grouped by age and geographical location.
There is no constraint in python libraries.

## Solution 1
To solve this problem we first check the dataframes and clean them.

We find the conflict, duplicate and wrong ids for pcr dataframe:
* conflict id: if the duplicated id has different pcr value 
* duplicate id: if the id is repeated more than one time
* wrong id: the ids that are not numeric

Then, we do the same for patient dataframe:
* conflict id: if the duplicated id is related to different patients
* duplicate id: if a same record with same id is repeated
* duplicate record: if a record is repeated more than one time
* wrong id: we checked and found no wrong id in patient dataframe (so no need to consider)

In order to find the duplicated records, the fuzzywuzzy similarity is used. In fact, each of the records are compared with other ones in patient dataframe and if their similarity is high enough (here we considered >90% similarity), then we consider and convert them as one record.

This library works fine for strings and it can match the typos. However, the speed of dataframes are the issue. In order to speed up the task we did these steps:
* Using `rapidfuzz` library instead of `fuzzywuzzy` (the result is same but it speedups the task)
* Convert the dataframes to list or array:
  * The patient dataframe is converted to list as list is faster for comparison
  * The pcr dataframe is converted to dictionary
  * Note that we could decrease the df_patinet from the start, by deleting the records that their patinet_id is not in pcr table. However, in this case we could not correct the typos as we find all the similar records and find the right one by mode function. For example, if there are john, jonh, john, johnn as the name, then mode of these records will be john which corrects the typos.


## Solution 2 (faster) - (not uploaded yet and will be uploaded if interested)
* Using super fast string matching
In this solution the tf-idf, N-Grams and Cosine similarity will be used to match the records (`TfidfVectorizer` and 'csr_matrix' libraries)
