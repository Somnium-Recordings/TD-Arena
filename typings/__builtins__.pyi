"""
This file ensures that the TD modules defined in the stubs
are available in the global scope when typechecking.

See:
  - https://microsoft.github.io/pyright/#/builtins?id=extending-builtins
  - https://forum.derivative.ca/t/td-stubs-in-vscode/138656/13?u=llwt
"""
from td import *
