import sys
from queue import Queue
from threading import Thread, Lock as _ThreadLock
import multiprocessing as _multiprocessing

####
# Define multi-processing internal global variables.
#########################################################################################

def _get_mp_context():
    """
    Return the multiprocessing context used by this module.

    Pandora FMS plugins are usually plain scripts executed from top to
    bottom, without an ``if __name__ == "__main__"`` guard. Python 3.14
    changed the default start method on Linux to ``forkserver``, which
    re-imports the main script in every worker process and breaks that
    pattern. Use ``fork`` on Linux when available to keep the previous
    behavior, and fall back to the platform default otherwise.
    """
    if sys.platform.startswith("linux"):
        try:
            return _multiprocessing.get_context("fork")
        except ValueError:
            pass

    return _multiprocessing.get_context()

_MP_CONTEXT = _get_mp_context()
_MANAGER = None
_SHARED_DICT = None
_SHARED_DICT_LOCK = None
_SHARED_DICT_INIT_LOCK = _ThreadLock()

def _get_shared_dict():
    """
    Return the shared dictionary and its lock, creating the manager
    lazily on first use.
    """
    global _MANAGER, _SHARED_DICT, _SHARED_DICT_LOCK

    if _SHARED_DICT is not None and _SHARED_DICT_LOCK is not None:
        return _SHARED_DICT, _SHARED_DICT_LOCK

    with _SHARED_DICT_INIT_LOCK:
        if _SHARED_DICT is None or _SHARED_DICT_LOCK is None:
            _MANAGER = _MP_CONTEXT.Manager()
            _SHARED_DICT = _MANAGER.dict()
            _SHARED_DICT_LOCK = _MANAGER.Lock()

    return _SHARED_DICT, _SHARED_DICT_LOCK

def _init_process_shared_dict(
        shared_dict = None,
        shared_dict_lock = None
    ):
    """
    Internal use only: install the parent shared dictionary proxies in a
    worker process.
    """
    global _SHARED_DICT, _SHARED_DICT_LOCK

    if shared_dict is not None:
        _SHARED_DICT = shared_dict
    if shared_dict_lock is not None:
        _SHARED_DICT_LOCK = shared_dict_lock

####
# Internal: Alias for output.print_debug function
#########################################################################################

def _print_debug(
        var = "",
        print_errors: bool = False
    ):
    """
    Prints the provided variable in a JSON-like format.
    
    Args:
        var: The variable (list, dict, string, float, integer) to be printed.
        print_errors (bool): If True, prints any errors that occur during formatting.
    """
    from .output import print_debug
    print_debug(var, print_errors)

####
# Internal use only: Run a given function in a thread
#########################################################################################
def _single_thread(
        q = None,
        function: callable = None,
        errors: list = []
    ):
    """
    Internal use only: Runs a given function in a thread.

    Args:
        q: A queue from which to get parameters for the function.
        function (callable): The function to be executed in the thread.
        errors (list): A list to store any errors encountered during execution.
    """
    params=q.get()
    q.task_done()
    try:
        function(params)
    except Exception as e:
        errors.append("Error while runing single thread: "+str(e))

####
# Run a given function for given items list in a given number of threads
#########################################################################################
def run_threads(
        max_threads: int = 1,
        function: callable = None,
        items: list = [],
        print_errors: bool = False
    ) -> bool:
    """
    Run a given function for a list of items in multiple threads.

    Args:
        max_threads (int): Maximum number of threads to use.
        function (callable): The function to be executed in each thread.
        items (list): List of items to process.
        print_errors (bool): Whether to print errors encountered during execution.

    Returns:
        bool: True if all threads executed successfully, False otherwise.
    """
    from .output import print_stderr

    # Assign threads
    threads = max_threads

    if threads > len(items):
        threads = len(items)

    if threads < 1:
        threads = 1

    # Distribute items per thread
    items_per_thread = []
    thread = 0
    for item in items:
        if not 0 <= thread < len(items_per_thread):
            items_per_thread.append([])
        
        items_per_thread[thread].append(item)

        thread += 1
        if thread >= threads:
            thread=0

    # Run threads
    try:
        q=Queue()
        for n_thread in range(threads) :
            q.put(items_per_thread[n_thread])

        run_threads = []
        errors = []

        for n_thread in range(threads):
            t = Thread(target=_single_thread, args=(q, function, errors))
            t.daemon=True
            t.start()
            run_threads.append(t)

        for t in run_threads:
            t.join()

        q.join()

        if print_errors:
            for error in errors:
                print_stderr(str(error))

        if len(errors) > 0:
            return False
        else:
            return True

    except Exception as e:
        if print_errors:
            print_stderr("Error while running threads: "+str(e))
        return False

####
# Set a given value to a key in the internal shared dict.
# Used by all parallel processes.
#########################################################################################
def set_shared_dict_value(
        key: str = None,
        value = None
    )-> None:
    """
    Set a value for a key in the internal shared dictionary.
    This function is used by all parallel processes.

    Args:
        key (str): The key in the shared dictionary.
        value: The value to be assigned to the key.
    """
    if key is not None:
        shared_dict, shared_dict_lock = _get_shared_dict()
        with shared_dict_lock:
            shared_dict[key] = value

####
# Add a given value to a key in the internal shared dict.
# Used by all parallel processes.
#########################################################################################
def add_shared_dict_value(
        key: str = None,
        value = None
    )-> None:
    """
    Add a value to a key in the internal shared dictionary.
    This function is used by all parallel processes.

    Args:
        key (str): The key in the shared dictionary.
        value: The value to be added to the key.
    """
    if key is not None:
        shared_dict, shared_dict_lock = _get_shared_dict()
        with shared_dict_lock:
            if key in shared_dict:
                shared_dict[key] += value
            else:
                shared_dict[key] = value

####
# Get the value of a key in the internal shared dict.
# Used by all parallel processes.
#########################################################################################
def get_shared_dict_value(
        key: str = None
    ):
    """
    Get the value of a key in the internal shared dictionary.
    This function is used by all parallel processes.

    Args:
        key (str): The key in the shared dictionary.

    Returns:
        The value associated with the key, or None if the key does not exist.
    """
    if key is None:
        return None

    shared_dict, shared_dict_lock = _get_shared_dict()
    with shared_dict_lock:
        if key in shared_dict:
            return shared_dict[key]
        else:
            return None

####
# Run a given function for given items list in a given number of processes
# Given function receives each item as first parameter
#########################################################################################
def run_processes(
        max_processes: int = 1,
        function: callable = None,
        items: list = [],
        print_errors: bool = False
    ) -> bool:
    """
    Run a given function for given items list in a given number of processes

    Args:
        max_processes (int): The maximum number of processes to run in parallel.
        function (callable): The function to be executed for each item.
        items (list): List of items to be processed.
        print_errors (bool): Whether to print errors.

    Returns:
        bool: True if all processes completed successfully, False otherwise.
    """
    from .output import print_stderr

    # Assign processes
    processes = max_processes

    if processes > len(items):
        processes = len(items)

    if processes < 1:
        processes = 1

    # Ensure the shared dictionary manager exists before forking, so worker
    # processes inherit its proxy even when they are the ones writing to it.
    shared_dict, shared_dict_lock = _get_shared_dict()

    # Run processes
    with _MP_CONTEXT.Pool(
            processes,
            initializer=_init_process_shared_dict,
            initargs=(shared_dict, shared_dict_lock)
        ) as pool:
        try:
            pool.map(function, items)
            result = True
        except Exception as error:
            if print_errors:
                print_stderr(str(error))
            result = False

    return result