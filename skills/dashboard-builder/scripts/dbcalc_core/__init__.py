"""dbcalc_core — deterministic computation layer for the dashboard-builder skill.

Standard library only (openpyxl is optional, for .xlsx input). Every public
function is deterministic: no randomness, no clock reads, stable sort orders,
and no rounding except at presentation (``trace.render``).
"""

VERSION = "0.2.0"
SCRIPT = "dbcalc.py"
