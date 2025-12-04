from typing import List, TypeVar, Generic

T = TypeVar('T')

class MinHeap(Generic[T]):
    def __init__(self):
        # underlying list to store heap elements
        self.heap: List[T] = []

    def push(self, item: T):
        # add item to the end and bubble it up to maintain heap property
        self.heap.append(item)
        self._sift_up(len(self.heap) - 1)

    def pop(self) -> T:
        # remove and return the smallest item (root)
        if self.is_empty():
            raise IndexError("pop from empty heap")
        
        # swap root with last element
        self._swap(0, len(self.heap) - 1)
        item = self.heap.pop()
        
        # bubble down the new root to maintain heap property
        if not self.is_empty():
            self._sift_down(0)
            
        return item

    def is_empty(self) -> bool:
        return len(self.heap) == 0

    def _sift_up(self, idx: int):
        parent = (idx - 1) // 2
        if idx > 0 and self.heap[idx] < self.heap[parent]:
            self._swap(idx, parent)
            self._sift_up(parent)

    def _sift_down(self, idx: int):
        smallest = idx
        left = 2 * idx + 1
        right = 2 * idx + 2

        if left < len(self.heap) and self.heap[left] < self.heap[smallest]:
            smallest = left
        
        if right < len(self.heap) and self.heap[right] < self.heap[smallest]:
            smallest = right
            
        if smallest != idx:
            self._swap(idx, smallest)
            self._sift_down(smallest)

    def _swap(self, i: int, j: int):
        self.heap[i], self.heap[j] = self.heap[j], self.heap[i]

    def __len__(self):
        return len(self.heap)
