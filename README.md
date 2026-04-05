# Game Project

A 2D top-down survival game with real-time LLM-driven narrative, built in Python.

## Overview

The player navigates a procedurally generated tile world (grass, water, stone), fights monsters, collects loot, and manages HP and sanity — while GPT-4o-mini acts as a live "world director," generating narrative text based on game state.

## Features

- **Procedural terrain** — Infinite tile map using sine/cosine noise. Terrain type (grass / water / stone) affects movement speed, attack accuracy, and enemy behavior.
- **Combat system** — Melee weapons (Wooden Sword → Stone Sword → Iron Sword) with arc-based swing detection, and a ranged Bow with projectile physics.
- **Monster AI** — Three enemy types that scale with dynamic difficulty:
  - **Bite** — Chases and attacks at close range
  - **Charge** — Winds up then dashes at the player
  - **Throw** — Keeps distance and lobs projectiles
- **Sanity mechanic** — Proximity to threats drains sanity; low sanity causes UI flicker and increased pressure. Sanity recovers when safe.
- **Inventory & loot** — Monsters drop weapons and materials. Open the bag to browse and equip items.
- **LLM narrative** — A background thread sends game context (HP, sanity, weapon, inventory, monster count) to GPT-4o-mini every 2 seconds and displays the returned narrative on-screen.

## Controls

| Key | Action |
|---|---|
| W A S D | Move |
| Left click | Attack / Shoot |
| R | Toggle inventory |
| ← → | Navigate inventory |
| Space | Equip selected item |

## Project Structure

| File | Description |
|---|---|
| `main.py` | Game loop, input handling, spawning, camera |
| `engine.py` | Combat, projectiles, monster AI, item drops |
| `ui.py` | Rendering — world tiles, entities, HUD, inventory |
| `llm.py` | Background LLM worker (OpenAI API) |
| `test_envi.py` | Minimal Pygame environment test |
| `Hakurei_Reimu_1.0 version` | Hakurei eimu NPC prototype (agent + PyCharm) |

## Requirements

- Python 3
- Pygame
- `openai` Python package
- An OpenAI API key (provided via a local `api.py` module)

## Running

```bash
python main.py
```

## Contributors

- [RuixiuZhang](https://github.com/RuixiuZhang)
- [Alumin-Hydro](https://github.com/Alumin-Hydro)

*A project by SDSZ 2028 Class 21 students.*

## License

[Unlicense](LICENSE)
