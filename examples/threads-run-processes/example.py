"""
Demonstrates pandoraPlugintools.run_processes: run a function across a
list of items using a bounded pool of processes.

Note: the worker function must be importable (defined at module level,
not as a lambda or a nested function) since it runs in separate
processes.
"""

import pandoraPlugintools as ppt


def worker(item):
    # Runs in a separate process; avoid non-picklable state here.
    return item * item


if __name__ == "__main__":
    items = [1, 2, 3, 4, 5]

    success = ppt.run_processes(
        max_processes=2, function=worker, items=items, print_errors=True
    )

    print("All processes succeeded:", success)
