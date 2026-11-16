import signal
import unittest
import uuid

import pandoraPlugintools as ppt


def _square(item):
    return item * item


def _add_shared_value(item):
    key, value = item
    ppt.add_shared_dict_value(key, value)


class ThreadsTest(unittest.TestCase):
    def test_run_processes(self):
        self.assertTrue(ppt.run_processes(2, _square, [1, 2, 3, 4]))

    @unittest.skipUnless(hasattr(signal, "SIGALRM"), "SIGALRM is required")
    def test_shared_dict_from_processes(self):
        existing_key = f"existing_{uuid.uuid4().hex}"
        missing_key = f"missing_{uuid.uuid4().hex}"
        ppt.set_shared_dict_value(existing_key, 0)
        items = ([(existing_key, 1)] * 4) + ([(missing_key, 1)] * 4)

        def timeout_handler(signum, frame):
            raise TimeoutError("run_processes deadlocked")

        previous_handler = signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(30)
        try:
            self.assertTrue(ppt.run_processes(2, _add_shared_value, items))
        finally:
            signal.alarm(0)
            signal.signal(signal.SIGALRM, previous_handler)

        self.assertEqual(ppt.get_shared_dict_value(existing_key), 4)
        self.assertEqual(ppt.get_shared_dict_value(missing_key), 4)


if __name__ == "__main__":
    unittest.main()
