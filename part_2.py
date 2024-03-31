# Group #:          33
# Student names:    Rachael Peng, Michael Koon

import threading
import queue
import time, random

def consumerWorker(queue: queue.Queue) -> None:
    """
    The target function for a consumer thread.

    This function runs in an infinite loop, continuously consuming items from the shared queue.
    For each item, it prints a message indicating which thread consumed the item,
    calls `queue.task_done()` to signal that the item has been processed,
    and then sleeps for a random amount of time to simulate work.

    Args:
        queue (queue.Queue): The shared queue from which to consume items.
    """
    # Just do while True as this is a daemon thread (infinite loop)
    while True:
        item = queue.get()  # Get the item from the queue
        print(f"{threading.current_thread().name} consumed item {item}")
        # Decrement the unfinished task counter in the queue, necessary for `queue.join()`
        queue.task_done()
        time.sleep(random.random())  # Introduce some randomness


def producerWorker(queue: queue.Queue) -> None:
    """
    The target function for a producer thread.

    This function runs a loop for a number of times specified by `items_per_producer`, 
    which is defined in the parent thread. In each iteration, it generates a random item 
    within the range specified by `item_range`, puts the item into the shared queue, 
    prints a message indicating which thread produced the item, and then sleeps for a 
    random amount of time to simulate work.

    The `queue.put()` method is thread-safe, so multiple producer threads can safely 
    put items into the queue concurrently.

    Args:
        queue (queue.Queue): The shared queue into which to put items.
    """
    # Producer thread has access to `items_per_producer` defined in the parent thread as threads share memory space
    for _ in range(items_per_producer):  # Just for iterating
        # Gnerate some random item to put, this is config by the tuple `item_range` in the parent threads
        # We pass them to `random.randint()` through unpacking
        item = random.randint(*item_range)
        # Put the item into the queue, noted that `queue.put()` is thread-safe
        queue.put(item)
        print(f"{threading.current_thread().name} produced item {item}")
        time.sleep(random.random())  # Introduce some randomness


if __name__ == "__main__":
    buffer: queue.Queue[int] = queue.Queue() # We will put randint into the queue

    # Use threading module types to create 4 producer threads and 5 consumer threads.
    num_producers = 4
    num_consumers = 5

    # Each producer will put 5 items in total, i.e. total 5 * 4 = 20 items
    items_per_producer = 5

    # Random number range
    item_range = (1, 100)

    # Create, name & start producer threads
    # An array is created to store the producer workers as they are non-daemon and we would need to `.join()` for them
    producers: list[threading.Thread] = []
    for i in range(num_producers):
        t = threading.Thread(target=producerWorker, args=(buffer,), name=f"Producer-{i}")
        t.start()
        producers.append(t)

    # Create, name & start consumer threads
    # Consumers are daemon threads as they will run indefinitely until the buffer is empty 
    # Therefore, we don't need to `.join()` for them and thus no need to store them in an array
    for i in range(num_consumers):
        threading.Thread(target=consumerWorker, args=(buffer,), daemon=True, name=f"Consumer-{i}").start()

    # Wait for all producer threads to finishs
    for p in producers:
        p.join()

    # Wait for the buffer to be empty, i.e. all consumer threads have finished
    # After this is done, we can safely exit the program
    buffer.join()

    # Some additional checks
    print(f"The buffer is empty now: {buffer.empty()}")  # Should be True

    remaining_threads = threading.enumerate()
    print(f"Remaining threads: {len(remaining_threads)}")  # Should be 1 (MainThread) + 5 (num_consumers) = 6
    for thread in remaining_threads: # Should be only the MainThread and the `Consumer-{i}` threads
        print(thread.name)

    # We can then gracefully exit the program as buffer is empty and consumer threads are daemon
    print("All threads have finished, exiting program...")
