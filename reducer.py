from collections import Counter
from multiprocessing import Process

class Reducer(Process):
    def __init__(self, queue, output_file, num_mappers):
        super().__init__()
        self.queue = queue  
        self.output_file = output_file  
        self.num_mappers = num_mappers  
        self.word_counts = Counter()  

    def run(self):
        # The run method is called when the process starts
        eof_received = 0  # Counter for EOF signals received from mappers
        while eof_received < self.num_mappers:  
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

                








                
#### IF WE WANT TO USE A QUEUE INSTEAD OF A FILE TO SEND RESULTS FROM REDUCERS TO MAIN PROCESS ####

# # reducer.py
# from multiprocessing import Process

# class Reducer(Process):
#     def __init__(self, input_queue, output_queue, num_mappers):
#         super().__init__()
#         self.input_queue = input_queue
#         self.output_queue = output_queue
#         self.num_mappers = num_mappers
#         self.word_counts = {}

#     def run(self):
#         eof_received = 0
#         while eof_received < self.num_mappers:
#             data = self.input_queue.get()
#             if data is None:
#                 eof_received += 1
#             else:
#                 word, count = data
#                 if word in self.word_counts:
#                     self.word_counts[word] += count
#                 else:
#                     self.word_counts[word] = count

#         # Instead of writing to a file, put the results in the output queue
#         self.output_queue.put(self.word_counts)


