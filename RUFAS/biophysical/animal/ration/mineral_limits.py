"""Explicit NRC 2005 tolerable TOTAL dietary minerals, separate from NRC 2001 needs.

Source: NRC, Mineral Tolerance of Animals (2005), doi:10.17226/11309.
These ceilings (Ca 1.5%, P 0.7% of DM) are not recommended concentrations.
No supplement-specific or Ca:P bounds are inferred from these ceilings.
"""

import numpy as np


def calcium_total_upper(x, config):
    return float(np.dot(x, [15.0 - 10.0 * f.calcium for f in config.feeds_used]))


def phosphorus_total_upper(x, config):
    return float(np.dot(x, [7.0 - 10.0 * f.phosphorus for f in config.feeds_used]))


def mineral_report(x, config):
    dm = float(sum(x))
    ca = float(np.dot(x, [10.0 * f.calcium for f in config.feeds_used]))
    p = float(np.dot(x, [10.0 * f.phosphorus for f in config.feeds_used]))
    return dict(
        dry_matter_kg=dm,
        calcium_total_g=ca,
        phosphorus_total_g=p,
        calcium_percent_dm=ca / (10 * dm) if dm else None,
        phosphorus_percent_dm=p / (10 * dm) if dm else None,
        calcium_upper_g=15 * dm,
        phosphorus_upper_g=7 * dm,
        calcium_to_phosphorus=ca / p if p else None,
        tolerable=calcium_total_upper(x, config) >= -1e-6 and phosphorus_total_upper(x, config) >= -1e-6,
        source="NRC 2005 doi:10.17226/11309; total dietary minerals, not absorbed requirements",
    )
