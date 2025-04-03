import random
import string


class Vigenere:
    @staticmethod
    def get_initial_instructions():
        """
        Displays instructions for how to use the Vigenere cipher class.
        """
        instructions = (
            "You are a deciphering agent. Your task is to decipher a ciphertext produced from a Vigenere cipher without the keys and return meaningful plain text. "
            "In Vigenere cipher, the letters of the plaintext is encoded with a different Caesar cipher. Here are the rules of Vigenere cipher. "
            "\nEach letter is right shifted by a number of positions corresponding to the alphabetical index of the corresponding letter in the key. If the key length is less than the length of plain text, the key string is repeated until key and plaintext is equal. A space or non-alphabetical characters are not encrypted and left as they are, but each of such characters still consume a key letter during encryption/decryption.\n"
            "Note: The plain texts are always meaningful sentences in the English language."
        )
        return instructions

    @staticmethod
    def generate_random_parameters() -> dict:
        """Method to generate random parameters for an encryption. The returned dict can be passed as arguments to encrypt function.
        Returns:
            dict: Dictionary with keys "key". "key" is a alphabetical key and can be from length between 10 to 20 letters.
        """
        num_letters = random.randint(10, 20)
        key = "".join(random.choice(string.ascii_lowercase) for _ in range(num_letters))
        return {"key": key}

    @staticmethod
    def extend_key(key: str, text_length: int) -> str:
        """
        Extends the key to match the length of the text to encrypt or decrypt.

        Args:
            key (str): The keyword.
            text_length (int): The length of the text to process.

        Returns:
            str: The extended key.
        """
        key = key.upper()
        extended_key = (
            key * (text_length // len(key)) + key[: text_length % len(key)]
        ).upper()
        return extended_key

    @staticmethod
    def encrypt(key: str, plain_text: str) -> str:
        """
        Encrypts a plain text message using the Vigenere cipher.

        Args:
            key (str): The encryption key.
            plain_text (str): The message to encrypt.

        Returns:
            str: The encrypted message.
        """
        key = Vigenere.extend_key(key, len(plain_text))
        encrypted_text = ""

        for i, char in enumerate(plain_text):
            if char.isalpha():
                ascii_offset = 65 if char.isupper() else 97
                key_shift = ord(key[i]) - 65
                new_char = chr(
                    ((ord(char) - ascii_offset + key_shift) % 26) + ascii_offset
                )
                encrypted_text += new_char
            else:
                encrypted_text += char  # Non-alphabetic characters remain unchanged
        return encrypted_text

    @staticmethod
    def decrypt(key: str, cipher_text: str) -> str:
        """
        Decrypts a cipher text message using the Vigenere cipher.

        Args:
            key (str): The decryption key.
            cipher_text (str): The encrypted message to decrypt.

        Returns:
            str: The decrypted message.
        """
        key = Vigenere.extend_key(key, len(cipher_text))
        decrypted_text = ""

        for i, char in enumerate(cipher_text):
            if char.isalpha():
                ascii_offset = 65 if char.isupper() else 97
                key_shift = ord(key[i]) - 65
                new_char = chr(
                    ((ord(char) - ascii_offset - key_shift) % 26) + ascii_offset
                )
                decrypted_text += new_char
            else:
                decrypted_text += char  # Non-alphabetic characters remain unchanged
        return decrypted_text


# Example usage
# if __name__ == "__main__":
#     vigenere = Vigenere()
#     print(vigenere.get_initial_instructions())
#     plain_text = "attacking tonight"
#     key = "oculorhinolaryngology"
#     encrypted = vigenere.encrypt(key, plain_text)
#     print("Encrypted:", encrypted)
#     decrypted = vigenere.decrypt(key, encrypted)
#     print("Decrypted:", decrypted)
