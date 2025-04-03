import math
import random


class Affine:
    @staticmethod
    def get_initial_instructions():
        """
        Displays instructions for how to use the Affine cipher class.
        """
        instructions = (
            "You are a deciphering agent. Your task is to decipher a ciphertext produced from an Affine cipher without the keys and return meaningful plain text. "
            "The Affine cipher is a substitution cipher that uses a mathematical formula to encode letters. "
            "The formula is: E(x) = (a * x + b) mod m, where 'a' and 'b' are keys, 'x' is the letter's position in the alphabet, and 'm' is the size of the alphabet (26). "
            "The plain texts are always meaningful sentences in the English language."
        )
        return instructions

    @staticmethod
    def generate_random_parameters() -> dict:
        """Method to generate random parameters for an encryption.
        Returns:
            dict: Dictionary with keys "a", "b". Remember "a" is the multiplicative key and "b" is the additive key. "a" has to be coprime with integer 26.

        """
        return {
            "a": random.choice([3, 5, 7, 9, 11, 15, 17, 19, 21, 23, 25]),
            "b": random.randint(1, 100),
        }

    @staticmethod
    def mod_inverse(a: int, m: int) -> int:
        """
        Calculates the modular multiplicative inverse of 'a' under modulo 'm'.

        Args:
            a (int): The integer whose modular inverse is to be calculated.
            m (int): The modulo.

        Returns:
            int: The modular inverse of 'a'.
        """
        a = a % m
        for x in range(1, m):
            if (a * x) % m == 1:
                return x
        raise ValueError(f"No modular inverse for a = {a} under modulo m = {m}")

    @staticmethod
    def encrypt(a: int, b: int, plain_text: str) -> str:
        """
        Encrypts a plain text message using the Affine cipher.

        Args:
            a (int): Multiplicative key.
            b (int): Additive key.
            plain_text (str): The message to encrypt.

        Returns:
            str: The encrypted message.
        """
        if math.gcd(a, 26) != 1:
            raise ValueError("Key 'a' must be coprime with 26.")

        encrypted_text = ""
        for char in plain_text:
            if char.isalpha():
                ascii_offset = 65 if char.isupper() else 97
                x = ord(char) - ascii_offset
                new_char = chr(((a * x + b) % 26) + ascii_offset)
                encrypted_text += new_char
            else:
                encrypted_text += char  # Non-alphabetic characters remain unchanged
        return encrypted_text

    @staticmethod
    def decrypt(a: int, b: int, cipher_text: str) -> str:
        """
        Decrypts a cipher text message using the Affine cipher.

        Args:
            a (int): Multiplicative key.
            b (int): Additive key.
            cipher_text (str): The encrypted message to decrypt.

        Returns:
            str: The decrypted message.
        """
        if math.gcd(a, 26) != 1:
            raise ValueError("Key 'a' must be coprime with 26.")

        a_inv = Affine.mod_inverse(a, 26)
        decrypted_text = ""
        for char in cipher_text:
            if char.isalpha():
                ascii_offset = 65 if char.isupper() else 97
                y = ord(char) - ascii_offset
                new_char = chr(((a_inv * (y - b)) % 26) + ascii_offset)
                decrypted_text += new_char
            else:
                decrypted_text += char  # Non-alphabetic characters remain unchanged
        return decrypted_text


# # Example usage
# if __name__ == "__main__":
#     affine = Affine()
#     print(affine.get_initial_instructions())
#     plain_text = "Hello World!"
#     a, b = 5, 8
#     encrypted = affine.encrypt(a, b, plain_text)
#     print("Encrypted:", encrypted)
#     decrypted = affine.decrypt(a, b, encrypted)
#     print("Decrypted:", decrypted)
