import pygame
import threading
import os

from dify_client import talk_to_npc
from event_system import handle_trigger_event

# ================= 工具 =================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def asset(path):
    return os.path.join(BASE_DIR, path)


def load_reimu_image(path, max_width=220, max_height=360):
    img = pygame.image.load(path).convert_alpha()
    w, h = img.get_size()

    scale = min(max_width / w, max_height / h)
    new_size = (int(w * scale), int(h * scale))

    img = pygame.transform.smoothscale(img, new_size)
    return img

# ================= 初始化 =================
pygame.init()
pygame.key.start_text_input()   # 只此一次

screen = pygame.display.set_mode((900, 600))
pygame.display.set_caption("幻想乡 · 博丽灵梦")

clock = pygame.time.Clock()
font = pygame.font.SysFont("simhei", 22)

# ================= 世界状态 =================
world_state = {
    "location": "hakurei_shrine",
    "mode": "dialogue",
    "stories": set()
}

player = {
    "money": 10,
    "reputation": 5
}

reimu = {
    "expression": "lazy"
}

# ================= 立绘 =================
EXPRESSIONS = {
    "lazy": load_reimu_image(asset("assets/reimu/lazy.png")),
    "angry": load_reimu_image(asset("assets/reimu/angry.png")),
    "smile": load_reimu_image(asset("assets/reimu/smile.png")),
    "serious": load_reimu_image(asset("assets/reimu/serious.png"))
}

current_image = EXPRESSIONS["lazy"]

# ================= 对话 =================
input_text = ""
reply_text = "（灵梦懒洋洋地靠在神社柱子上）"
thinking = False


def draw_text(text, x, y, max_width):
    line = ""
    for ch in text:
        if font.size(line + ch)[0] > max_width:
            screen.blit(font.render(line, True, (255, 200, 200)), (x, y))
            y += 26
            line = ch
        else:
            line += ch
    if line:
        screen.blit(font.render(line, True, (255, 200, 200)), (x, y))

def submit_input():
    global input_text, thinking, reply_text

    if thinking or not input_text.strip():
        return

    thinking = True
    reply_text = "（灵梦在思考……）"

    threading.Thread(
        target=request_npc,
        args=(input_text,),
        daemon=True
    ).start()

    input_text = ""
def handle_trigger_event(event, world_state):
    if event is None:
        return

    if isinstance(event, str):
        print("LLM 提示事件：", event)
        return

    if not isinstance(event, dict):
        return

    event_type = event.get("type")
def request_npc(text):
    global reply_text, thinking, current_image

    result = talk_to_npc(
        text,
        inputs={
            "player_money": player["money"],
            "player_reputation": player["reputation"],
            "location": world_state["location"]
        }
    )

    reply_text = result.get("reply", "")
    expr = result.get("expression", "lazy")
    if not isinstance(expr, str):
        expr = "lazy"
    if expr in EXPRESSIONS:
        current_image = EXPRESSIONS[expr]

    handle_trigger_event(result.get("trigger_event"), world_state)

    thinking = False


# ================= 主循环 =================
running = True
while running:
    screen.fill((25, 25, 40))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.TEXTINPUT:
            # 输入法/英文输入
            if not thinking:
                input_text += event.text

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE and not thinking:
                input_text = input_text[:-1]

            elif event.key == pygame.K_RETURN:
                submit_input()

    # ⭐ 绘制顺序：先图片，后文字
    screen.blit(current_image, (20, 120))
    draw_text("灵梦：" + reply_text, 260, 120, 600)
    draw_text("你：" + input_text, 20, 540, 860)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
