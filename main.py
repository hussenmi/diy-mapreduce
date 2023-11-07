import os
import shutil
from multiprocessing import Process, Queue
from mapper import Mapper
from reducer import Reducer
from collections import Counter

# Constants
NUM_MAPPERS = 4
NUM_REDUCERS = 2
INPUT_FILE = 'transcript.txt'
BASE_DIR = 'data'

def split_input_file_block(input_file, num_mappers, base_dir):
    """
    Splits an input file into blocks and distributes these blocks among files for each mapper.
    
    This method counts the lines in the input file first and then writes out blocks of lines to each mapper's file.
    It ensures that each mapper receives a contiguous block of lines and handles very large files efficiently by
    reading and writing one line at a time.
    
    Args:
    input_file (str): The path to the input file.
    num_mappers (int): The number of mappers (and thus files) to create.
    base_dir (str): The base directory where the mapper directories will be created.
    """
    # Ensure the base directory exists and is empty
    if os.path.exists(base_dir):
        shutil.rmtree(base_dir)
    os.makedirs(base_dir)

    # First pass: count the total number of lines in the input file
    total_lines = 0
    with open(input_file, 'r') as f:
        for line in f:
            total_lines += 1
    
    # Calculate the chunk size and remainder for the block distribution
    chunk_size, remainder = divmod(total_lines, num_mappers)
    
    # Second pass: write the lines to the appropriate chunk files
    with open(input_file, 'r') as f:
        for i in range(num_mappers):
            # Create a directory for each mapper
            mapper_dir = os.path.join(base_dir, f'mapper{i}')
            os.makedirs(mapper_dir, exist_ok=True)
            with open(os.path.join(mapper_dir, 'input.txt'), 'w') as mapper_f:
                # Write a block of lines to the mapper file
                for j in range(chunk_size + (1 if i < remainder else 0)):
                    mapper_f.write(next(f))

                    
def split_input_file_round_robin(input_file, num_mappers, base_dir):
    """
    Splits an input file among files for each mapper using a round-robin distribution.
    
    This method reads the input file line by line and distributes each line to a mapper's file in turn.
    This ensures that all mappers get an approximately equal number of lines without taking the entire file into memory.
    
    Args:
    input_file (str): The path to the input file.
    num_mappers (int): The number of mappers (and thus files) to create.
    base_dir (str): The base directory where the mapper directories will be created.
    """
    # Ensure the base directory exists
    if os.path.exists(base_dir):
        shutil.rmtree(base_dir)
    os.makedirs(base_dir)
    
    # Create a directory for each mapper
    mapper_dirs = [os.path.join(base_dir, f'mapper{i}') for i in range(num_mappers)]
    for mapper_dir in mapper_dirs:
        os.makedirs(mapper_dir, exist_ok=True)

    # Create a file for each mapper
    mapper_files = [
        open(os.path.join(mapper_dir, 'input.txt'), 'w') for mapper_dir in mapper_dirs
    ]
    
    # Distribute lines round-robin
    with open(input_file, 'r') as f:
        for i, line in enumerate(f):
            # Calculate which mapper to send the line to
            file_index = i % num_mappers
            mapper_files[file_index].write(line)
    
    # Close all the files
    for file in mapper_files:
        file.close()

def aggregate_results(num_reducers):
    """
    Aggregates the results from individual reducer outputs into a final result file.
    
    This function reads the output file from each reducer, aggregates the word counts across all reducers, and writes the 
    final word count to a single output file. It is designed to process each reducer's output file line by line to handle 
    potentially large files efficiently.
    
    Args:
    num_reducers (int): The number of reducers that have processed the data.
    """
    final_counts = Counter()
    for i in range(num_reducers):
        output_file = f'reducer_output_{i}.txt'
        with open(output_file, 'r') as f:
            for line in f:
                word, count = line.strip().split(': ')
                final_counts[word] += int(count)
    # Write the final results to a file
    with open('final_output.txt', 'w') as f:
        for word, count in final_counts.items():
            f.write(f"{word}: {count}\n")

def main():
    # Step 1: Split input file into chunks for mappers. We can choose to use either the block or round-robin method.
    split_input_file_block(INPUT_FILE, NUM_MAPPERS, BASE_DIR)
    # split_input_file_round_robin(INPUT_FILE, NUM_MAPPERS, BASE_DIR)

    # Step 2: Initialize queues for reducers
    reducer_queues = [Queue() for _ in range(NUM_REDUCERS)]

    # Step 3: Start reducer processes
    reducers = []
    for i in range(NUM_REDUCERS):
        output_file = f'reducer_output_{i}.txt'
        reducer = Reducer(reducer_queues[i], output_file, NUM_MAPPERS)
        reducers.append(reducer)
        reducer.start()

    # Step 4: Start mapper processes
    mappers = []
    for i in range(NUM_MAPPERS):
        mapper_dir = os.path.join(BASE_DIR, f'mapper{i}')
        mapper = Mapper(mapper_dir, reducer_queues)
        mappers.append(mapper)
        mapper.start()
        
    # Next, before we start aggregating the results, we want to make sure both the mappers and reducers have finished,
    # so we use the join() method on each process to wait for them to finish.

    # Step 5: Wait for all mappers to finish
    for mapper in mappers:
        mapper.join()

    # Step 6: Wait for all reducers to finish
    for reducer in reducers:
        reducer.join()

    # Step 7: Aggregate results from reducers and write to final output file
    aggregate_results(NUM_REDUCERS)

if __name__ == '__main__':
    main()
    
    




    
#### IF WE WANT TO USE QUEUES TO SEND RESULTS FROM REDUCERS TO MAIN PROCESS INSTEAD OF WRITING TO FILES ####
    
# import os
# import shutil
# from multiprocessing import Process, Queue
# from mapper import Mapper
# from reducer import Reducer
# from collections import Counter

# # Constants
# NUM_MAPPERS = 4
# NUM_REDUCERS = 2
# INPUT_FILE = 'transcript.txt'
# BASE_DIR = 'data'

# def split_input_file(input_file, num_mappers, base_dir):
#     # Ensure the base directory exists
#     if os.path.exists(base_dir):
#         shutil.rmtree(base_dir)
#     os.makedirs(base_dir)
    
#     # Read the input file and split into chunks
#     with open(input_file, 'r') as f:
#         content = f.read()
    
#     # Split the content by lines to ensure words are not broken
#     lines = content.splitlines()
#     chunk_size = len(lines) // num_mappers
#     chunks = [lines[i:i + chunk_size] for i in range(0, len(lines), chunk_size)]

#     # If there are more lines than mappers, add the remainder to the last chunk
#     if len(chunks) > num_mappers:
#         chunks[-2].extend(chunks[-1])
#         chunks = chunks[:-1]

#     # Write chunks to separate directories
#     for idx, chunk in enumerate(chunks):
#         mapper_dir = os.path.join(base_dir, f'mapper{idx}')
#         os.makedirs(mapper_dir)
#         with open(os.path.join(mapper_dir, 'input.txt'), 'w') as f:
#             f.write('\n'.join(chunk))

# def main():
#     # Step 1: Split input file into chunks for mappers
#     split_input_file(INPUT_FILE, NUM_MAPPERS, BASE_DIR)

#     # Step 2: Initialize queues for reducers
#     reducer_queues = [Queue() for _ in range(NUM_REDUCERS)]
#     output_queue = Queue()  # Queue for reducers to send their results

#     # Step 3: Start reducer processes
#     reducers = []
#     for i in range(NUM_REDUCERS):
#         reducer = Reducer(reducer_queues[i], output_queue, NUM_MAPPERS)
#         reducers.append(reducer)
#         reducer.start()

#     # Step 4: Start mapper processes
#     mappers = []
#     for i in range(NUM_MAPPERS):
#         mapper_dir = os.path.join(BASE_DIR, f'mapper{i}')
#         mapper = Mapper(mapper_dir, reducer_queues)
#         mappers.append(mapper)
#         mapper.start()

#     # Step 5: Wait for all mappers to finish
#     for mapper in mappers:
#         mapper.join()

#     # Step 6: Send a signal to reducers that mapping is complete
#     for q in reducer_queues:
#         q.put(None)

#     # Step 7: Collect results from all reducers
#     final_results = Counter()
#     for _ in reducers:
#         final_results.update(output_queue.get())

#     # Step 8: Write the final results to a file
#     with open('final_output.txt', 'w') as f:
#         for word, count in final_results.items():
#             f.write(f"{word}: {count}\n")

#     # Step 9: Wait for all reducers to finish (after collecting results)
#     for reducer in reducers:
#         reducer.join()

#     # Step 10: (Optional) Cleanup if needed
#     # ...

# if __name__ == '__main__':
#     main()

