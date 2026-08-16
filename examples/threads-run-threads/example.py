"""
Demonstrates pandoraPlugintools.run_threads: run a function across a
list of items using a bounded pool of threads.
"""

import pandoraPlugintools as ppt


def worker(item):
    ppt.set_shared_dict_value(f"result_{item}", item * item)


items = [1, 2, 3, 4, 5]

success = ppt.run_threads(max_threads=3, function=worker, items=items, print_errors=True)

print("All threads succeeded:", success)

for item in items:
    print(item, "->", ppt.get_shared_dict_value(f"result_{item}"))
