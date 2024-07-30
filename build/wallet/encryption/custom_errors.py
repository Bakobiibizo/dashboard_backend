# Key errors

    
class KeyNotFoundError(KeyError):
    """Error raised when a key is not found in the keyring."""
    
    
class IncorrectKeyError(KeyError):
    """Error raised when an incorrect key is provided."""    


# Cryptography errors

    
class CryptographyError(Exception):
    """Error raised when encrypting and decrypting files."""
    
    
class DecryptionError(CryptographyError):
    """Error raised when decryption fails."""
    

class EncryptionError(CryptographyError):
    """Error raised when encryption fails."""
    

class WrongPasswordError(CryptographyError):
    """Error raised when the password is incorrect."""
    
    
class InvalidKeyError(CryptographyError):
    """Error raised when the key is invalid."""
    

class InvalidSaltError(CryptographyError):
    """Error raised when the salt is invalid."""
    
