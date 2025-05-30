import pygame
import sys

def run_cutscene_walkin():
    pygame.init()

    # Setup layar
    WIDTH, HEIGHT = 1000, 800
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Whitehouse Heist - Shadow Approaches")

    # Load background
    background = pygame.image.load("game/assets/background/cut_scene_walkin3.png")
    background = pygame.transform.scale(background, (WIDTH, HEIGHT))

    # Load sprite sheet
    sprite_sheet = pygame.image.load("game/assets/sprite/thief.png").convert_alpha()

    FRAME_WIDTH = 48
    FRAME_HEIGHT = 64
    SCALE = 1

    # Baris ke-1 = menghadap depan (arah ke gedung)
    walk_up_frames = []
    for i in range(3):
        frame = sprite_sheet.subsurface((i * FRAME_WIDTH, 0 * FRAME_HEIGHT, FRAME_WIDTH, FRAME_HEIGHT))
        frame = pygame.transform.scale(frame, (FRAME_WIDTH * SCALE, FRAME_HEIGHT * SCALE))
        walk_up_frames.append(frame)

    # Baris ke-2 = jalan ke kiri
    walk_left_frames = []
    for i in range(3):
        frame = sprite_sheet.subsurface((i * FRAME_WIDTH, 1 * FRAME_HEIGHT, FRAME_WIDTH, FRAME_HEIGHT))
        frame = pygame.transform.scale(frame, (FRAME_WIDTH * SCALE, FRAME_HEIGHT * SCALE))
        # Flip horizontal untuk membuat karakter menghadap ke kiri
        frame = pygame.transform.flip(frame, True, False)
        walk_left_frames.append(frame)

    # Posisi awal dari kanan layar
    x = WIDTH
    y = HEIGHT - FRAME_HEIGHT - 50
    current_frame = 0
    frame_timer = 0
    frame_interval = 200
    speed = 4
    clock = pygame.time.Clock()
    phase = "walk_left"  # atau "jump_fence" atau "walk_up"

    jump_progress = 0
    jump_peak = 20  

    running = True
    while running:
        screen.blit(background, (0, 0))

        now = pygame.time.get_ticks()
        if now - frame_timer > frame_interval:
            current_frame = (current_frame + 1) % 3
            frame_timer = now

        # Gerakan karakter
        if phase == "walk_left":
            if x > WIDTH // 2:
                x -= speed
            else:
                phase = "jump_fence"
        elif phase == "jump_fence":
            if jump_progress < jump_peak:
                y -= 4  # naik
            elif jump_progress < 2 * jump_peak:
                y += 4  # turun
            else:
                phase = "walk_up"
            jump_progress += 1
        elif phase == "walk_up":
            y -= speed
            if y < HEIGHT // 3:
                pygame.time.delay(1000)
                running = False

        # Pilih frame sesuai fase
        if phase == "walk_left":
            sprite = walk_left_frames[current_frame]
        else:
            sprite = walk_up_frames[current_frame]

        screen.blit(sprite, (x, y))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        pygame.display.flip()
        clock.tick(60)
