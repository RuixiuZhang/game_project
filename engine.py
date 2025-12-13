import math
import random
from ui import get_tile, TILE
ATTACK_WINDUP = 0.08
ATTACK_SWING = 0.22
ATTACK_RECOVER = 0.12

MELEE_RANGE = 32.0
MELEE_ARC_HALF = math.radians(60)

ARROW_SPEED = 170.0
ARROW_RANGE = 150.0

ENEMY_PROJECTILE_SPEED = 120.0
ENEMY_PROJECTILE_RANGE = 120.0

WATER_PLAYER_ARROW_SPREAD = math.radians(12)
NORMAL_PLAYER_ARROW_SPREAD = 0.0

WEAPONS = {
    "Wooden Sword": {"type": "melee", "atk": 6},
    "Stone Sword": {"type": "melee", "atk": 10},
    "Iron Sword": {"type": "melee", "atk": 14},
    "Bow": {"type": "ranged", "atk": 8},
}
def segment_hit(px, py, nx, ny, cx, cy, r):
    vx, vy = nx - px, ny - py
    wx, wy = cx - px, cy - py

    c1 = vx * wx + vy * wy
    if c1 <= 0:
        return (cx - px) ** 2 + (cy - py) ** 2 <= r * r

    c2 = vx * vx + vy * vy
    if c2 <= c1:
        return (cx - nx) ** 2 + (cy - ny) ** 2 <= r * r

    b = c1 / c2
    bx, by = px + b * vx, py + b * vy
    return (cx - bx) ** 2 + (cy - by) ** 2 <= r * r


def terrain_speed_multiplier(tile):
    if tile == "water":
        return 0.45
    if tile == "stone":
        return 0.75
    return 1.0

def effective_atk(player):
    w = player["equipment"]["weapon"]
    return WEAPONS.get(w, {"atk": 6}).get("atk", 6)

def _angle_diff(a, b):
    d = (a - b + math.pi) % (2 * math.pi) - math.pi
    return abs(d)

def start_attack(player, angle, projectiles):
    w = player["equipment"]["weapon"]
    weapon = WEAPONS.get(w, WEAPONS["Wooden Sword"])

    if weapon["type"] == "melee":
        if player["attack_state"] == "idle":
            player["attack_state"] = "windup"
            player["attack_timer"] = 0.0
            player["attack_dir"] = angle
            player["hit_ids"] = set()
        return

    tx = int(player["x"] // TILE)
    ty = int(player["y"] // TILE)
    tile = get_tile(tx, ty)

    spread = random.uniform(-WATER_PLAYER_ARROW_SPREAD, WATER_PLAYER_ARROW_SPREAD) if tile == "water" else NORMAL_PLAYER_ARROW_SPREAD
    ang = angle + spread

    projectiles.append({
        "owner": "player",
        "x": float(player["x"]),
        "y": float(player["y"]),
        "dx": math.cos(ang),
        "dy": math.sin(ang),
        "spd": ARROW_SPEED,
        "dist": 0.0,
        "max_range": ARROW_RANGE,
        "dmg": weapon["atk"],
        "r_hit": 0.75
    })

def update_attack(player, monsters, items, dt):
    if player["attack_state"] == "idle":
        return

    player["attack_timer"] += dt

    if player["attack_state"] == "windup":
        if player["attack_timer"] >= ATTACK_WINDUP:
            player["attack_state"] = "swing"
            player["attack_timer"] = 0.0
        return

    if player["attack_state"] == "swing":
        atk = effective_atk(player)
        for m in monsters[:]:
            if id(m) in player["hit_ids"]:
                continue

            dx = m["x"] - player["x"]
            dy = m["y"] - player["y"]
            dist = math.hypot(dx, dy)

            if dist > MELEE_RANGE:
                continue

            ang = math.atan2(dy, dx)
            if _angle_diff(ang, player["attack_dir"]) <= MELEE_ARC_HALF:
                m["hp"] -= atk
                player["hit_ids"].add(id(m))
                if m["hp"] <= 0:
                    monsters.remove(m)
                    drop_item(items, m)

        if player["attack_timer"] >= ATTACK_SWING:
            player["attack_state"] = "recover"
            player["attack_timer"] = 0.0
        return

    if player["attack_state"] == "recover":
        if player["attack_timer"] >= ATTACK_RECOVER:
            player["attack_state"] = "idle"

def update_projectiles(projectiles, monsters, player, items, dt):
    for p in projectiles[:]:
        step = p["spd"] * dt

        ox, oy = p["x"], p["y"]
        p["x"] += p["dx"] * step
        p["y"] += p["dy"] * step
        p["dist"] += step

        if p["owner"] == "player":
            for m in monsters[:]:
                if segment_hit(
                    ox, oy,
                    p["x"], p["y"],
                    m["x"], m["y"],
                    p["r_hit"] + 0.4
                ):
                    m["hp"] -= p["dmg"]
                    if m["hp"] <= 0:
                        monsters.remove(m)
                        drop_item(items, m)
                    projectiles.remove(p)
                    break

        else:
            if segment_hit(
                ox, oy,
                p["x"], p["y"],
                player["x"], player["y"],
                p["r_hit"]
            ):
                player["hp"] -= p["dmg"]
                projectiles.remove(p)

        if p in projectiles and p["dist"] >= p["max_range"]:
            projectiles.remove(p)


def spawn_monster(monsters, x, y, difficulty=1.0):
    bite_w = max(20, 50 - int(difficulty * 15))
    charge_w = 30 + int(difficulty * 10)
    throw_w = 20 + int(difficulty * 12)

    mtype = random.choices(
        ["bite", "charge", "throw"],
        weights=[bite_w, charge_w, throw_w],
        k=1
    )[0]

    hp = 14
    spd = 2.0
    dmg = 4

    if mtype == "charge":
        hp = 18
        spd = 2.3
        dmg = 6
    elif mtype == "throw":
        hp = 12
        spd = 1.8
        dmg = 3

    monsters.append({
        "x": float(x),
        "y": float(y),
        "hp": hp,
        "max_hp": hp,
        "spd": spd,
        "dmg": dmg,
        "cd": 0.0,
        "type": mtype,
        "state": "idle",
        "charge_cd": 0.0,
        "charge_dir": 0.0
    })

def drop_item(items, m):
    r = random.random()
    if r < 0.22:
        items.append({"type": "weapon", "name": "Bow", "x": m["x"], "y": m["y"]})
    elif r < 0.30:
        items.append({"type": "weapon", "name": "Iron Sword", "x": m["x"], "y": m["y"]})
    else:
        items.append({"type": "material", "name": random.choice(["wood", "stone", "iron"]), "x": m["x"], "y": m["y"]})

def update_monsters(monsters, player, projectiles, dt):
    for m in monsters:
        m["cd"] = max(0.0, m["cd"] - dt)

        dx = player["x"] - m["x"]
        dy = player["y"] - m["y"]
        dist = math.hypot(dx, dy) + 1e-6

        tx = int(m["x"] // TILE)
        ty = int(m["y"] // TILE)
        tile = get_tile(tx, ty)

        base_spd = m["spd"]
        env_mul = terrain_speed_multiplier(tile)

        if m["type"] == "bite":
            m["x"] += (dx / dist) * base_spd * env_mul * dt
            m["y"] += (dy / dist) * base_spd * env_mul * dt
            if dist < 0.95 and m["cd"] <= 0.0:
                player["hp"] -= m["dmg"]
                m["cd"] = 0.6
            continue

        if m["type"] == "charge":
            if tile == "water":
                dash_speed = 3.6
                windup_time = 0.6
                dmg_mul = 1.0
            elif tile == "stone":
                dash_speed = 5.0
                windup_time = 0.4
                dmg_mul = 1.3
            else:
                dash_speed = 6.2
                windup_time = 0.4
                dmg_mul = 1.0

            if m["state"] == "idle":
                m["x"] += (dx / dist) * base_spd * env_mul * dt
                m["y"] += (dy / dist) * base_spd * env_mul * dt
                if dist < 3.0 and m["cd"] <= 0.0:
                    m["state"] = "windup"
                    m["charge_cd"] = windup_time
                    m["charge_dir"] = math.atan2(dy, dx)
                continue

            if m["state"] == "windup":
                m["charge_cd"] -= dt
                if m["charge_cd"] <= 0.0:
                    m["state"] = "dash"
                    m["charge_cd"] = 0.25
                continue

            if m["state"] == "dash":
                m["x"] += math.cos(m["charge_dir"]) * dash_speed * dt
                m["y"] += math.sin(m["charge_dir"]) * dash_speed * dt
                m["charge_cd"] -= dt

                ndx = player["x"] - m["x"]
                ndy = player["y"] - m["y"]
                nd = math.hypot(ndx, ndy) + 1e-6
                if nd < 1.05:
                    player["hp"] -= int(m["dmg"] * 2 * dmg_mul)
                    m["state"] = "idle"
                    m["cd"] = 1.2

                if m["charge_cd"] <= 0.0:
                    m["state"] = "idle"
                    m["cd"] = max(m["cd"], 0.5)
                continue

        if m["type"] == "throw":
            desired_min = 3.0
            desired_max = 6.0

            if dist < desired_min:
                m["x"] -= (dx / dist) * (base_spd * 1.1) * env_mul * dt
                m["y"] -= (dy / dist) * (base_spd * 1.1) * env_mul * dt
            elif dist > desired_max:
                m["x"] += (dx / dist) * (base_spd * 0.9) * env_mul * dt
                m["y"] += (dy / dist) * (base_spd * 0.9) * env_mul * dt

            if desired_min < dist < desired_max and m["cd"] <= 0.0:
                base_angle = math.atan2(dy, dx)
                if tile == "water":
                    spread = random.uniform(-math.radians(18), math.radians(18))
                elif tile == "stone":
                    spread = random.uniform(-math.radians(4), math.radians(4))
                else:
                    spread = random.uniform(-math.radians(8), math.radians(8))

                ang = base_angle + spread
                projectiles.append({
                    "owner": "enemy",
                    "x": float(m["x"]),
                    "y": float(m["y"]),
                    "dx": math.cos(ang),
                    "dy": math.sin(ang),
                    "spd": ENEMY_PROJECTILE_SPEED,
                    "dist": 0.0,
                    "max_range": ENEMY_PROJECTILE_RANGE,
                    "dmg": 3,
                    "r_hit": 0.85
                })
                m["cd"] = 1.2