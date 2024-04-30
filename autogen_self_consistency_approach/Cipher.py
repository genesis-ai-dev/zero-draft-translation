import random
from string import ascii_letters

class RandomSubCipher:
    def __init__(self):
        self.forward_map = self._generate_map()
        self.backward_map = {v: k for k, v in self.forward_map.items()}

    def _generate_map(self):
        letters = list(ascii_letters)
        shuffled_letters = random.sample(letters, len(letters))
        return dict(zip(letters, shuffled_letters))

    def cipher(self, text):
        return ''.join(self.forward_map.get(char, char) for char in text)

    def decipher(self, text):
        return ''.join(self.backward_map.get(char, char) for char in text)

# # Example usage
# cipher_instance = RandomSubCipher()
# original_text = "In the beginning, God created the heavens and the earth."
# encrypted_text = cipher_instance.cipher(original_text)
# decrypted_text = cipher_instance.decipher(encrypted_text)

# print("Original:", original_text)
# print("Encrypted:", encrypted_text)
# print("Decrypted:", decrypted_text)
