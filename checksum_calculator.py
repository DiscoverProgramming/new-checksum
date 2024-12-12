import hashlib

class ChecksumCalculator:
    def __init__(self):
        self.hash_functions = {
            'MD5': hashlib.md5,
            'SHA-1': hashlib.sha1,
            'SHA-256': hashlib.sha256,
            'SHA-512': hashlib.sha512
        }

    def calculate(self, filepath: str, hash_type: str) -> str:
        hash_func = self.hash_functions.get(hash_type, hashlib.sha256)()
        
        try:
            with open(filepath, 'rb') as file:
                while chunk := file.read(8192):
                    hash_func.update(chunk)
            return hash_func.hexdigest()
        except Exception as e:
            return f"Error: {str(e)}"
