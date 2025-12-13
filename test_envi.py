import pygame
import sys

# 初始化 pygame
pygame.init()

# 创建窗口
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Pygame 基础测试")

# 字体
font = pygame.font.SysFont("Arial", 32)

# 初始位置
x, y = 400, 300
speed = 5

clock = pygame.time.Clock()

while True:
    # 每秒最多 60 帧
    clock.tick(60)

    # 处理事件
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # 键盘输入测试
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        y -= speed
    if keys[pygame.K_s]:
        y += speed
    if keys[pygame.K_a]:
        x -= speed
    if keys[pygame.K_d]:
        x += speed

    # 背景填充
    screen.fill((30, 30, 30))

    # 显示提示文字
    text_surface = font.render("USE W A S D TO MOVE THE BLOCK", True, (255, 255, 255))
    screen.blit(text_surface, (20, 20))

    # 绘制一个方块（模拟玩家）
    pygame.draw.rect(screen, (255, 255, 255), (x - 20, y - 20, 40, 40))

    # 刷新画面
    pygame.display.flip()
