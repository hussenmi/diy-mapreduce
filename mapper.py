import os
import re
import hashlib  # Used to hash the words
from multiprocessing import Process, current_process
import signal

class Mapper(Process):
    def __init__(self, input_dir, reducer_queues, identifier):
        # Call the initializer of the parent Process class
        super().__init__()
        self.input_dir = input_dir  
        self.reducer_queues = reducer_queues
        self.identifier = identifier

    def run(self):
        # The run method is called when the process starts
        input_file_path = os.path.join(self.input_dir, 'input.txt')  
        with open(input_file_path, 'r') as input_file:  
            for line in input_file:
                # if self.identifier == 2:  
                #     print("Simulating failure for mapper with identifier 2")
                #     os.kill(current_process().pid, signal.SIGTERM)
                    
                    
                words = re.findall(r'\b\w+\b', line)  # Extract words using regex
                for word in words:  
                    clean_word = word.lower()  
                    reducer_index = self.get_reducer_index(clean_word)  # Get the reducer index based on the word
                    # Put the word and its count (1) into the appropriate reducer queue
                    self.reducer_queues[reducer_index].put((clean_word, 1))

        # After processing all lines, send a None (EOF marker) to all reducer queues
        for queue in self.reducer_queues:
            queue.put(None)

    def get_reducer_index(self, word):
        # This function uses a hash function to map a word to a reducer index
        # The md5 hash function is used to create a hash of the word
        word_hash = int(hashlib.md5(word.encode()).hexdigest(), 16)
        # The hash is then used to determine which reducer queue to use
        # by taking the modulo with the number of reducer queues
        return word_hash % len(self.reducer_queues)
