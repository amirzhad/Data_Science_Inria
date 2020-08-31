# Version française

# Test technique de science des données pour l'INRIA

## Contenu du référentiel

* `ds_inria_main.ipynb`
* Données: 1 fichier en sql (2 tables existent: la table patient et la table pcr)


## Directives de test

Dans ce test, nous avons deux tableaux: les informations du patient (ID, nom, famille, adresse, etc.) et le test pcr (ID et pcr). Le tableau pcr indique si un ID est COVID positif ou négatif.
La tâche est de trouver les doublons en considérant qu'il pourrait y avoir des fautes de frappe dans les données. En outre, visualiser les cas positifs regroupés par âge et emplacement géographique.
Il n'y a pas de contrainte dans les bibliothèques python.

## Solution 1
Pour résoudre ce problème, nous vérifions d'abord les dataframes et les nettoyons.

J'ai vérifié les données pour trouver de simples doublons. J'ai également vérifié chaque colonne et ligne de données pour vérifier les mauvaises entrées de données. (J'ai ignoré les mettre dans le code soumis). J'ai créé ce code pour l'ensemble de données actuellement disponibles.

Nous trouvons le conflit, les doublons et les identifiants erronés pour pcr dataframe:
* identifiant de conflit: si l'identifiant dupliqué a une valeur pcr différente
* identifiant en double: si l'identifiant est répété plus d'une fois
* faux id: les identifiants qui ne sont pas numériques

Ensuite, nous faisons la même chose pour le dataframe patient:
* identifiant de conflit: si l'identifiant dupliqué est lié à différents patients
* duplicate id: si un même enregistrement avec le même id est répété
* enregistrement en double: si un enregistrement est répété plus d'une fois
* faux identifiant: nous avons vérifié et trouvé aucun identifiant erroné dans le dataframe du patient (donc pas besoin de considérer)

Afin de trouver les enregistrements dupliqués, la similitude floue est utilisée. En fait, chacun des enregistrements est comparé à d'autres dans la base de données patient et si leur similitude est suffisamment élevée (ici nous avons considéré une similitude> 90%), nous les considérons et les convertissons comme un seul enregistrement.

Cette bibliothèque fonctionne très bien pour les chaînes et peut correspondre aux fautes de frappe. Cependant, la vitesse des dataframes est le problème. Afin d'accélérer la tâche, nous avons effectué ces étapes:
* Utilisation de la bibliothèque `rapidfuzz` au lieu de` fuzzywuzzy` (le résultat est le même mais cela accélère la tâche)
* Convertissez les dataframes en liste ou en tableau:
  * Le dataframe patient est converti en liste car la liste est plus rapide pour la comparaison
  * Le dataframe pcr est converti en dictionnaire
  * Notez que nous pourrions diminuer le df_patinet depuis le début, en supprimant les enregistrements dont le patinet_id n'est pas dans la table pcr. Cependant, dans ce cas, nous n'avons pas pu corriger les fautes de frappe car nous trouvons tous les enregistrements similaires et trouvons le bon par la fonction de mode. Par exemple, s'il y a john, jonh, john, johnn comme nom, alors le mode de ces enregistrements sera john qui corrige les fautes de frappe.

## Solution 2 (plus rapide) - (pas encore téléchargé et sera téléchargé si vous êtes intéressé)
* Utilisation de la correspondance de chaînes super rapide
Dans cette solution, la similitude tf-idf, N-Grams et Cosine sera utilisée pour faire correspondre les enregistrements (bibliothèques `TfidfVectorizer` et 'csr_matrix')

###########

# English Version
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

I did some data checking to find simple duplicates. I also, checked each column and row of the data to check the wrong data inputs. (I ignored putting them in submitted code). I made this code for current available data-set.

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
