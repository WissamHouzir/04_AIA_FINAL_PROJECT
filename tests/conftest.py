# tests/conftest.py
class FakeTI:
    def __init__(self):
        self.store = {}

    def xcom_push(self, key, value):
        self.store[key] = value

    def xcom_pull(self, task_ids=None, key=None):
        return self.store.get(key)
