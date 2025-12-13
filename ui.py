import pygame
import math
import random

PIX_W = 320
PIX_H = 180
TILE = 8

def noise(x, y):
    return (math.sin(x * 0.08) + math.cos(y * 0.08)) * 0.5

def get_tile(x, y):
    n = noise(x, y)
    if n < -0.2:
        return "water"
    if n > 0.4:
        return "stone"
    return "grass"

def draw_world(surface, camera):
    for sy in range(-2, PIX_H // TILE + 2):
        for sx in range(-2, PIX_W // TILE + 2):
            wx = int((sx * TILE + camera["x"]) // TILE)
            wy = int((sy * TILE + camera["y"]) // TILE)
            t = get_tile(wx, wy)
            if t == "grass":
                color = (60, 110, 60)
            elif t == "water":
                color = (50, 90, 140)
            else:
                color = (110, 110, 110)
            surface.fill(
                color,
                (
                    sx * TILE - (camera["x"] % TILE),
                    sy * TILE - (camera["y"] % TILE),
                    TILE,
                    TILE
                )
            )

def draw_monster_hp(surface, m, camera):
    ratio = max(0.0, min(1.0, m["hp"] / m.get("max_hp", 14)))
    x = m["x"] - camera["x"] - 4
    y = m["y"] - camera["y"] - 6
    pygame.draw.rect(surface, (20, 20, 20), (x, y, 8, 2))
    if ratio > 0:
        pygame.draw.rect(surface, (200, 70, 70), (x, y, int(8 * ratio), 2))

def draw_items(surface, items, camera):
    for it in items:
        color = (200, 180, 80) if it["type"] == "material" else (180, 180, 220)
        pygame.draw.rect(
            surface,
            color,
            (it["x"] - camera["x"], it["y"] - camera["y"], 5, 5)
        )

def draw_entities(surface, player, monsters, projectiles, camera):
    px = player["x"] - camera["x"]
    py = player["y"] - camera["y"]
    pygame.draw.rect(surface, (230, 230, 230), (px, py, 4, 4))

    if player["attack_state"] == "swing":
        t = player["attack_timer"] / 0.22
        base = player["attack_dir"]
        a = base - math.pi / 3 + t * (2 * math.pi / 3)
        ex = player["x"] + math.cos(a) * 18
        ey = player["y"] + math.sin(a) * 18
        pygame.draw.line(
            surface,
            (240, 240, 200),
            (px, py),
            (ex - camera["x"], ey - camera["y"]),
            2
        )

    for p in projectiles:
        col = (220, 220, 180) if p["owner"] == "player" else (180, 200, 240)
        x1 = p["x"] - camera["x"]
        y1 = p["y"] - camera["y"]
        x2 = x1 - p["dx"] * 4
        y2 = y1 - p["dy"] * 4
        pygame.draw.line(surface, col, (x1, y1), (x2, y2), 1)

    for m in monsters:
        pygame.draw.rect(
            surface,
            (180, 60, 60),
            (m["x"] - camera["x"], m["y"] - camera["y"], 5, 5)
        )
        draw_monster_hp(surface, m, camera)

def draw_ui(surface, player, llm_text, show_bag, bag_index):
    font = pygame.font.SysFont("arial", 7)

    hp_ratio = max(0.0, min(1.0, player["hp"] / player["max_hp"]))
    san_ratio = max(0.0, min(1.0, player.get("sanity", 100) / player.get("max_sanity", 100)))

    low_san = san_ratio < 0.3
    flicker = low_san and random.random() < 0.15

    ox = random.randint(-1, 1) if flicker else 0
    oy = random.randint(-1, 1) if flicker else 0

    pygame.draw.rect(surface, (30, 10, 10), (4 + ox, 4 + oy, 50, 4))
    pygame.draw.rect(surface, (160, 40, 40), (4 + ox, 4 + oy, int(50 * hp_ratio), 4))

    pygame.draw.rect(surface, (10, 10, 30), (4 + ox, 10 + oy, 50, 4))
    san_color = (120, 120, 220) if not low_san else (160, 160, 255)
    pygame.draw.rect(surface, san_color, (4 + ox, 10 + oy, int(50 * san_ratio), 4))

    surface.blit(
        font.render(f"Weapon: {player['equipment']['weapon']}", True, (220, 220, 220)),
        (PIX_W - 120 + ox, 4 + oy)
    )

    if llm_text:
        surface.blit(
            font.render(llm_text, True, (150, 170, 190)),
            (6 + ox, PIX_H - 12 + oy)
        )

    if not show_bag:
        return

    pygame.draw.rect(surface, (18, 18, 18), (36, 18, 248, 144))
    pygame.draw.rect(surface, (120, 120, 120), (36, 18, 248, 144), 1)

    inv = player["inventory"]
    y = 34
    for i, it in enumerate(inv):
        col = (255, 255, 255) if i == bag_index else (160, 160, 160)
        suffix = "wpn" if it["type"] == "weapon" else "mat"
        surface.blit(font.render(f"{it['name']} {suffix}", True, col), (44, y))
        y += 10

    surface.blit(
        font.render("← → select   space equip   R close", True, (140, 140, 140)),
        (44, 154)
    )