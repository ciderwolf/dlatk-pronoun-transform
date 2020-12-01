import os
import pandas as pd
from sys import argv
from get_engine import engine_from_config
from swap_gender_pronouns import remap_df, gender_name_to_id

# Change this prefix if your base table isn't named `twitter`.
TABLE_NAME = "twitter_"


def create_base_table():
    """
    Create a base messages table with ids of the messages to be analyzed.
    This table doesn't require any information about the messages themselves, so
    it contains only the ids.
    """
    engine = engine_from_config()
    if TABLE_NAME in engine.table_names():
        print(TABLE_NAME, "already exists! Skipping creation...")
        return
    with engine.connect() as conn:
        conn.execute(
            """CREATE TABLE {} AS
            SELECT feat$cat_LIWC2015_w$twitter$sid$1gra.group_id AS "sid"
            FROM feat$cat_LIWC2015_w$twitter$sid$1gra
            WHERE feat$cat_LIWC2015_w$twitter$sid$1gra.feat='SHEHE';""".format(
                TABLE_NAME
            )
        )


def transform_1grams(gender_from_name: str, gender_to_name: str) -> pd.DataFrame:
    """
    Collect all of the 1-grams from the messages to be analyzed, and perform the
    specified gender swaps.

    Parameters
    ----------
    gender_from_name
        The name of the gender whose pronouns will be replaced
    gender_to_name
        The name of the target gender for the replaced pronouns

    Returns
    -------
    A pandas DataFrame which contains the 1-gram table with the `feat` column
    containing the transformed pronouns.
    """
    engine = engine_from_config()
    with engine.connect() as conn:
        df = pd.read_sql(
            """SELECT feat$1gram$twitter$sid$16to16.*
            FROM feat$1gram$twitter$sid$16to16 INNER JOIN feat$cat_LIWC2015_w$twitter$sid$1gra
            ON feat$1gram$twitter$sid$16to16.group_id=feat$cat_LIWC2015_w$twitter$sid$1gra.group_id
            WHERE feat$cat_LIWC2015_w$twitter$sid$1gra.feat='SHEHE';""",
            conn,
        )

    df = remap_df(
        df, gender_name_to_id(gender_from_name), gender_name_to_id(gender_to_name)
    )
    return df


def calculate_transformed_scores(transformed_df: pd.DataFrame):
    """
    Create a 1-gram table from the `transformed_df`, and runs dlatk to compute
    lexicon scores on the transformed messages.

    Parameters
    ----------
    transformed_df
        A DataFrame which contains the 1-grams to be analyzed with the lexicon.
        This should be the output of `transform_1grams`.
    """
    engine = engine_from_config()
    # Upload 1grams to table
    with engine.connect() as conn:
        table_name = "feat$1gram${table_name}$sid$16to16".format(table_name=TABLE_NAME)
        transformed_df.to_sql(table_name, conn, index=False, if_exists="replace")

    # Use dlatk to create lex table
    # TODO: Call dlatk from python?
    dlatk_command = "~/dlatkInterface.py -d politeness -t {table_name} -c sid --add_lex_table -l dd_twitter_politeness --weighted_lexicon".format(
        table_name=TABLE_NAME
    )
    os.system(dlatk_command)


def compare_transform_effect():
    """
    Select the message id, the lexicon-predicted scores of the original message,
    and the lexicon-predicted scores of the transformed message. Compute the
    difference between the original and transformed scores, and save the whole
    DataFrame to a csv file.
    """
    sql = """SELECT feat$cat_dd_twitter_politeness_w$twitter$sid$1gra.group_id AS 'id',
    feat$cat_dd_twitter_politeness_w$twitter$sid$1gra.group_norm AS 'original_score',
    feat$cat_dd_twitter_politeness_w${table_name}$sid$1gra.group_norm AS 'transformed_score'
    FROM feat$cat_dd_twitter_politeness_w$twitter$sid$1gra INNER JOIN feat$cat_dd_twitter_politeness_w${table_name}$sid$1gra
    ON feat$cat_dd_twitter_politeness_w$twitter$sid$1gra.group_id=feat$cat_dd_twitter_politeness_w${table_name}$sid$1gra.group_id""".format(
        table_name=TABLE_NAME
    )
    engine = engine_from_config()
    with engine.connect() as conn:
        df = pd.read_sql(sql, conn)
        df["score_difference"] = df["original_score"] - df["transformed_score"]
        df.to_csv(
            "twitter_{operation}_scores.csv".format(operation=operation), index=False
        )
        return df["score_difference"].sum() / len(df["score_difference"])


if __name__ == "__main__":
    if len(argv) != 4:
        raise ValueError(
            "Expected 3 command line arguments. See README.md for usage details."
        )

    operation = argv[1]
    TABLE_NAME += operation
    gender_from_name = argv[2]
    gender_to_name = argv[3]

    create_base_table()
    transformed = transform_1grams(gender_from_name, gender_to_name)
    calculate_transformed_scores(transformed)
    diff = compare_transform_effect()

    print("The average score difference was ", diff)
