import random


class Caesar:
    @staticmethod
    def get_initial_instructions():
        """
        Displays instructions for how to use the Caesar cipher class.
        """
        instructions = "You are a deciphering agent. Your task is to decipher a ciphertext produced from a Caesar cipher and return meaningful plain text. Caesar cipher is a type of substitution cipher in which each alphabetical letter in the plaintext is replaced by a letter some fixed number of position shifts down the alphabet. The shift can be either left shift of right shift. The plain texts are always meaningful sentences in English language."
        return instructions

    @staticmethod
    def generate_random_parameters() -> dict:
        """Method to generate random parameters for an encryption.
        Returns:
            dict: Dictionary with keys "shift", "shift_direction".
        """
        return {
            "shift": random.randint(1, 25),
            "shift_direction": random.choice(["left", "right"]),
        }

    @staticmethod
    def encrypt(shift: int, shift_direction: str, plain_text: str) -> str:
        """
        Encrypts a plain text message using the Caesar cipher.

        Args:
            shift (int): Number of positions to shift the alphabet.
            shift_direction (str): Direction of the shift ('left' or 'right').
            plain_text (str): The message to encrypt.

        Returns:
            str: The encrypted message.
        """
        if shift_direction not in ["left", "right"]:
            raise ValueError("shift_direction must be 'left' or 'right'")

        if shift_direction == "left":
            shift = -shift  # Convert left shift to negative right shift

        encrypted_text = ""
        for char in plain_text:
            if char.isalpha():  # Only encrypt alphabetic characters
                ascii_offset = 65 if char.isupper() else 97
                new_char = chr((ord(char) - ascii_offset + shift) % 26 + ascii_offset)
                encrypted_text += new_char
            else:
                encrypted_text += char  # Non-alphabetic characters remain unchanged
        return encrypted_text

    @staticmethod
    def decrypt(shift: int, shift_direction: str, cipher_text: str):
        """
        Decrypts a cipher text message using the Caesar cipher.

        Args:
            shift (int): Number of positions the text was shifted.
            shift_direction (str): Direction of the original shift ('left' or 'right').
            cipher_text (str): The encrypted message to decrypt.

        Returns:
            str: The decrypted message.
        """
        # Reverse the direction for decryption
        opposite_direction = "right" if shift_direction == "left" else "left"
        return Caesar.encrypt(shift, opposite_direction, cipher_text)


# Example Usage:
# if __name__ == "__main__":
#     Caesar.get_initial_instructions()

#     # Encrypting a message
#     shift = 5
#     direction = "left"
#     plain_text = "Hello, World!"
#     cipher_text = Caesar.encrypt(shift, direction, plain_text)
#     print(f"Encrypted Text: {cipher_text}")

#     # Decrypting the message
#     decrypted_text = Caesar.decrypt(shift, direction, cipher_text)
#     print(f"Decrypted Text: {decrypted_text}")
