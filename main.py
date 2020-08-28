# The imports
import pandas as pd
from sqlalchemy import create_engine
# from fuzzywuzzy import fuzz
from rapidfuzz import fuzz
from collections import Counter
import numpy as np

### constant values --------------
thr_similarity = 90


# ******************************************************

### The functions ---------------

def mostCommon(lst):
    # this function returns the most common values (of each column) in a list of lists
    return [Counter(col).most_common(1)[0][0] for col in zip(*lst)]

# *******************************************************
def is_same(r1, r2):
    # this function takes two records and return true if they are similar
    # similarity: using the NLP (Fuzzy string matching)

    return fuzz.token_sort_ratio(r1, r2) > thr_similarity

# *******************************************************

def detect_duplicates(df_p, df_pcr):
    # this function takes a dataframe as a parameter and returns a new dataframe after removing the duplicates

    # adding a column, indicating if this record is checked or not
    df_p['checked'] = False

    # convert to list and dict
    list_df_patient = df_patient.astype(str).values.tolist()
    dict_df_pcr = df_pcr.set_index('patient_id')['pcr'].to_dict()

    new_df = pd.DataFrame(columns=df_patient.columns)
    new_df['pcr'] = ''

    for index in range(0, len(list_df_patient)):
        #if not index % 1000:  ###### delete later
        print(index)

        # if it was checked before
        if list_df_patient[index][-1] == 'True':
            continue

        # we check this record
        list_df_patient[index][-1] = 'True'

        r1 = list_df_patient[index]

        # create a temporary dataframe containing all similar records with r1
        df_tmp = [r1]

        # creating a list containing the ID ('patient_id') of all similar records
        l_patient_id = [list_df_patient[index][0]]

        # for index2, r2 in df_p.iterrows():
        for index2 in range(index + 1, len(list_df_patient)):

            # if it was checked before
            if list_df_patient[index2][-1] == 'True':
                continue

            r2 = list_df_patient[index2]

            # if r1 and r2 are similar
            if is_same(str(list_df_patient[index][1:]), str(list_df_patient[index2][1:])):
                # we check this record
                list_df_patient[index2][-1] = 'True'

                # add the ID to the list
                l_patient_id.append(list_df_patient[index2][0])

                # add r2 to df_tmp
                df_tmp.append(r2)

        # find the true pcr value for current record (from pcr data)
        list_found_pcr = [dict_df_pcr.get(int(x)) for x in l_patient_id if dict_df_pcr.get(int(x))]
        if not list_found_pcr:  # if there is no pcr for the patient_id
            pcr = 'NaN'
            patient_id = l_patient_id[0]
        else:
            pcr = max(set(list_found_pcr), key=list_found_pcr.count)
            patient_id = [x for x in l_patient_id if dict_df_pcr.get(int(x)) == pcr][0]

        # now from all similar record, pick the most common one and replace it with r1 (delete r1 and add the most common one)
        adding_data = pd.DataFrame(df_tmp, columns=df_p.columns)
        adding_data = adding_data.mode().iloc[0, :]
        adding_data['pcr'] = pcr
        adding_data['patient_id'] = int(patient_id)

        new_df = new_df.append(adding_data)

    new_df = new_df.drop(columns=['checked'])
    new_df = new_df.reset_index(drop=True)
    return new_df

# *******************************************************
# *******************************************************
### Main code start from here ---------------

# reading the dataframes
engine = create_engine('sqlite:///data.db', echo=False)
con = engine.connect()
df_patient = pd.read_sql('select * from patient', con=con)
df_pcr = pd.read_sql('select * from test', con=con)
con.close()

# converting N to Negative (and P to Positive) in df_pcr dataframe
df_pcr[df_pcr['pcr']=='N'] = 'Negative'
df_pcr[df_pcr['pcr']=='P'] = 'Positive'

# check if df_pcr have all correct patient_id (should be numeric)
df_pcr.patient_id.astype(str).str.isnumeric().all()
# so we have some wrong id in df_pcr

# keeping the initial total size of the dataframes
total_size_pcr = len(df_pcr)
total_size_patient = len(df_patient)

# initial patient_id
patient_ids = df_patient['patient_id']

# clean df_pcr from string patient_id
num_of_bad_p_id_pcr = len(df_pcr[~df_pcr.patient_id.astype(str).str.isnumeric()])

# clean df_pcr from bad id
df_pcr = df_pcr[df_pcr.patient_id.astype(str).str.isnumeric()]

# finding the duplicated patient_id in df_pcr and checking if they have same pcr or not
# add the id to conflict list (of pcr) if the pcr values are not same
p_id_conflict_pcr = []
df_pcr_dup_id = df_pcr[(df_pcr.duplicated(subset='patient_id'))]['patient_id']
for p_id in df_pcr_dup_id.values:
    tmp = df_pcr[df_pcr['patient_id'] == p_id]
    if (not tmp.empty) and (tmp.pcr.nunique() > 1):
        p_id_conflict_pcr.append(p_id)

# subtracting the conflict ids from dublicated id
df_pcr_dup_id = df_pcr_dup_id[~df_pcr_dup_id.isin(p_id_conflict_pcr)]

# we drop the conflicted patient_id
df_pcr = df_pcr.drop(df_pcr[df_pcr.patient_id.isin(p_id_conflict_pcr)].index)
# drop one of the duplicated patient_id (we keep one)
df_pcr = df_pcr.drop_duplicates(subset='patient_id')

# finding the duplicated patient_id in df_patient and checking if they are for same patient or not
# add the id to conflict list (of patient) if the patient are not same
p_id_conflict_patient = []
df_patient_dup_id = df_patient[(df_patient.duplicated(subset='patient_id'))]['patient_id']
for p_id in df_patient_dup_id.values:
    tmp = df_patient[df_patient['patient_id'] == p_id]

    r1 = str(tmp.values[0, 1:])
    for i in range(1, len(tmp)):
        r2 = str(tmp.values[i, 1:])
        if not is_same(r1, r2):
            p_id_conflict_patient.append(p_id)
            break

# subtracting the conflict ids from dublicated id
df_patient_dup_id = df_patient_dup_id[~df_patient_dup_id.isin(p_id_conflict_patient)]

# we drop the conflicted patient_id
df_patient = df_patient.drop(df_patient[df_patient.patient_id.isin(p_id_conflict_patient)].index)
num_conflict_duplicated_records = total_size_patient - len(df_patient)

# no need to drop duplicate id because there is no duplicate patient_id
# instead, we find and drop the duplicated records (considering the typos)

# finding and cleaning the duplicates from patient dataframe
df_patient_cleaned = detect_duplicates(df_patient, df_pcr)
# this function takes time so feel free to take a coffee (for me it takes about 2h)

# information of this data
total_dup_records_df_patient = len(df_patient)-len(df_patient_cleaned)
total_records_with_pcr = len(df_patient_cleaned[df_patient_cleaned.pcr != 'NaN'])
total_positives = len(df_patient_cleaned[df_patient_cleaned.pcr == 'Positive'])
total_negatives = len(df_patient_cleaned[df_patient_cleaned.pcr == 'Negative'])
positive_percentage = total_positives * 100 / total_records_with_pcr
negative_percentage = total_negatives * 100 / total_records_with_pcr

print('Total number of records in df_patient: ', total_size_patient)
print('Total number of records in df_pcr: ', total_size_pcr)

print('Total number of conflict duplicated patient_id in df_patient (the duplicated id with different patient) : ', len(p_id_conflict_patient))
print('Total number of conflict duplicated records in df_patient: ', num_conflict_duplicated_records)
print('Total number of duplicate records in df_patient (with typos): ', total_dup_records_df_patient)
print('Total number of records in df_patient which have pcr lable (after cleaning): ', total_records_with_pcr)

print('Total number of wrong records in df_pcr (bad patient_id) : ', num_of_bad_p_id_pcr)
print('Total number of conflict duplicated patient_id in df_pcr (the duplicated id with different pcr value) : ', len(p_id_conflict_pcr))
print('Total number of duplicated records in df_pcr : ', len(df_pcr_dup_id))

print('Total number of positive cases: ', total_positives)
print('percentage of positive cases: %.2f%%'% positive_percentage)

print('Total number of negative cases: ', total_negatives)
print('percentage of negative cases: %.2f%%'% negative_percentage)

# The conflicted ids in patient DataFrame
print(p_id_conflict_patient)

# The duplicated ids in patient DataFrame
patient_id_cleaned = df_patient_cleaned['patient_id']
id_dup_records = patient_ids[~patient_ids.isin(patient_id_cleaned)]
id_dup_records = patient_ids[~patient_ids.isin(p_id_conflict_patient)]
print(id_dup_records)

# changing the type of the columns (because we used list, they are all changed to object)
df_patient_cleaned = df_patient_cleaned.astype({"age": float, "street_number":float, "patient_id":np.int64, "date_of_birth": float})
df_patient_cleaned["state"].replace({"None": float('NaN')}, inplace=True)

### visualize the statistics

# number of patients positive for Covid19 by age
ax = df_patient_cleaned['age'].value_counts().plot(kind='bar', figsize=(15,5))
ax.set_xlabel("The Ages")
ax.set_ylabel("Number of positives")

# number of patients positive for Covid19 by state (geographical location)
ax = df_patient_cleaned['state'].value_counts().nlargest(10).plot(kind='bar', figsize=(15,5))
ax.set_xlabel("The State")
ax.set_ylabel("The number of positives")

