
"""
Module providing utility functions for generating random codes and other common tasks.

Classes:
    Utils: Contains utility methods, such as generating verification codes.
"""

import string
import random

from .database import Database

__all__ = ['Database', 'Utils']

class Utils:
    """
    Utility class providing commonly used helper methods.

    Methods:
        generate_verification_code: Generates a random alphanumeric verification code.
    """
    
    @classmethod
    def generate_verification_code(cls, size: int = 6) -> str:
        """
        Generate a random alphanumeric verification code of a specified length.

        Parameters:
            size (int): The length of the verification code to generate. Default is 6.

        Returns:
            str: A randomly generated verification code containing uppercase letters, lowercase letters, and digits.

        Example:
            >>> Utils.generate_verification_code(8)
            'A3kLp9Vz'
        """
        CHARS = string.ascii_letters + string.digits
        return ''.join(random.choice(CHARS) for _ in range(size))
