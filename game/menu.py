import pygame
import sys
from game.cutscenes.intro import run_cutscene_intro
from game.cutscenes.walkin import run_cutscene_walkin
from game.cutscenes.intro_mission import run_cutscene_intro_mission
from game.maps.gameplay import run_gameplay

def draw_text(screen, font, text, rect, hover=False):
    color = HOVER if hover else WHITE
    label = font.render(text, True, color)
    label_rect = label.get_rect(center=rect.center)
    screen.blit(label, label_rect)

def show_how_to_play(screen, clock):
    # Setup font
    title_font = pygame.font.Font("game/assets/font/Share_Tech_Mono/ShareTechMono-Regular.ttf", 36)
    font = pygame.font.Font("game/assets/font/Share_Tech_Mono/ShareTechMono-Regular.ttf", 24)
    small_font = pygame.font.Font("game/assets/font/Share_Tech_Mono/ShareTechMono-Regular.ttf", 20)
    
    # Judul dan instruksi
    title = "CARA BERMAIN"
    instructions = [
        "KONTROL:",
        "- Klik Kiri: Berjalan ke arah kursor",
        "- Klik Kanan: Berlari ke arah kursor (menghabiskan stamina)",
        "- Tombol C: Jongkok/Berdiri (jongkok untuk bersembunyi di tanaman)",
        "- Tombol ESC: Keluar dari permainan",
        "",
        "TUJUAN PERMAINAN:",
        "1. Kamu berperan sebagai Agen Mangki, seorang agen rahasia yang harus mencuri",
        "   dokumen super rahasia dari Gedung Putih.",
        "2. Kumpulkan semua barang berharga di setiap ruangan untuk memunculkan kunci.",
        "3. Gunakan kunci untuk membuka pintu ke ruangan berikutnya.",
        "4. Hindari penjaga dan laser - jika tertangkap, permainan berakhir!",
        "",
        "TIPS:",
        "- Bersembunyilah di balik tanaman saat penjaga mendekat",
        "- Jongkok untuk mengurangi kebisingan dan visibilitas",
        "- Perhatikan stamina saat berlari",
        "- Laser akan memicu alarm dan menarik perhatian semua penjaga",
        "- Barang akan tertarik ke arahmu saat kamu mendekat",
        ""
    ]
    
    # Loop utama
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_SPACE:
                    running = False
        
        # Gambar latar belakang
        screen.fill((0, 0, 0))
        
        # Gambar judul
        title_surface = title_font.render(title, True, (255, 255, 255))
        title_rect = title_surface.get_rect(center=(screen.get_width() // 2, 80))
        screen.blit(title_surface, title_rect)
        
        # Gambar garis pemisah
        pygame.draw.line(screen, (100, 100, 100), 
                         (100, title_rect.bottom + 20), 
                         (screen.get_width() - 100, title_rect.bottom + 20), 3)
        
        # Gambar instruksi
        y_offset = title_rect.bottom + 60
        for line in instructions:
            if line.startswith("KONTROL:") or line.startswith("TUJUAN PERMAINAN:") or line.startswith("TIPS:"):
                # Gunakan font yang lebih besar untuk judul bagian
                text_surface = font.render(line, True, (255, 200, 0))
            elif line == "":
                # Baris kosong, hanya tambahkan spasi
                y_offset += 10
                continue
            else:
                # Teks instruksi normal
                text_surface = small_font.render(line, True, (200, 200, 200))
            
            text_rect = text_surface.get_rect(midleft=(100, y_offset))
            screen.blit(text_surface, text_rect)
            y_offset += 30
        
        # Gambar indikator "tekan spasi" yang berkedip
        if (pygame.time.get_ticks() // 500) % 2 == 0:  # Berkedip setiap 500ms
            back_text = font.render("Tekan SPASI untuk kembali ke menu", True, (255, 255, 255))
            back_rect = back_text.get_rect(center=(screen.get_width() // 2, screen.get_height() - 50))
            screen.blit(back_text, back_rect)
        
        pygame.display.flip()
        clock.tick(60)

def main_menu():
    # Inisialisasi pygame mixer jika belum diinisialisasi
    if not pygame.mixer.get_init():
        pygame.mixer.init()
    
    # Setup layar
    lebar, tinggi = 1000, 800
    screen = pygame.display.set_mode((lebar, tinggi))
    pygame.display.set_caption("Whitehouse Heist - Main Menu")

    # Load dan putar backsound menu
    try:
        pygame.mixer.music.load("game/assets/sound/menu.wav")
        pygame.mixer.music.set_volume(0.5)  # Set volume ke 50%
        pygame.mixer.music.play(-1)  # -1 berarti loop tanpa batas
    except pygame.error as e:
        print(f"Tidak dapat memuat file musik menu: {e}")

    # Load gambar latar belakang
    background = pygame.image.load("game/assets/background/first.png")
    background = pygame.transform.scale(background, (lebar, tinggi))

    # Load font
    font = pygame.font.Font("game/assets/font/Share_Tech_Mono/ShareTechMono-Regular.ttf", 40)

    # Warna
    global WHITE, DARK, HOVER
    WHITE = (255, 255, 255)
    DARK = (30, 30, 30)
    HOVER = (100, 100, 100)

    # Tombol
    buttons = {
        "Start": pygame.Rect(lebar // 2 - 100, 500, 200, 60),
        "Info": pygame.Rect(lebar // 2 - 100, 580, 200, 60),
        "Quit": pygame.Rect(lebar // 2 - 100, 660, 200, 60)
    }

    # Buat objek clock
    clock = pygame.time.Clock()

    running = True
    while running:
        screen.blit(background, (0, 0))

        mouse_pos = pygame.mouse.get_pos()

        for name, rect in buttons.items():
            is_hover = rect.collidepoint(mouse_pos)
            pygame.draw.rect(screen, DARK, rect, border_radius=12)
            draw_text(screen, font, name, rect, hover=is_hover)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if buttons["Start"].collidepoint(mouse_pos):
                    # Hentikan musik menu saat memulai game
                    pygame.mixer.music.stop()
                    run_cutscene_intro()
                    run_cutscene_intro_mission()
                    run_cutscene_walkin()
                    # Panggil gameplay setelah cutscene
                    run_gameplay()
                    running = False
                elif buttons["Info"].collidepoint(mouse_pos):
                    show_how_to_play(screen, clock)
                elif buttons["Quit"].collidepoint(mouse_pos):
                    pygame.quit()
                    sys.exit()

        pygame.display.flip()
        clock.tick(60)
