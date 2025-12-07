from typing import TypeVar, Generic, Optional

T = TypeVar('T')

class Node(Generic[T]):
    """Internal node for linked-list based structures."""
    def __init__(self, value: T):
        self.value = value
        self.next: Optional['Node[T]'] = None

class Stack(Generic[T]):
    """
    A manual implementation of a Stack using a Linked List.
    Used for DFS (Depth-First Search).
    LIFO: Last-In, First-Out.
    """
    def __init__(self):
        self.top: Optional[Node[T]] = None
        self._size = 0

    def push(self, item: T):
        # add item to the top of the stack
        new_node = Node(item)
        new_node.next = self.top
        self.top = new_node
        self._size += 1

    def pop(self) -> T:
        # remove and return item from the top
        if self.is_empty():
            raise IndexError("pop from empty stack")
        
        value = self.top.value
        self.top = self.top.next
        self._size -= 1
        return value

    def is_empty(self) -> bool:
        return self.top is None

    def clear(self):
        self.top = None
        self._size = 0

    def __len__(self):
        return self._size
