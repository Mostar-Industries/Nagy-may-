"""Compatibility shim for backend.shared."""
from importlib import import_module

backend_shared = import_module('backend.shared')

# Expose backend.shared submodules as if they were under this package
__path__ = backend_shared.__path__

for attr in dir(backend_shared):
    if not attr.startswith('_'):
        globals()[attr] = getattr(backend_shared, attr)
