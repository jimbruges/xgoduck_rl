"""Shared CAD inertials and servo timing for XgoDuck tasks."""


def configure_xgoduck_physics(cfg):
    """Keep CAD mass/inertia fixed; 4 ms physics steps at a 50 Hz policy rate.

    BAM's JSON delay (4 ms, 1910_m6.json) is identification metadata in mjlab. The
    actuator delay itself is set in xgoduck_constants.py (delay_min/max_lag, in 4 ms
    physics steps): 2-6 steps, to cover the real runtime's command pipeline.
    Five physics steps retain the existing 20 ms policy/control period.
    """
    cfg.events.pop("randomize_mass_inertia", None)
    cfg.sim.mujoco.timestep = 0.004
    cfg.decimation = 5
    return cfg
