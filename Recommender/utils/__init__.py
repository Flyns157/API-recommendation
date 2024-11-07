
"""
Module providing utility functions for generating random codes and other common tasks.

Classes:
    Utils: Contains utility methods, such as generating verification codes.
"""

import numpy as np
import string
import random
import re

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

    @classmethod
    def snake_to_camel(cls, snake_str: str) -> str:
        """
        Convertit une chaîne de caractères de snake_case à camelCase.

        Args:
            snake_str (str): La chaîne de caractères en snake_case.

        Returns:
            str: La chaîne de caractères convertie en camelCase.
        """
        components = snake_str.split('_')
        return components[0] + ''.join(x.title() for x in components[1:])

    @classmethod
    def array_avg(cls, matrices):
        """
        Calcule la moyenne d'une liste de matrices (numpy.ndarray).

        Args:
            matrices (list of numpy.ndarray): Liste de matrices à moyenner.

        Returns:
            numpy.ndarray: La matrice moyenne.
        """
        matrices = list(matrices)
        if not matrices:
            raise ValueError("La liste de matrices ne doit pas être vide.")
        
        # Vérifier que toutes les matrices ont la même forme
        shape = matrices[0].shape
        if not all(matrix.shape == shape for matrix in matrices):
            raise ValueError("Toutes les matrices doivent avoir la même forme.")
        
        # Calculer la somme des matrices
        sum_matrix = np.sum(matrices, axis=0)
        
        # Diviser par le nombre de matrices pour obtenir la moyenne
        average_matrix = sum_matrix / len(matrices)
        
        return average_matrix
