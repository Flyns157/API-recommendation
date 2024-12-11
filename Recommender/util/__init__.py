
"""
Module providing utility functions for generating random codes and other common tasks.
"""

import numpy as np
import string
import random
import bcrypt


def generate_verification_code(size: int = 6) -> str:
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

def snake_to_camel(snake_str: str) -> str:
    """
    Convertit une chaîne de caractères de snake_case à camelCase.

    Args:
        snake_str (str): La chaîne de caractères en snake_case.

    Returns:
        str: La chaîne de caractères convertie en camelCase.
    """
    components = snake_str.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])

def array_avg(matrices: list[np.ndarray], *args) -> np.ndarray:
    """
    Calcule la moyenne d'une liste de matrices (numpy.ndarray).

    Args:
        matrices (list of numpy.ndarray): Liste de matrices à moyenner.

    Returns:
        numpy.ndarray: La matrice moyenne.
    """
    matrices = list(matrices if len(args) == 0 else args)
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

def isiterable(obj) -> bool:
    try:
        iter(obj)
        return True
    except:
        return False

def generate_password(size: int = 15) -> str:
    """
    Generate a random password of a given size.

    Parameters:
        size (int): The length of the password to be generated. Defaults to 15.

    Returns:
        str: A randomly generated password consisting of ASCII letters and digits.
    """
    CHARS = string.ascii_letters + string.digits
    return ''.join(random.choice(CHARS) for _ in range(size))


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.

    Parameters:
        password (str): The password to be hashed.

    Returns:
        str: The hashed password.
    """
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password using bcrypt.

    Parameters:
        plain_password (str): The plain password to be verified.
        hashed_password (str): The hashed password to be verified against.

    Returns:
        bool: True if the plain password matches the hashed password, False otherwise.
    """
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
