"""Centralized PLANS configuration.

Keep plan entries as a list of dicts with keys:
- url: remote PDF URL
- pages: page selection string for camelot (e.g. "1,2")

This module is intentionally a simple Python file so callers can import
`from app.plans import PLANS` without parsing external formats.
"""

PLANS = [
    {
        "url": "https://chiemgau-recycling.de/wp-content/uploads/2025/01/Abfuhrplan_LK_Rosenheim_2025.pdf",
        "pages": "1,2",
    },
]
