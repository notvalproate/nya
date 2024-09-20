from typing import Self

from bitarray import bitarray

import heapq

class HUFFMAN_NODE:
    def __init__(self, value: str, frequency: int):
        self.VALUE = value
        self.FREQUENCY = frequency
        self.LEFT = None
        self.RIGHT = None

    def __lt__(self, other: Self):
        return self.FREQUENCY < other.FREQUENCY
    
    def __eq__(self, other: Self):
        if other == None:
            return False
        
        if not isinstance(other, HUFFMAN_NODE):
            return False
        
        return self.FREQUENCY == other.FREQUENCY

frequencies = {
    'a': 45,
    'b': 13,
    'c': 12,
    'd': 16,
    'e': 9,
    'f': 5
}

heap = []

for key in frequencies:
    node = HUFFMAN_NODE(key, frequencies[key])
    heapq.heappush(heap, node)

while len(heap) > 1:
    left = heapq.heappop(heap)
    right = heapq.heappop(heap)

    parent = HUFFMAN_NODE(None, left.FREQUENCY + right.FREQUENCY)
    parent.LEFT = left
    parent.RIGHT = right

    heapq.heappush(heap, parent)

huffman_codes = {}
root = heapq.heappop(heap)

def make_huffman_codes(node: HUFFMAN_NODE, current_code: bitarray):
    if node == None:
        return

    if node.VALUE != None:
        huffman_codes[node.VALUE] = current_code.copy()
        return
    
    make_huffman_codes(node.LEFT, current_code + bitarray([0]))
    make_huffman_codes(node.RIGHT, current_code + bitarray([1]))

make_huffman_codes(root, bitarray())

print("HUFFMAN CODES", len(huffman_codes))
for key, value in huffman_codes.items():
    print(f"{str(key).ljust(1)} : {value}")
