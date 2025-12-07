from typing import TypeVar, Generic, Optional

T = TypeVar('T')

class Node(Generic[T]):
    def __init__(self, value: T):
        self.value = value
        self.next: Optional['Node[T]'] = None

class Queue(Generic[T]):
    def __init__(self):
        self.head: Optional[Node[T]] = None
        self.tail: Optional[Node[T]] = None
        self._size = 0

    def enqueue(self, item: T):
        # create a new node with the item
        new_node = Node(item)
        # if there's already a tail, link it to the new node
        if self.tail:
            self.tail.next = new_node
        # make the new node the tail
        self.tail = new_node
        # if queue was empty, this is also the head
        if not self.head:
            self.head = new_node
        # increment size
        self._size += 1

    def dequeue(self) -> T:
        # can't remove from empty queue
        if self.is_empty():
            raise IndexError("dequeue from empty queue")
        
        # grab the value from the head
        value = self.head.value
        # move head to the next node
        self.head = self.head.next
        # if queue is now empty, clear the tail too
        if not self.head:
            self.tail = None
        # decrement size
        self._size -= 1
        return value

    def is_empty(self) -> bool:
        return self.head is None

    def clear(self):
        # reset everything
        self.head = None
        self.tail = None
        self._size = 0

    def __len__(self):
        return self._size