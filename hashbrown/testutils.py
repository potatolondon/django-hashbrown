from functools import wraps

import hashbrown


class SwitchesContext(object):
    def __init__(self, **kwargs):
        self.keys = kwargs
        self.is_active_func = hashbrown.is_active

    def __call__(self, func):
        @wraps(func)
        def inner(*args, **kwargs):
            with self:
                return func(*args, **kwargs)
        return inner

    def __enter__(self):
        self.patch()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.unpatch()

    def patch(self):
        def is_active_patched(tag, user=None):
            return self.keys.get(tag, self.is_active_func(tag))

        hashbrown.is_active = is_active_patched

    def unpatch(self):
        hashbrown.is_active = self.is_active_func


switches = SwitchesContext
