import pandas as pd

file_list = ["valid_guesses.csv", "valid_solutions.csv"]

# create column for each letter
for file in file_list:
    df = pd.read_csv(file)
    df[["l1", "l2", "l3", "l4", "l5"]] = df["word"].apply(lambda x: pd.Series(list(x)))

    # save to new csv
    df.to_csv(f"{file.replace('valid_', '')}", index=False)