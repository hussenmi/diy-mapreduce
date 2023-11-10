# DIY MapReduce Framework Detailed Description

This document provides a thorough explanation of the MapReduce framework implemented in this project. It covers the different components, their interactions, and the design choices made during the development.

## Overview

A video explaining how the program works and how the files interact can be found [here](https://screenapp.io/app/#/shared/f31a1151-41f6-411a-9996-f9aa89bd5292).

The MapReduce framework is designed to mimic the parallel processing capabilities of the MapReduce programming model, which allows for distributed processing of large data sets across a cluster of computers using a simple programming model.

## Components

The framework comprises three main components:

- `main.py`: The driver script that orchestrates the entire MapReduce process.
- `mapper.py`: Defines the `Mapper` class responsible for the map phase of the MapReduce process.
- `reducer.py`: Defines the `Reducer` class responsible for the reduce phase of the MapReduce process.

### main.py

The `main.py` script acts as the conductor for the MapReduce operation. It performs the following tasks:

1. **Data Splitting**: Depending on the selected method (block-wise or round-robin), the input data is split into chunks that are manageable for each mapper. This is done without loading the entire file into memory to accommodate very large datasets.

2. **Process Initialization**: The script initializes and starts separate processes for each mapper and reducer. The mappers are responsible for processing the data and producing intermediate key-value pairs. The reducers then take these pairs and aggregate them.

3. **Result Aggregation**: After all mappers and reducers have completed their tasks, `main.py` aggregates the results from all reducers into a final output file.

### mapper.py

The `Mapper` class is responsible for reading its chunk of data, processing it line by line, and emitting key-value pairs where the key is a word and the value is the count of 1. These pairs are then distributed to reducers based on a consistent hashing mechanism.

### reducer.py

The `Reducer` class receives key-value pairs from mappers. It aggregates the counts for each word and once all mappers have finished (signaled by an EOF message), it writes the aggregated counts to an output file specific to that reducer.

## Interactions

- Mappers and reducers communicate through multiprocessing queues. This allows for mappers to asynchronously send data to reducers as soon as it's available.
- Each mapper sends an EOF marker to all reducers to signal that it has finished sending data. This allows reducers to know when all mappers have completed their tasks.
- Reducers start processing data as soon as it arrives in their queue, without waiting for all mappers to finish.

## Design Choices

- **Data Splitting**: Two strategies were implemented for splitting data — block-wise and round-robin. The block-wise method divides the file into contiguous chunks that are sent to each mapper. The round-robin method distributes the lines across mappers in a round-robin fashion. Each method has its advantages and can be chosen based on the specific characteristics of the dataset and the processing requirements.
- **Continuous Processing**: When the mappers process a line, they'll put the data into the appropriate reducer's queue, and the reducer that receives the data will get to work right away instead of waiting for all the mapper processes to finish. This is useful in processing a huge amount of, as is usually the case when discussing MapReduce.
- **Hashing**: A consistent hashing function is used to distribute words to reducers. The hd5 hash function was used for this purpose.
- **Simulating Failures**: I killed a mapper and reducer, one at a time to see what the result is going to be like. When I killed a mapper, the system could not finish because the reducers would be waiting for an EOF from that mapper, but since it's dead, it won't give that signal, so the reducers will keep waiting and the program won't terminate. When I kill one of the reducers, the program terminates but it'll only give the result from one of the reducers, and it'll also tell us which reducers have failed.

## Future Improvements

The current framework is a basic implementation and can be extended with features like:

- Adding fault tolerance in case of a mapper or reducer failure to be able to handle all the data.
- Scalability to run across multiple machines in a cluster.