from collections import Counter
from multiprocessing import Process
import os
import signal

class Reducer(Process):
    def __init__(self, queue, output_file, num_mappers, identifier):
        super().__init__()
        self.queue = queue  
        self.output_file = output_file  
        self.num_mappers = num_mappers
        self.identifier = identifier
        self.word_counts = Counter()  

    def run(self):
        # The run method is called when the process starts
        
        # Simulate failure for a specific reducer, with identifier 1
        # if self.identifier == 1:
        #     print(f"Simulating failure for reducer with identifier {self.identifier}")
        #     os.kill(os.getpid(), signal.SIGTERM)
            
        eof_received = 0  # Counter for EOF signals received from mappers
        while eof_received < self.num_mappers:  
            # Here, we are hearing for anything that is put into the queue. The mapper process doesn't have to finish for the 
            # reducer to start processing the data.
            data = self.queue.get()  
            if data is None:  
                eof_received += 1  
            else:
                word, count = data  
                self.word_counts[word] += count

        self.write_results()  

    def write_results(self):
        # This method writes the reducer's results to the output file
        with open(self.output_file, 'w') as f:  
            for word, count in self.word_counts.items():  
                f.write(f"{word}: {count}\n")