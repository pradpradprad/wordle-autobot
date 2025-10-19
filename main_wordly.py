from playwright.sync_api import sync_playwright
import pandas as pd
import time
from loguru import logger
from utils import type_word, query


# define variables
df_solution = pd.read_csv("data/solutions.csv")
df_guess = pd.read_csv("data/guesses.csv")
default_word = "audio"
selector_type = "#game-wrapper > div.game_rows"

# input game loop
loop = int(input("Insert total game loop: "))


# main function
def main():
    """
    Main function for playing infinite wordle.

    Parameter:
        None.

    Return:
        None.
    """

    try:
        with sync_playwright() as p:

            # loading browser and website
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            logger.info("===== Loading website =====")
            page.goto("https://wordly.org", timeout=60000*5)

            page.wait_for_load_state("load")
            logger.info("===== Finished loading website =====")
            time.sleep(2)

            correct_guess = 0

            # for each game loop
            for game_number in range(loop):
                logger.info(f"\n\n===== Starting game {game_number+1} =====")

                # reset variables at the start
                guess_word = default_word
                list_wrong_word = []
                list_no_letter = []
                list_have_letter = []
                list_wrong_pos = []
                list_right_pos = []

                # get all rows element
                time.sleep(2)
                rows = page.query_selector_all("div.game_rows > div")

                # loop through each row
                for row in rows:

                    # letter index to reference letter position
                    idx_letter = 1

                    # type a word
                    logger.info(f"Guessing: {guess_word}")
                    type_word(page, selector_type, guess_word)

                    # get result element (wait for 4 seconds)
                    time.sleep(4)
                    result = page.query_selector_all("div.Game > div")
                    result_class = [component.get_attribute("class") for component in result]

                    # check if result window popup after guessing word

                    # if correct
                    if "modal_finish poof active" in result_class:
                        logger.success(f"Correct guessed, word is: {guess_word}")
                        page.keyboard.press("Enter")
                        correct_guess += 1
                        break

                    # if incorrect
                    elif "modal_finish  active" in result_class:

                        # display the correct answer
                        answer = page.query_selector(
                                                    "#root > div > div > div.modal_finish.active > div.data > div > div.word"
                                                ).inner_text().lower()
                        logger.error(f"Wrong guessed, word is: {answer}")
                        page.keyboard.press("Enter")

                        # log to text file
                        with open("wrong_word.txt", "a") as f:
                            f.write(f"Game number: {game_number+1}")
                            f.write(f"\nAnswer: {answer}")
                            f.write(f"\nWrong word: {list_wrong_word}")
                            f.write(f"\nNo letter: {list_no_letter}")
                            f.write(f"\nHave letter: {list_have_letter}")
                            f.write(f"\nWrong position: {list_wrong_pos}")
                            f.write(f"\nRight position: {list_right_pos}")
                            f.write("\n=====\n\n")
                        break

                    # if not finish
                    else:

                        # get letter elements
                        letters = row.query_selector_all("div")

                        # loop through each letter to collect hint as list
                        for letter in letters:

                            # get class name and letter as text
                            class_name = letter.get_attribute("class")
                            text_letter = letter.inner_text().lower()

                            # if letter is in correct position
                            if "correct" in class_name:
                                list_have_letter.append(text_letter)
                                list_right_pos.append(f"{idx_letter}{text_letter}")

                            # if letter is in wrong position
                            elif "elsewhere" in class_name:
                                list_have_letter.append(text_letter)
                                list_wrong_pos.append(f"{idx_letter}{text_letter}")

                            # if letter does not present in answer word
                            else:
                                list_no_letter.append(text_letter)
                            
                            # increase letter index as we move to next position
                            idx_letter += 1

                        # define recently used guess word to compare with next guess word
                        previous_word = guess_word

                        # query possible word from (solutions.csv) dataframe with the given hint lists
                        guess_word = query(
                                        df_solution, 
                                        list_wrong_word, 
                                        list_no_letter, 
                                        list_have_letter, 
                                        list_wrong_pos, 
                                        list_right_pos
                                    )
                        
                        # if it queried same word (which is incorrect guess), we filter out that word and find new one
                        if guess_word == previous_word:

                            list_wrong_word.append(guess_word)
                            guess_word = query(
                                            df_solution, 
                                            list_wrong_word, 
                                            list_no_letter, 
                                            list_have_letter, 
                                            list_wrong_pos, 
                                            list_right_pos
                                        )

                        # change to (guesses.csv) if there is no possible word from (solutions.csv)
                        if not guess_word:
                            second_guess = query(
                                                df_guess, 
                                                list_wrong_word, 
                                                list_no_letter, 
                                                list_have_letter, 
                                                list_wrong_pos, 
                                                list_right_pos
                                            )
                            
                            # if it queried same word (which is incorrect guess), we filter out that word and find new one
                            if second_guess == previous_word:

                                list_wrong_word.append(second_guess)
                                second_guess = query(
                                                    df_guess, 
                                                    list_wrong_word, 
                                                    list_no_letter, 
                                                    list_have_letter, 
                                                    list_wrong_pos, 
                                                    list_right_pos
                                                )

                            # if word does exist
                            if second_guess:
                                logger.info("Word found in guess dataframe")
                                guess_word = second_guess

                            # if there is no possible word from both dataframe, use default word instead
                            else:
                                logger.warning("No word found in both dataframe")
                                guess_word = default_word

            # end of gameplay
            time.sleep(5)
            logger.success(f"Total score: {correct_guess}/{loop}")
            logger.success("===== Finished =====")
            browser.close()

    # catch exceptions
    except Exception as e:
        logger.error(e)
        raise e
    

# run main function
if __name__ == "__main__":
    main()