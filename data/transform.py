import pandas as pd

file_list = ["valid_guesses.csv", "valid_solutions.csv"]

remove_list = ["fifis", "farro", "jeons"]

# transform in both files
for file in file_list:

    # create column for each letter
    df = pd.read_csv(file)
    df[["l1", "l2", "l3", "l4", "l5"]] = df["word"].apply(lambda x: pd.Series(list(x)))

    # remove invalid words
    df = df[~df["word"].isin(remove_list)]

    # save to new csv
    df.to_csv(f"{file.replace('valid_', '')}", index=False)