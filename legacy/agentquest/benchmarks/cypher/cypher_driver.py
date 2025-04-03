from agentquest.utils import Observation


class CypherDriver:
    def __init__(self, game):
        self.game = game["clue"]
        self.answer = game["answer"].lower()
        self.split_answer = [x for x in self.answer]
        self.hints = game["hints"]
        self.sequence = game["sequence"]
        self.no_sub = game["no_sub"].lower()
        self.past_guesses = []
        self.provided_hints = []

    @classmethod
    def generate_json_structure(cls, word):
        # This is to develop an automatic ways to generate data! Would do it later!
        return word

    def reset(self):
        # Reset your environment status here.
        word_len = len(self.answer)

        # Instantiate your initial observation from the environment
        obs = Observation(
            output=f"Decode a cyphered {word_len} letters word: {self.game}", done=False
        )
        obs.repetition_rate = 0.0
        obs.provided_hints = 0
        obs.followed_hints = 0

        return obs

    @staticmethod
    def verify_shift_steps_both_directions(string1, string2, step):
        # Check if the lengths of the two words are the same
        if len(string1) != len(string2):
            return False

        # Verify that each character is shifted by the specified number of steps
        for i in range(len(string1)):
            # Calculate the expected characters for both right and left shifts
            expected_right_char = chr(
                (ord(string1[i]) - ord("a") + step) % 26 + ord("a")
            )
            expected_left_char = chr(
                (ord(string1[i]) - ord("a") - step) % 26 + ord("a")
            )

            # Check if either expected character matches the shifted character
            if string2[i] != expected_right_char and string2[i] != expected_left_char:
                return False
        return True

    @staticmethod
    def verify_shift_direction(string1, string2, direction, max_step=5):
        # Check if the lengths of the two strings are the same
        if len(string1) != len(string2):
            return False, None

        # Calculate the initial shift based on the direction
        if direction == "right":
            initial_shift = (ord(string2[0]) - ord(string1[0])) % 26
        elif direction == "left":
            initial_shift = (ord(string1[0]) - ord(string2[0])) % 26
        else:
            return False, None

        # Normalize the shift to the range [-26, 26]
        if initial_shift > 13:
            initial_shift -= 26

        # Check if the shift is within the allowed range [-max_step, max_step]
        if not -max_step <= initial_shift <= max_step:
            return False, initial_shift

        # Verify that each subsequent pair of characters has the same shift
        for i in range(1, len(string1)):
            if direction == "right":
                current_shift = (ord(string2[i]) - ord(string1[i])) % 26
            elif direction == "left":
                current_shift = (ord(string1[i]) - ord(string2[i])) % 26

            if current_shift > 13:
                current_shift -= 26

            if current_shift != initial_shift:
                return False, current_shift

        # Return True and the shift if everything is consistent
        return True, initial_shift

    @staticmethod
    def verify_substitution(string1, string2, original_char, substituted_char):
        # Check if the lengths of the two strings are the same
        if len(string1) != len(string2):
            return False

        # Verify that each specified character is substituted correctly
        for i in range(len(string1)):
            if string1[i] == original_char:
                if string2[i] != substituted_char:
                    return False
            else:
                if string1[i] != string2[i]:
                    return False

        return True

    def count_followed_hints(self, guess):
        followed_hints = 0
        for hint in set(self.provided_hints):
            guess = "".join(guess).lower()
            print(guess, self.no_sub, self.answer)
            # Number of letters
            if hint.split(" ")[2] == "word":
                if len(guess) == len(self.split_answer):
                    followed_hints += 1

            # shift step
            elif hint.split(" ")[2] == "step":
                moves = int(hint.split(" ")[-1])
                print(guess, self.no_sub, moves)
                if self.verify_shift_steps_both_directions(guess, self.no_sub, moves):
                    followed_hints += 1

            # shift direction
            elif hint.split(" ")[2] == "direction":
                direction = hint.split(" ")[-1]
                verify_direction, move_step = self.verify_shift_direction(
                    guess, self.no_sub, direction
                )
                if verify_direction:
                    followed_hints += 1

            # sub
            elif hint.split(" ")[1] == "substitution":
                orig_char = hint.split(" ")[-3]
                sub_char = hint.split(" ")[-1]
                if self.verify_substitution(guess, self.answer, orig_char, sub_char):
                    followed_hints += 1

            # start letter
            elif hint.split(" ")[2] == "starts":
                letter = hint.split(" ")[-1]
                if guess[0] == letter:
                    followed_hints += 1

            # end letter
            elif hint.split(" ")[2] == "ends":
                letter = hint.split(" ")[-1]
                if guess[-1] == letter:
                    followed_hints += 1
        return followed_hints

    def check_correct(self, guess: list, truth: list):
        msg = "You won!"
        # Check the length of the guess
        print(f"guess: {guess}, truth: {truth}")
        if len(guess) != len(truth):
            msg = f"Wrong! The word to guess has {len(truth)} letters."
            self.provided_hints.append(msg)
        else:
            for hint_id in self.sequence:
                hint = self.hints[hint_id]

                if "".join(guess) != "".join(truth):
                    self.provided_hints.append(hint)
                    msg = f"Wrong! {hint}"
                    if "step" in hint:
                        msg += f" from the cyphered word: {self.game}"
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
