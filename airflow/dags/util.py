import random

def get_random_string(self, length):
    """
    Adapted from: https://pynative.com/python-generate-random-string/
    """
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str