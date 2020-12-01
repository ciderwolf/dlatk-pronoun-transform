import pandas as pd

PRONOUNS = [
    ("himself", "herself", "themselves"),
    ("him", "her", "them"),
    ("his", "hers", "theirs"),
    ("his", "her", "their"),
    ("he", "she", "they"),
    ("man", "woman", "person"),
    ("men", "women", "people"),
    ("boys", "girls", "children"),
    ("boy", "girl", "child"),
    ("sons", "daughters", "children"),
    ("son", "daughter", "child"),
    ("brother", "sister", "sibling"),
    ("brothers", "sisters", "siblings"),
]
MALE = 0
FEMALE = 1
NEUTRAL = 2


def gender_name_to_id(name: str) -> int:
    """
    Convert a gender name to its corresponding index.

    Parameters
    ----------
    name
        The gender name to be converted.

    Returns
    -------
    An int corresponding to the correct index in the pronoun lookup table.
    """
    if name.lower() == "male":
        return MALE
    elif name.lower() == "female":
        return FEMALE
    else:
        return NEUTRAL


def replace_pronouns(token: str, from_gender: int, to_gender: int) -> str:
    """
    Check the given token against each row of the look up table, and transform
    it if it matches any row.

    Parameters
    ----------
    token
        The string to be transformed
    from_gender
        The index in the lookup table to check the token agains
    to_gender
        If the token matches an entry in the lookup table, return the
        corresponding entry in the to_gender index.

    Returns
    -------
    The token, transformed if it matched any row in the lookup table, unchanged
    otherwise.
    """
    for pronoun_group in PRONOUNS:
        if pronoun_group[from_gender] == token:
            return pronoun_group[to_gender]
    return token


def swap_pronouns(token: str, a_gender: int, b_gender: int) -> str:
    """
    The same as `replace_pronouns`, except instead of transforming from
    `from_gender` to `to_gender`, this function swaps any pronoun between
    `a_gender` and `b_gender`. See `replace_pronouns` for more details.
    """
    for pronoun_group in PRONOUNS:
        if pronoun_group[a_gender] == token:
            return pronoun_group[b_gender]
        elif pronoun_group[b_gender] == token:
            return pronoun_group[a_gender]

    return token


def remap_df(df: pd.DataFrame, from_gender: int, to_gender: int) -> pd.DataFrame:
    """
    Take a DataFrame and transform all of the pronouns in the `feat` column with
    the genders as specified.

    Parameters
    ----------
    df
        The DataFrame with tokens to be transformed. This must have a `feat`
        column.
    from_gender, to_gender
        See `replace_pronouns` for more details.

    Returns
    -------
    The transformed DataFrame.
    """
    remapped_messages = df["feat"].apply(
        lambda feat: replace_pronouns(feat, from_gender, to_gender)
    )
    df["feat"] = remapped_messages
    return df
