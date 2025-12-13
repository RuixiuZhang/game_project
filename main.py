import math
import random
import threading
import pygame

from engine import (
    terrain_speed_multiplier,
    start_attack,
    update_attack,
    update_projectiles,
    update_monsters,
    spawn_monster
)
from ui import PIX_W, PIX_H, TILE, get_tile, draw_world, draw_items, draw_entities, draw_ui
from llm import llm_worker, llm_queue

pygame.init()
screen = pygame.display.set_mode((PIX_W * 3, PIX_H * 3))
canvas = pygame.Surface((PIX_W, PIX_H))
clock = pygame.time.Clock()

player = {
    "x": 0.0,
    "y": 0.0,
    "speed": 90.0,
    "hp": 100,
    "max_hp": 100,
    "sanity": 100,
    "max_sanity": 100,
    "equipment": {"weapon": "Wooden Sword"},
    "inventory": [],
    "attack_state": "idle",
    "attack_timer": 0.0,
    "attack_dir": 0.0
}

monsters = []
items = []
projectiles = []
camera = {"x": 0.0, "y": 0.0}
llm_text = ""

show_bag = False
bag_index = 0

MAX_MONSTERS = 4
SPAWN_MARGIN = 55


def game_difficulty():
    weapon_bonus = {
        "Wooden Sword": 0.0,
        "Stone Sword": 0.4,
        "Iron Sword": 0.8,
        "Bow": 0.6
    }.get(player["equipment"]["weapon"], 0.0)

    inv_bonus = len(player["inventory"]) * 0.15
    time_bonus = pygame.time.get_ticks() / 1000.0 * 0.01

    return 1.0 + weapon_bonus + inv_bonus + time_bonus


def spawn_monster_at_edge():
    side = random.choice(["left", "right", "top", "bottom"])
    if side == "left":
        x = camera["x"] - SPAWN_MARGIN
        y = camera["y"] + random.randint(0, PIX_H)
    elif side == "right":
        x = camera["x"] + PIX_W + SPAWN_MARGIN
        y = camera["y"] + random.randint(0, PIX_H)
    elif side == "top":
        x = camera["x"] + random.randint(0, PIX_W)
        y = camera["y"] - SPAWN_MARGIN
    else:
        x = camera["x"] + random.randint(0, PIX_W)
        y = camera["y"] + PIX_H + SPAWN_MARGIN

    spawn_monster(monsters, x, y, game_difficulty())


def ctx():
    inv_tail = player["inventory"][-6:]
    return {
        "hp": player["hp"],
        "sanity": int(player["sanity"]),
        "weapon": player["equipment"]["weapon"],
        "monsters": len(monsters),
        "inventory": [f"{it['name']}:{it['type']}" for it in inv_tail]
    }


threading.Thread(target=llm_worker, args=(ctx,), daemon=True).start()

running = True
while running:
    dt = clock.tick(60) / 1000.0

    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False

        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_r:
                show_bag = not show_bag
                bag_index = 0

            if show_bag and e.key == pygame.K_LEFT:
                bag_index = max(0, bag_index - 1)

            if show_bag and e.key == pygame.K_RIGHT:
                if player["inventory"]:
                    bag_index = min(len(player["inventory"]) - 1, bag_index + 1)

            if show_bag and e.key == pygame.K_SPACE and player["inventory"]:
                it = player["inventory"][bag_index]
                if it["type"] == "weapon":
                    old = {"type": "weapon", "name": player["equipment"]["weapon"]}
                    player["equipment"]["weapon"] = it["name"]
                    player["inventory"].pop(bag_index)
                    player["inventory"].append(old)
                    bag_index = 0

        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1 and not show_bag:
            mx, my = pygame.mouse.get_pos()
            wx, wy = mx / 3 + camera["x"], my / 3 + camera["y"]
            ang = math.atan2(wy - player["y"], wx - player["x"])
            start_attack(player, ang, projectiles)

    if len(monsters) < MAX_MONSTERS:
        spawn_chance = 0.018 + game_difficulty() * 0.004
        if random.random() < spawn_chance:
            spawn_monster_at_edge()

    keys = pygame.key.get_pressed()
    if not show_bag:
        vx = keys[pygame.K_d] - keys[pygame.K_a]
        vy = keys[pygame.K_s] - keys[pygame.K_w]
        if vx or vy:
            tile = get_tile(int(player["x"] // TILE), int(player["y"] // TILE))
            mul = terrain_speed_multiplier(tile)
            l = math.hypot(vx, vy)
            player["x"] += (vx / l) * player["speed"] * mul * dt
            player["y"] += (vy / l) * player["speed"] * mul * dt

    update_attack(player, monsters, items, dt)
    update_projectiles(projectiles, monsters, player, items, dt)
    update_monsters(monsters, player, projectiles, dt)

    for it in items[:]:
        if math.hypot(player["x"] - it["x"], player["y"] - it["y"]) < 1.0:
            player["inventory"].append({"type": it["type"], "name": it["name"]})
            items.remove(it)

    near_threat = False
    for m in monsters:
        if math.hypot(player["x"] - m["x"], player["y"] - m["y"]) < 48:
            near_threat = True
            break

    if near_threat:
        pressure = 6.0 + len(monsters) * 1.2
        if player["sanity"] < 30:
            pressure *= 1.6
        player["sanity"] -= dt * pressure
    else:
        if player["sanity"] < 40:
            player["sanity"] += dt * 18.0
        elif player["sanity"] < 70:
            player["sanity"] += dt * 10.0
        else:
            player["sanity"] += dt * 4.0

    player["sanity"] = max(0, min(player["max_sanity"], player["sanity"]))

    camera["x"] = player["x"] - PIX_W / 2
    camera["y"] = player["y"] - PIX_H / 2

    while not llm_queue.empty():
        llm_text = llm_queue.get().get("narrative", "")

    canvas.fill((20, 20, 22))
    draw_world(canvas, camera)
    draw_items(canvas, items, camera)
    draw_entities(canvas, player, monsters, projectiles, camera)
    draw_ui(canvas, player, llm_text, show_bag, bag_index)

    pygame.transform.scale(canvas, screen.get_size(), screen)
    pygame.display.flip()

pygame.quit()
