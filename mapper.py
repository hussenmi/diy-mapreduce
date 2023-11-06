import os
import hashlib  # I tried using the md5 hash function but it's not necessary for our case. I opted for a simpler hash function that simply sums the ASCII values of the characters in the word.
import re
from multiprocessing import Process

class Mapper(Process):
    def __init__(self, input_dir, reducer_queues):
        super().__init__()
        self.input_dir = input_dir
        self.reducer_queues = reducer_queues

    def run(self):
        # Read the input file in the given directory
        with open(os.path.join(self.input_dir, 'input.txt'), 'r') as f:
            content = f.read()  # Read the whole file at once

        # Use a regular expression to find all words
        words = re.findall(r'\b\w+\b', content)

        for word in words:
            clean_word = word.lower()  # Convert to lowercase
            reducer_index = self.get_reducer_index(clean_word)
            self.reducer_queues[reducer_index].put((clean_word, 1))

        # Send EOF message to all reducers to signal the end of data
        for queue in self.reducer_queues:
            queue.put(None)

    def get_reducer_index(self, word):
        # In our case, a simple hash function should suffice since the aim is not security but distributing the words evenly
        # among the reducers and for the data I have, I checked the distribution and it is pretty even. One of the reducers
        # got 189 words and the other got 196 words. The difference is not that much. I also tried using the md5 hash function
        # and it also does well, but it's not necessary for our case.
        word_hash = self.simple_hash(word)
        return word_hash % len(self.reducer_queues)
    
        """
        word_hash = int(hashlib.md5(word.encode()).hexdigest(), 16)
        return word_hash % len(self.reducer_queues)
        """

    
    # We're using static method here because we don't need to access any instance variables
    @staticmethod
    def simple_hash(word):
        return sum(ord(char) for char in word)



if __name__ == '__main__':
    # Example usage of the Mapper class
    # Assuming you have set up the necessary infrastructure for the queues and such
    pass
