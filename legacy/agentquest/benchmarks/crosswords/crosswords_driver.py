import json
import random

from agentquest.utils import Observation

cardinals = {
    1: "first",
    2: "second",
    3: "third",
    4: "fourth",
    5: "fifth",
    6: "sixth",
    7: "seventh",
    8: "eighth",
    9: "ninth",
    10: "tenth",
    11: "eleventh",
    12: "twelfth",
    13: "thirteenth",
    14: "fourteenth",
    15: "fifteenth",
    16: "sixteenth",
    17: "seventeenth",
    18: "eighteenth",
    19: "nineteenth",
    20: "twentieth",
    21: "twenty-first",
    22: "twenty-second",
    23: "twenty-third",
    24: "twenty-fourth",
    25: "twenty-fifth",
    26: "twenty-sixth",
    27: "twenty-seventh",
    28: "twenty-eighth",
    29: "twenty-ninth",
    30: "thirtieth",
}


class CrosswordsDriver:
    def __init__(self, game):
        self.game = game["clue"]
        self.answer = game["answer"].lower()
        self.split_answer = [x for x in self.answer]
        self.hints = game["hints"]
        self.sequence = game["sequence"]
        self.past_guesses = []
        self.provided_hints = []

    @classmethod
    def generate_json_structure(cls, word):
        # Create the basic structure
        structure = {"clue": "", "answer": word, "hints": [], "sequence": []}

        # Generate hints
        structure["hints"].append(f"The word starts with letter: {word[0]}")
        for i in range(1, len(word) - 1):
            structure["hints"].append(f"The letter at position {i + 1} is {word[i]}")
        structure["hints"].append(f"The word ends with letter: {word[-1]}")

        # Generate random sequence
        structure["sequence"] = list(range(len(word)))
        random.shuffle(structure["sequence"])

        # Convert to JSON
        json_structure = json.dumps(structure, indent=2)

        return json_structure

    def reset(self):
        # Reset your environment status here.
        word_len = len(self.answer)

        # Instantiate your initial observation from the environment
        # obs = Observation(
        #    output=f'Guess a {word_len} letters word whose definition is \'{self.game}\'',
        #    done=False
        # )
        obs = Observation(output=f"Guess a {word_len} letters word", done=False)
        obs.repetition_rate = 0.0
        obs.provided_hints = 0
        obs.followed_hints = 0

        return obs

    def count_followed_hints(self, guess):
        followed_hints = 0
        for hint in set(self.provided_hints):
            # Number of letters
            if hint.split(" ")[2] == "word":
                if len(guess) == len(self.split_answer):
                    followed_hints += 1

            # Starting letter
            elif hint.split(" ")[2] == "starts":
                letter = hint.split(" ")[-1]
                if guess[0] == letter:
                    followed_hints += 1

            # Ending letter
            elif hint.split(" ")[2] == "ends":
                letter = hint.split(" ")[-1]
                if guess[-1] == letter:
                    followed_hints += 1

            elif hint.split(" ")[1] == "letter":
                position = int(hint.split(" ")[4]) - 1
                letter = hint.split(" ")[-1]
                if (
                    len(guess) > position
                ):  # TODO bugfix, verify if this is the bug! RB: Yes, it should be > not >=
                    if guess[position] == letter:
                        followed_hints += 1
        return followed_hints

    def check_correct(self, guess: list, truth: list):
        msg = "You won!"
        # Check the length of the guess
        if len(guess) != len(truth):
            msg = f"Wrong! The word to guess has {len(truth)} letters."
            self.provided_hints.append(msg)
        else:
            for hint_id in self.sequence:
                hint = self.hints[hint_id]

                if guess[hint_id] != truth[hint_id]:
                    self.provided_hints.append(hint)
                    if hint.split(" ")[1] == "letter":
                        position = int(hint.split(" ")[4])
                        new_position = cardinals[position]
                        hint = hint.replace(
                            f"at position {position}", f"in {new_position} position"
                        )
                    msg = f"Wrong! {hint}"
                    break
        if msg == "You won!" and "".join(guess) != self.answer:
            msg = "Wrong! Try another guess"
        return msg

    def step(self, action):
        action = action.action_value  # Retrieve the action value
        self.past_guesses.append(action.lower())
        # Process your action here
        split_guess = [x for x in str(action.lower())]

        msg = self.check_correct(split_guess, self.split_answer)

        if msg == "You won!":
            done = True
        else:
            done = False

        repetition_rate = 1 - len(set(self.past_guesses)) / len(self.past_guesses)

        # Instantiate your current observation from the environment
        obs = Observation(
            output=msg,
            done=done,
        )
        obs.repetition_rate = repetition_rate
        obs.provided_hints = len(set(self.provided_hints))
        obs.followed_hints = self.count_followed_hints(split_guess)
        obs.progress = len(set(split_guess).intersection(self.split_answer)) / len(
            self.split_answer
        )

        return obs
