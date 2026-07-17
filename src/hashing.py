import hashlib

def calc_with(binary_input, algo:str) -> str:
    h = hashlib.new(algo)
    h.update(binary_input)
    return h.hexdigest()
