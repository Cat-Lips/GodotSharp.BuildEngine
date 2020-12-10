import os
import time
import humanize
import functools
import datetime as dt

### Classes ###

class PerfMon:
    def __init__(self, label=None, threshold=1):
        self.label = label
        self.threshold = threshold

    def __enter__(self):
        self.perfStart = time.perf_counter()

    def __exit__(self, exc_type, exception, exc_traceback):
        if exception: return
        duration = time.perf_counter() - self.perfStart
        if duration > self.threshold:
            duration = humanize.precisedelta(duration, minimum_unit='milliseconds')
            print(f'{self.label or "Elapsed Time"}: {duration}')

class Title:
    def __init__(self, title):
        self.title = title

    def __enter__(self):
        self.closure = print_title(self.title)

    def __exit__(self, exc_type, exception, exc_traceback):
        if exception: return
        print_closure(self.closure)

class ScopedEnv:
    def __init__(self, key, value):
        self.key = key
        self.value = value

    def __enter__(self):
        if self.value is None: return
        if self.key in os.environ:
            self.original_value = os.environ[self.key]
            os.environ[self.key] = f'{self.value}{os.pathsep}{self.original_value}'
        else:
            self.original_value = None
            os.environ[self.key] = self.value

    def __exit__(self, exc_type, exception, exc_traceback):
        if self.value is None: return
        if self.original_value:
            os.environ[self.key] = self.original_value
        else:
            del os.environ[self.key]

### Decorators ###

def perf(label=None, threshold=1):
    def _decorator(func):
        @functools.wraps(func)
        def _wrapper(*args, **kwargs):
            with PerfMon(label, threshold):
                return func(*args, **kwargs)
        return _wrapper
    return _decorator

def title(title):
    def _decorator(func):
        @functools.wraps(func)
        def _wrapper(*args, **kwargs):
            with Title(title), PerfMon():
                return func(*args, **kwargs)
        return _wrapper
    return _decorator

def scoped_env(key, value):
    def _decorator(func):
        @functools.wraps(func)
        def _wrapper(*args, **kwargs):
            with ScopedEnv(key, value):
                return func(*args, **kwargs)
        return _wrapper
    return _decorator

### Utilities ###

def print_title(title):
    closure = f'*** [END] {title} [END] ***'
    title = f'*** {title} ***'
    border = '*' * len(title)
    print('', border, title, border, sep='\n')
    return closure

def print_closure(closure):
    border = '*' * len(closure)
    print(border, closure, border, sep='\n')
