class Atbash:
    @staticmethod
    def get_initial_instructions():
        """
        Displays instructions for how to use the Atbash cipher class.
        """
        instructions = (
            "You are a deciphering agent. Your task is to decipher a ciphertext produced from an Atbash cipher and return meaningful plain text. "
            "The Atbash cipher is a substitution cipher where each letter of the alphabet is replaced with its reverse counterpart. "
            "For example, 'A' becomes 'Z', 'B' becomes 'Y', and so on. The plain texts are always meaningful sentences in the English language."
        )
        return instructions

    @staticmethod
    def generate_random_parameters() -> dict:
        return {}

    @staticmethod
    def encrypt(plain_text: str) -> str:
        """
        Encrypts a plain text message using the Atbash cipher.

        Args:
            plain_text (str): The message to encrypt.

        Returns:
            str: The encrypted message.
        """
        encrypted_text = ""
        for char in plain_text:
            if char.isalpha():
                ascii_offset = 65 if char.isupper() else 97
                new_char = chr(ascii_offset + (25 - (ord(char) - ascii_offset)))
                encrypted_text += new_char
            else:
                encrypted_text += char  # Non-alphabetic characters remain unchanged
        return encrypted_text

    @staticmethod
    def decrypt(cipher_text: str) -> str:
        """
        Decrypts a cipher text message using the Atbash cipher.

        Args:
            cipher_text (str): The encrypted message to decrypt.

        Returns:
            str: The decrypted message.
        """
        # Decryption is the same as encryption in the Atbash cipher
        return Atbash.encrypt(cipher_text)


# # Example usage
# if __name__ == "__main__":
#     atbash = Atbash()
#     print(atbash.get_initial_instructions())
#     plain_text = "Hello there in the world!"
#     encrypted = atbash.encrypt(plain_text)
#     print("Encrypted:", encrypted)
#     decrypted = atbash.decrypt(encrypted)
#     print("Decrypted:", decrypted)
