# XgoDuck RL

Reinforcement-learning environments for training XgoDuck, a small biped whose geometry and inertia differ from MicroDuck. Policies are trained with PPO on [mjlab](https://github.com/mujocolab/mjlab) (MuJoCo Warp) and exported to ONNX.

## About this fork

This fork of [LuwuDynamics/xgoduck_rl](https://github.com/LuwuDynamics/xgoduck_rl) retrains the walk policy for an XgoDuck built with an Arduino UNO Q, the Luwu expansion board, a 2 × 18650 pack and a clip-on UNO Q cover. Upstream's model is about 27 g light and has its centre of mass too far forward for that build. On the robot, backward walking needed 9–10° of extra lean to hold.

Companion forks:
- [jimbruges/xgoduck_hardware](https://github.com/jimbruges/xgoduck_hardware): the UNO Q cover and the [whole-robot SolidCraft assembly](https://github.com/jimbruges/xgoduck_hardware/blob/master/structure/assembly/xgoduck_full_assembly.solidcraft) ([notes](https://github.com/jimbruges/xgoduck_hardware/blob/master/docs/UNO_Q_COVER.md)) that the mass placement below is taken from.
- [jimbruges/xgoduck_runtime_arduino](https://github.com/jimbruges/xgoduck_runtime_arduino) (branch `calibration-tools`): the runtime that loads these policies, with a **Walk policy** switch for A/B tests and a flight recorder that measures how well the servos follow.

What changes, all in the Flat velocity (walk) task's robot model:

| | Upstream | This fork | Why |
|---|---|---|---|
| Total mass | 798 g | 825 g | Weighed on the assembled robot |
| Trunk inertial | 228.6 g at x −13.3, z −23.6 mm | 255.9 g at x −22.7, z −27.5 mm | Battery (~95 g) inside the body at x −20, z −31 mm and the UNO Q, board, cover and connectors (~48 g) behind it at x −51, z −31 mm, positions from the CAD assembly; inertia from the parallel-axis theorem |
| Whole-robot CoM (trunk frame, zero pose) | x +10.3 mm | x +6.6 mm | Follows from the trunk change |
| Actuator delay | 1 physics step (4 ms) | 2–6 steps (8–24 ms), randomised | On the UNO Q runtime a command reaches the servos about 5–25 ms after the state it was computed from |

The existing ±15 mm centre-of-mass randomisation covers the remaining uncertainty: the CAD has no real part masses, so the 95/48 g split is an estimate. Get-up, pick and the other tasks share the robot model but have not been retrained.

Branches:
- `back-cover` (current): the screw-on back cover design. The UNO Q stack sits 6.9 mm closer to the body, the cover weighs 16 g (the clip-on one 13 g), and the battery mount's screw bosses add 8 g. Total about 836 g (estimated: 825 g weighed with the clip-on cover, plus 11 g). Trunk 266.9 g at x −22.4, z −28.0 mm; whole-robot CoM x +6.3 mm. Exported as `xgoduck_walk_backcover.onnx`.
- `cad-battery`: the table above, for the clip-on cover. Exported as `xgoduck_walk_cadbattery.onnx` in the runtime.
- `real-mass-com`: the first retrain, which put all ~143 g behind the body at x −55 mm (CoM x +2.3 mm). The CAD check showed that over-corrects. Exported as `xgoduck_walk_realcom.onnx`.

Both were trained on Hugging Face Jobs, about 3 h on one L4:

```bash
uv run hf auth login
uv run train Mjlab-Velocity-Flat-XgoDuck --env.scene.num-envs 4096 --agent.max_iterations 4000 \
    --hf-jobs --no-wandb --namespace <you> --run-name xgoduck-walk-cadbattery
```

Then download the last `model_3999.pt` from the checkpoint repo and export it as described under [ONNX](#onnx).

## Acknowledgments

This repository is a downstream project based on [microduck_rl](https://github.com/pollen-robotics/microduck_rl) by [Pollen Robotics](https://github.com/pollen-robotics). Training runs on [mjlab](https://github.com/mujocolab/mjlab). Joint actuation uses [BAM](https://github.com/Rhoban/bam) (Better Actuator Models) from Rhoban.

Thank you to the authors of those projects.

## What is different

The task code follows the MicroDuck recipes, but the robot does not:

- The MJCF and meshes use the XgoDuck model (`src/mjlab_microduck/robot/xgoduck/`).
- Actuators are the HLS1910 BAM model in `src/mjlab_microduck/robot/xgoduck/params/1910_m6.json`, not the MicroDuck XL330.

## Install

You need a CUDA GPU, Python 3.12, and [uv](https://docs.astral.sh/uv/).

```bash
cd xgoduck_rl
uv sync
```

On ARM machines (DGX Spark / GB10, Jetson), the first `uv sync` downloads a large CUDA wheel and uv's default 30 s HTTP timeout can abort it. Set `UV_HTTP_TIMEOUT=600` for that first sync.

## Train

From the repository root:

```bash
uv run train Mjlab-Velocity-Flat-XgoDuck --env.scene.num-envs 4096
uv run train Mjlab-Velocity-Swizzle-XgoDuck --env.scene.num-envs 4096
```

`uv run list-envs` prints every registered task. XgoDuck checkpoints and TensorBoard logs go under `logs/rsl_rl/<experiment>/`.

| Task | Terrain | Experiment directory |
|---|---|---|
| `Mjlab-Velocity-Flat-XgoDuck` | flat | `logs/rsl_rl/xgoduck_velocity/` |
| `Mjlab-Velocity-Rough-XgoDuck` | rough | `logs/rsl_rl/xgoduck_velocity/` |
| `Mjlab-StandUp-Flat-XgoDuck` | flat | `logs/rsl_rl/xgoduck_standup/` |
| `Mjlab-StandUp-Rough-XgoDuck` | rough | `logs/rsl_rl/xgoduck_standup/` |
| `Mjlab-GroundPick-Flat-XgoDuck` | flat | `logs/rsl_rl/xgoduck_ground_pick/` |
| `Mjlab-GroundPick-Rough-XgoDuck` | rough | `logs/rsl_rl/xgoduck_ground_pick/` |
| `Mjlab-SitStand-Flat-XgoDuck` | flat | `logs/rsl_rl/xgoduck_sitstand/` |
| `Mjlab-SitStand-Rough-XgoDuck` | rough | `logs/rsl_rl/xgoduck_sitstand/` |
| `Mjlab-BallKick-Flat-XgoDuck` | flat | `logs/rsl_rl/xgoduck_ball_kick_right/` |
| `Mjlab-BallKick-Left-Flat-XgoDuck` | flat | `logs/rsl_rl/xgoduck_ball_kick_left/` |
| `Mjlab-Roulade-Flat-XgoDuck` | flat | `logs/rsl_rl/xgoduck_roulade/` |
| `Mjlab-Velocity-Swizzle-XgoDuck` | flat | `logs/rsl_rl/xgoduck_velocity_swizzle/` |

## Play

`play` with no checkpoint flag loads the newest `model_*.pt` in that task's experiment directory:

```bash
uv run play Mjlab-Velocity-Flat-XgoDuck
uv run play Mjlab-Velocity-Swizzle-XgoDuck
```

Pass `--checkpoint-file path/to/model_XXXX.pt` to choose a specific checkpoint.

## ONNX

Export bakes observation normalization into the graph. Run it from the repository root and point it at a trained checkpoint:

```bash
uv run python scripts/export.py Mjlab-Velocity-Flat-XgoDuck \
    --checkpoint-file logs/rsl_rl/xgoduck_velocity/<run>/model_XXXX.pt \
    --onnx-file logs/rsl_rl/xgoduck_velocity/<run>/<run>.onnx
```

If you omit `--onnx-file`, the file is written to `output.onnx` in the current directory. `*.onnx` is gitignored. Keep the export next to the run that produced it, for example `logs/rsl_rl/xgoduck_velocity/<run>/<run>.onnx`.

## License

The code is licensed under Apache 2.0. See [LICENSE](LICENSE).
