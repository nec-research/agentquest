import random


class ADFGVX:
    @staticmethod
    def get_initial_instructions():
        """
        Displays instructions for how to use the ADFGVX cipher class.
        """
        instructions = (
            "You are a deciphering agent. Your task is to decipher a ciphertext produced from an ADFGVX cipher. The ADFGVX cipher is a combination of a Polybius square substitution cipher and a columnar transposition cipher. "
            "The cipher uses a 6x6 Polybius square constructed from a keyword, containing letters A-Z and digits 0-9. Any other characters like space or period or so on are not taken into account and stripped away from plaintext."
            "Each letter or digit is replaced by its coordinates in the square using the row and column identifiers (A, D, F, G, V, X). "
            "The resulting sequence of coordinates is then permuted according to a transposition key."
        )
        return instructions

    @staticmethod
    def generate_random_parameters() -> dict:
        """
        Method to generate random parameters for an encryption.

        Returns:
            dict: Dictionary with keys "key" and "grid_key".
        """
        # Generate a random alphabetic key for the substitution grid
        alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        key = "".join(random.sample(alphabet, 36))

        # Generate a random keyword for transposition
        keywords = ["CIPHER", "SECRET", "ENCODE", "DECODE", "CRYPTO"]
        grid_key = random.choice(keywords)

        return {"key": key, "grid_key": grid_key}

    @staticmethod
    def _create_substitution_grid(key: str) -> dict:
        """
        Creates a substitution grid using the given key.

        Args:
            key (str): 36-character key for grid creation.

        Returns:
            dict: Mapping of characters to their ADFGVX codes.
        """
        # Ensure key has 36 unique characters
        key = "".join(dict.fromkeys(key.upper()))[:36]

        # Create grid mapping
        grid_mapping = {}
        adfgvx_chars = "ADFGVX"

        for i, char in enumerate(key):
            row = adfgvx_chars[i // 6]
            col = adfgvx_chars[i % 6]
            grid_mapping[char] = row + col
        return grid_mapping

    @staticmethod
    def _create_reverse_grid(grid_mapping: dict) -> dict:
        """
        Creates a reverse mapping for decryption.

        Args:
            grid_mapping (dict): Original substitution grid mapping.

        Returns:
            dict: Reverse mapping of ADFGVX codes to characters.
        """
        return {v: k for k, v in grid_mapping.items()}

    @staticmethod
    def _columnar_transposition(message: str, grid_key: str) -> str:
        """
        Performs columnar transposition on the message.

        Args:
            message (str): Message to be transposed.
            grid_key (str): Keyword for transposition.

        Returns:
            str: Transposed message.
        """
        # Sort the grid key to determine column order
        sorted_key = sorted(enumerate(grid_key), key=lambda x: x[1])
        column_order = [x[0] for x in sorted_key]

        # Pad the message to make it divisible by key length
        padding_length = (
            len(grid_key) - (len(message) % len(grid_key))
            if len(message) % len(grid_key) != 0
            else 0
        )
        padded_message = message + "X" * padding_length

        # Create columns
        columns = [padded_message[i :: len(grid_key)] for i in range(len(grid_key))]
        # Rearrange columns
        rearranged_columns = [columns[column_order[i]] for i in range(len(grid_key))]
        return "".join(rearranged_columns)

    @staticmethod
    def encrypt(key: str, grid_key: str, plain_text: str) -> str:
        """
        Encrypts a plain text message using the ADFGVX cipher.

        Args:
            key (str): 36-character substitution key.
            grid_key (str): Keyword for transposition.
            plain_text (str): The message to encrypt.

        Returns:
            str: The encrypted message.
        """
        # Create substitution grid
        grid_mapping = ADFGVX._create_substitution_grid(key)

        # First, substitute each character
        substituted_text = ""
        for char in plain_text.upper():
            if char in "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789":
                substituted_text += grid_mapping.get(char, "")

        # Then, perform columnar transposition
        return ADFGVX._columnar_transposition(substituted_text, grid_key)

    @staticmethod
    def decrypt(key: str, grid_key: str, cipher_text: str) -> str:
        """
        Decrypts a cipher text message using the ADFGVX cipher.

        Args:
            key (str): 36-character substitution key.
            grid_key (str): Keyword for transposition.
            cipher_text (str): The encrypted message to decrypt.

        Returns:
            str: The decrypted message.
        """
        # Reverse the columnar transposition
        sorted_key = sorted(enumerate(grid_key), key=lambda x: x[1])
        column_order = [x[0] for x in sorted_key]

        # Calculate column lengths
        total_length = len(cipher_text)
        col_lengths = [
            total_length // len(grid_key)
            + (1 if i < total_length % len(grid_key) else 0)
            for i in range(len(grid_key))
        ]

        # Reconstruct the original columnar arrangement
        columns = [0] * len(grid_key)
        current_index = 0
        for i in column_order:
            columns[i] = cipher_text[current_index : current_index + col_lengths[i]]
            current_index += col_lengths[i]
        # Reconstruct the original message
        transposed_text = "".join(["".join(col) for col in zip(*columns)])

        # Create reverse grid for decryption
        grid_mapping = ADFGVX._create_substitution_grid(key)
        reverse_grid = ADFGVX._create_reverse_grid(grid_mapping)

        # Substitute back to original characters
        decrypted_text = ""
        for i in range(0, len(transposed_text), 2):
            code = transposed_text[i : i + 2]
            decrypted_text += reverse_grid.get(code, "")

        return decrypted_text


# if __name__ == "__main__":
#     # Generate random parameters
#     params = ADFGVX.generate_random_parameters()

#     # Encrypt a message
#     plain_text = "HELLO WORLD"
#     cipher_text = ADFGVX.encrypt(params["key"], params["grid_key"], plain_text)
#     # cipher_text = ADFGVX.encrypt(
#     #     "NA1C3H8TB2OME5WRPD4F6G7I9J0KLQSUVXYZ", "PRIVACY", "attack at 1200am"
#     # )
#     print(cipher_text)

#     # Decrypt the message
#     decrypted_text = ADFGVX.decrypt(params["key"], params["grid_key"], cipher_text)
#     # decrypted_text = ADFGVX.decrypt(
#     #     "NA1C3H8TB2OME5WRPD4F6G7I9J0KLQSUVXYZ", "PRIVACY", cipher_text
#     # )
#     print(decrypted_text)
