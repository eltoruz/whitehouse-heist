import pygame
import sys

def run_cutscene_intro():
    pygame.init()

    # Ukuran layar
    WIDTH, HEIGHT = 1000, 800
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Whitehouse Heist - Intro")

    # Load asset
    background = pygame.image.load("game/assets/background/cut_scene_intro.png")
    background = pygame.transform.scale(background, (WIDTH, HEIGHT))

    # Font
    font_path = "game/assets/font/Orbitron/static/Orbitron-Black.ttf"
    font = pygame.font.Font(font_path, 20)
    small_font = pygame.font.Font(font_path, 18)

    # Load suara ketik (pastikan durasi 1 detik)
    typing_sound = pygame.mixer.Sound("game/assets/sound/cutscene1.mp3")
    typing_sound.set_volume(0.3)

    # Cerita lucu
    story = [
        "Tahun 2030. Dunia dalam keadaan damai... membosankan sekali.",
        "Tapi ada satu organisasi rahasia yang selalu bikin onar...",
        "BADAN INTELIJEN SUPER ABSURD (BISA).",
        "Mereka mengirim agen terbaik mereka... MANGKI.",
        "Mangki bukan agen biasa. Dia manusia dengan keahlian monyet.",
        "Misinya? Mencuri dokumen super rahasia dari Gedung Putih.",
        "Dokumen yang katanya berisi rahasia terbesar negara...................... :}"
    ]

    # State teks
    current_line = 0
    char_index = 0
    text_timer = 0
    full_line_displayed = False
    skip_typing = False  # Flag untuk skip animasi ketik

    # Timing
    TYPING_SPEED = 100    # delay antar huruf (ms)
    SOUND_INTERVAL = 800 # jeda antar sound (ms) = 1 detik
    last_sound_time = 0

    # Warna
    WHITE = (255, 255, 255)

    clock = pygame.time.Clock()
    running = True

    # Dialog box
    dialog_height = 180
    dialog_padding = 30

    while running:
        screen.blit(background, (0, 0))

        # Dialog box
        dialog_surface = pygame.Surface((WIDTH, dialog_height))
        dialog_surface.set_alpha(180)
        dialog_surface.fill((0, 0, 0))
        screen.blit(dialog_surface, (0, HEIGHT - dialog_height))

        now = pygame.time.get_ticks()

        # Efek teks ketik (kecuali jika di-skip)
        if not full_line_displayed and not skip_typing and now - text_timer > TYPING_SPEED:
            if char_index < len(story[current_line]):
                char_index += 1
                text_timer = now

                # Mainkan sound hanya jika cukup waktu berlalu dan story belum selesai
                if now - last_sound_time >= SOUND_INTERVAL:
                    typing_sound.play()
                    last_sound_time = now
            else:
                full_line_displayed = True
                typing_sound.stop()  # Stop sound saat teks selesai diketik

        # Jika di-skip, langsung tampilkan seluruh teks
        if skip_typing:
            char_index = len(story[current_line])
            full_line_displayed = True
            typing_sound.stop()
            skip_typing = False

        # Render teks
        display_text = story[current_line][:char_index]
        text_surface = small_font.render(display_text, True, WHITE)
        screen.blit(text_surface, (dialog_padding, HEIGHT - dialog_height + dialog_padding))

        # Prompt untuk lanjut
        if full_line_displayed:
            prompt = small_font.render("Press SPACE to continue...", True, WHITE)
            screen.blit(prompt, (WIDTH // 2 - 130, HEIGHT - 40))

        # Event
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if full_line_displayed:
                    # Lanjut ke kalimat berikutnya
                    current_line += 1
                    if current_line >= len(story):
                        running = False  # cutscene selesai
                    else:
                        char_index = 0
                        full_line_displayed = False
                        skip_typing = False
                        text_timer = pygame.time.get_ticks()
                        last_sound_time = 0  # reset suara untuk baris baru
                else:
                    # Skip animasi ketik untuk kalimat saat ini
                    skip_typing = True

        pygame.display.flip()
        clock.tick(60)
