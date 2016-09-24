import numpy as np
import json
letters = [l for l in 'ABCDEFGHIJKLMNOPQRSTUVXYZ']
numbers = np.random.permutation(np.arange(len(letters)))
num_to_letter = {'{:02}'.format(n): l for n, l in zip(numbers, letters)}
print(num_to_letter)
with open('num_to_letter.json', 'x') as f:
    json.dump(num_to_letter, f)
