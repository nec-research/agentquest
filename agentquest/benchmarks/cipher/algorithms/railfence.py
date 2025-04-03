import random


class RailFence:
    @staticmethod
    def get_initial_instructions():
        """
        Displays instructions for how to use the RailFence cipher class.
        """
        instructions = (
            "You are a deciphering agent. Your task is to decipher a ciphertext produced from a RailFence cipher and return meaningful plain text. "
            "The RailFence cipher is a transposition cipher that encrypts by writing the plaintext in a zigzag pattern across multiple rows (or rails), "
            "then reading it row by row. Note: The plain texts are always meaningful sentences in the English language."
        )
        return instructions

    @staticmethod
    def generate_random_parameters() -> dict:
        """Generates random parameters for an encryption.
        Returns:
            dict: Dictionary with keys "num_rails" with random value between 2 and 15.
        """
        return {"num_rails": random.randint(2, 15)}

    @staticmethod
    def encrypt(num_rails: int, plain_text: str) -> str:
        """
        Encrypts a plain text message using the RailFence cipher.

        Args:
            plain_text (str): The message to encrypt.
            num_rails (int): The number of rails to use in the zigzag pattern.

        Returns:
            str: The encrypted message.
        """
        if num_rails <= 1:
            raise ValueError("Number of rails must be greater than 1.")

        # Create an empty rail matrix
        rails = ["" for _ in range(num_rails)]
        direction_down = False
        row = 0

        # Write the plaintext in a zigzag pattern
        for char in plain_text:
            rails[row] += char
            if row == 0 or row == num_rails - 1:
                direction_down = not direction_down
            row += 1 if direction_down else -1

        # Read the rails row by row
        encrypted_text = "".join(rails)
        return encrypted_text

    @staticmethod
    def decrypt(num_rails: int, cipher_text: str) -> str:
        """
        Decrypts a cipher text message using the RailFence cipher.

        Args:
            cipher_text (str): The encrypted message to decrypt.
            num_rails (int): The number of rails used during encryption.

        Returns:
            str: The decrypted message.
        """
        if num_rails <= 1:
            raise ValueError("Number of rails must be greater than 1.")

        # Determine the zigzag pattern
        rail_lengths = [0] * num_rails
        direction_down = False
        row = 0

        for _ in cipher_text:
            rail_lengths[row] += 1
            if row == 0 or row == num_rails - 1:
                direction_down = not direction_down
            row += 1 if direction_down else -1

        # Reconstruct the rails
        rails = []
        start = 0
        for length in rail_lengths:
            rails.append(cipher_text[start : start + length])
            start += length

        # Read the rails in zigzag order to reconstruct the plaintext
        decrypted_text = ""
        row_indices = [0] * num_rails
        direction_down = False
        row = 0

        for _ in cipher_text:
            decrypted_text += rails[row][row_indices[row]]
            row_indices[row] += 1
            if row == 0 or row == num_rails - 1:
                direction_down = not direction_down
            row += 1 if direction_down else -1

        return decrypted_text


# Example usage
if __name__ == "__main__":
    rail_fence = RailFence()
    print(rail_fence.get_initial_instructions())
    plain_text = "HELLOWORLD"
    num_rails = 3
    encrypted = rail_fence.encrypt(num_rails, plain_text)
    print("Encrypted:", encrypted)
    decrypted = rail_fence.decrypt(num_rails, encrypted)
    print("Decrypted:", decrypted)
