# DLATK Pronoun Swapper

A set of utility scripts which work with DLATK to measure the difference in lexicon scores after swapping the gender of pronouns in tweets.

## Setup

These scripts expect to be run on `ssh.wwbp.org`. Specifically, they expect that 
 - `dlatkInterface.py` is located in your home directory
 - Your MySQL credentials are in a file named `.my.cnf` in your home directory, with contents as follows:
```ini
[client]
user=<your-username>
password=<your-password>
...
```
You should run the scripts in the `dlatk` conda environment, which contains all of the necessary dependencies. Activate it with:
```
source activate dlatk
```

### Prerequisites

The scripts make several assumptions about what exists in your MySQL environment. 
 - The scripts attempt to connect to a database named `politeness`
 - This database should have a table named `twitter`, which contains the messages to be analyzed. 
 - A 1-gram table generated with `dlatk` named `feat$1gram$twitter$sid$16to16` is expected, along with a LIWC lexicon table named `feat$cat_LIWC2015_w$twitter$sid$1gra`. 
 - The scores of the transformed messages will be computed with a data-driven lexicon named `dd_twitter_politeness`.

## Running the pipeline

```bash
python pronoun_transformation_pipeline.py <operation> <from_gender> <to_gender>
```

 - `from_gender` and `to_gender` specify what pronoun genders should be replaced, and what gender they should be replaced with. They should each be one of `male`, `female`, or `neutral`.
 - `operation` will be used to name the created SQL tables, and the output csv file. Choose something which denotes the type of transformation being performed.

The script will create an output csv file named `twitter_<operation>_scores.csv` with four columns:
 - `id`: The id of the tweet being transformed
 - `original_score`: The lexicon-predicted score of the original tweet.
 - `transformed_score`: The lexicon-predicted score of the transformed tweet.
 - `score_difference`: Equal to `original_score - transformed_score`. If this value is positive, the transformation decreased the predicted score, and if it's negative, the transformation increased the predicted score.



## Results
Each of the following gender swaps resulted in the corresponding `score_difference` averaged across all 391 tweets with a token in the LIWC `PRONOUN` and `SHEHE` categories. *(negative difference corresponds to an increase in score, and a positive difference is a decrease)*

 - `male->female`: `0.023583`
 - `female->male`: `-0.017585`
 - `male->neutral`: `0.00120`
 - `female->neutral`: `-0.01650`
