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

def split_input_file(input_file, num_mappers, base_dir):
    # Ensure the base directory exists
    if os.path.exists(base_dir):
        shutil.rmtree(base_dir)
    os.makedirs(base_dir)
    
    # Read the input file and split into chunks
    with open(input_file, 'r') as f:
        content = f.read()
    
    # Split the content by lines to ensure words are not broken
    lines = content.splitlines()
    chunk_size = len(lines) // num_mappers
    chunks = [lines[i:i + chunk_size] for i in range(0, len(lines), chunk_size)]

    # If there are more lines than mappers, add the remainder to the last chunk
    if len(chunks) > num_mappers:
        chunks[-2].extend(chunks[-1])
        chunks = chunks[:-1]

    # Write chunks to separate directories
    for idx, chunk in enumerate(chunks):
        mapper_dir = os.path.join(base_dir, f'mapper{idx}')
        os.makedirs(mapper_dir)
        with open(os.path.join(mapper_dir, 'input.txt'), 'w') as f:
            f.write('\n'.join(chunk))

def aggregate_results(num_reducers):
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
    # Step 1: Split input file into chunks for mappers
    split_input_file(INPUT_FILE, NUM_MAPPERS, BASE_DIR)

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

    # Step 8: (Optional) Cleanup if needed
    # ...

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

