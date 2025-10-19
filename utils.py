from playwright.sync_api import Page
import pandas as pd


def type_word(page: Page, selector: str, word: str) -> None:
    """
    Type word in webpage.

    Parameter:
        page    : Playwright page object.
        selector: CSS selector of the element to type into.
        word    : Text to type.

    Return:
        None.
    """

    page.type(selector, word)
    page.keyboard.press("Enter")


def query(
    df: pd.DataFrame, 
    list_wrong_word: list, 
    list_no_letter: list, 
    list_have_letter: list, 
    list_wrong_pos: list, 
    list_right_pos: list
) -> None:
    """
    Query possible words from dataframe with a given hint.

    Parameter:
        df              : Dataframe containing answer words.
        list_wrong_word : List of words that does not correct.
        list_no_letter  : List of letters that does not present in the quiz.
        list_have_letter: List of letters that present in the quiz.
        list_wrong_pos  : List of letters and positions that is in the wrong spot.
        list_right_pos  : List of letters and positions that is in the right spot.

    Return:
        1 possible word as string.
    """

    # remove duplicate from list
    set_no_letter = set(list_no_letter)
    set_have_letter = set(list_have_letter)

    # filter out intersecting letters of (set_have_letter) in (set_no_letter)
    set_no_letter = set_no_letter - set_have_letter

    # not contain any of words
    if list_wrong_word:
        df = df[~df["word"].isin(list_wrong_word)]

    # not contain any of letters
    if set_no_letter:
        pattern_no_letter = f"[{''.join(letter for letter in set_no_letter)}]"
        df = df[~df["word"].str.contains(pattern_no_letter, regex=True)]

    # contain all letters
    if set_have_letter:
        pattern_have_letter = "".join(f"(?=.*{letter})" for letter in set_have_letter)
        df = df[df["word"].str.contains(pattern_have_letter, regex=True)]

    # filter incorrect position letters
    if list_wrong_pos:
        for i in list_wrong_pos:
            df = df[df[f"l{i[0]}"] != i[-1]]

    # filter correct position letters
    if list_right_pos:
        for i in list_right_pos:
            df = df[df[f"l{i[0]}"] == i[-1]]

    # return None if no possible word matched
    if df.empty:
        return None

    # return 1st matching possible word
    return(df["word"].iloc[0])