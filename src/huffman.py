from typing import Self

from bitarray import bitarray

import heapq

class HUFFMAN_NODE:
    def __init__(self, value: str, frequency: int):
        self.VALUE = value
        self.FREQUENCY = frequency
        self.LEFT = None
        self.RIGHT = None
        self.PARENT = None

    def __lt__(self, other: Self):
        return self.FREQUENCY < other.FREQUENCY
    
    def __eq__(self, other: Self):
        if other == None:
            return False
        
        if not isinstance(other, HUFFMAN_NODE):
            return False
        
        return self.FREQUENCY == other.FREQUENCY

frequencies = {
    'A': 45,
    'B': 13,
    'C': 12,
    'D': 16,
    'E': 9,
    'F': 5
}

def make_huffman_codes(node: HUFFMAN_NODE, current_code: bitarray, huffman_codes: dict) -> None:
    if node == None:
        return

    if node.VALUE != None:
        huffman_codes[node.VALUE] = current_code.copy()
        return
    
    make_huffman_codes(node.LEFT, current_code + bitarray([0]), huffman_codes)
    make_huffman_codes(node.RIGHT, current_code + bitarray([1]), huffman_codes)

def create_huffman_tree() -> None:
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

    make_huffman_codes(root, bitarray(), huffman_codes)

    print("HUFFMAN CODES", len(huffman_codes))
    for key, value in huffman_codes.items():
        print(f"{str(key).ljust(1)} : {value}")

    # WRITE THEM TO A FILE 

    serialized = bitarray(endian='big')

    def dfs(node: HUFFMAN_NODE):
        if node == None:
            return
        
        if node.VALUE != None:
            serialized.append(1)
            serialized.extend(bitarray(format(ord(node.VALUE), '08b')))
            return
        
        serialized.append(0)
        dfs(node.LEFT)
        dfs(node.RIGHT)

    dfs(root)

    print(serialized)

    with open('huffman_tree', 'wb') as file:
        file.write(serialized.tobytes())

def read_huffman_bin() -> None:
    serialized = bitarray(endian='big')

    with open('huffman_tree', 'rb') as file:
        serialized.fromfile(file)

    root = HUFFMAN_NODE(None, 0)
    curr_node = root
    ind = 0
    total_bits = len(serialized)

    def get_node_with_empty_right(curr_node: HUFFMAN_NODE) -> HUFFMAN_NODE | None:
        if curr_node == None:
            return None

        if curr_node.RIGHT == None:
            return curr_node
        
        return get_node_with_empty_right(curr_node.PARENT)

    while ind < total_bits:
        curr_bit = serialized[ind]

        if curr_bit == 0:
            curr_node.LEFT = HUFFMAN_NODE(None, 0)
            curr_node.LEFT.PARENT = curr_node

            curr_node = curr_node.LEFT
        else:
            curr_node.VALUE = chr(int(serialized[ind + 1: ind + 9].to01(), 2))
            curr_node = get_node_with_empty_right(curr_node.PARENT)

            if curr_node == None:
                break

            curr_node.RIGHT = HUFFMAN_NODE(None, 0)
            curr_node.RIGHT.PARENT = curr_node

            curr_node = curr_node.RIGHT
            ind += 8

        ind += 1

    huffman_codes = {}
    make_huffman_codes(root, bitarray(), huffman_codes)

    print("HUFFMAN CODES", len(huffman_codes))
    for key, value in huffman_codes.items():
        print(f"{str(key).ljust(1)} : {value}")

create_huffman_tree()
read_huffman_bin()