import pygame
import sys
import math
from game.utils.constants import *

def run_cutscene_room2():
    # Setup layar
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Whitehouse Heist - Cutscene Ruangan 2")
    
    # Load gambar latar belakang (gunakan gambar ruangan 1 sebagai placeholder)
    try:
        background = pygame.image.load("game/assets/background/cutscene_ruangan2.png")
        background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))
    except pygame.error:
        # Fallback jika gambar tidak ada
        background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        background.fill((0, 0, 0))  # Latar belakang hitam sebagai fallback
    
    # Load font
    font = pygame.font.Font("game/assets/font/Share_Tech_Mono/ShareTechMono-Regular.ttf", 24)
    title_font = pygame.font.Font("game/assets/font/Share_Tech_Mono/ShareTechMono-Regular.ttf", 36)
    
    # Teks cutscene
    title = "Ruangan 2: Aula"
    dialogue = [
    "Mangki: \"Wow, ruangan ini putih sekali. Seperti di rumah sakit jiwa.\"",
    "Narator: \"Ini sayap keamanan. Ada laser dan penjaga yang lebih waspada.\"",
    "Mangki: \"Laser? Asyik! Aku bisa menari ala film Mission Impossible!\"",
    "Narator: \"TIDAK! Itu akan memicu alarm!\"",
    "Mangki: \"Tapi aku sudah latihan gerakan 'Monyet Meliuk di Antara Laser'!\"",
    "Narator: \"Kau BUKAN monyet!\"",
    "Mangki: \"Yaudahhh Yaudahhhh\"",
    "Narator: \"*menghela napas panjang* Fokus saja mencari kunci berikutnya.\""
    ]
    
    # Fungsi untuk memecah teks panjang menjadi beberapa baris
    def wrap_text(text, font, max_width):
        words = text.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            # Coba tambahkan kata ke baris saat ini
            test_line = ' '.join(current_line + [word])
            test_width = font.size(test_line)[0]
            
            if test_width <= max_width:
                current_line.append(word)
            else:
                # Jika baris saat ini sudah penuh, mulai baris baru
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    # Si la palabra es demasiado larga, dividirla
                    if font.size(word)[0] > max_width:
                        # Dividir la palabra carácter por carácter
                        for i in range(len(word)):
                            test_width = font.size(word[:i+1])[0]
                            if test_width > max_width:
                                if i > 0:
                                    lines.append(word[:i])
                                    current_line = [word[i:]]
                                else:
                                    current_line = [word]
                                break
                    else:
                        lines.append(word)
        
        # Tambahkan baris terakhir
        if current_line:
            lines.append(' '.join(current_line))
            
        return lines
    
    # Proses dialog untuk memecah teks panjang
    max_line_width = SCREEN_WIDTH - 300  # Reducido de 200 a 300 para dejar más margen
    
    # Struktur data untuk menyimpan dialog asli dan baris-baris yang dipecah
    dialog_structure = []
    
    for dialog in dialogue:
        wrapped_lines = wrap_text(dialog, font, max_line_width)
        
        # Determine the speaker for this dialogue
        speaker = None
        if dialog.startswith("Narator:"):
            speaker = "Narator"
        elif dialog.startswith("Mangki:"):
            speaker = "Mangki"
            
        dialog_structure.append({
            "original": dialog,
            "wrapped_lines": wrapped_lines,
            "line_count": len(wrapped_lines),
            "speaker": speaker  # Track the speaker for the entire dialogue
        })
    
    # Variabel untuk mengelola dialog
    current_dialog_index = 0  # Indeks dialog saat ini
    current_line_in_dialog = 0  # Indeks baris dalam dialog saat ini
    text_position = 0  # Posisi karakter dalam baris saat ini
    text_speed = 45  # Karakter per frame
    text_timer = 0
    line_spacing = 30  # Spacing antar baris
    
    # Variabel efek fade
    fade_alpha = 255  # Mulai dengan hitam penuh
    fade_speed = 3
    fade_in = True
    fade_out = False
    
    # Variabel untuk efek visual
    time_passed = 0
    
    # Variabel untuk mengelola tampilan dialog
    max_visible_lines = 12  # Maksimum baris yang ditampilkan sekaligus
    
    # Loop utama
    clock = pygame.time.Clock()
    running = True
    text_complete = False
    current_dialog_complete = False
    
    while running:
        dt = clock.tick(60)
        time_passed += dt
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    if current_dialog_complete:
                        # Pindah ke dialog berikutnya
                        if current_dialog_index < len(dialog_structure) - 1:
                            current_dialog_index += 1
                            current_line_in_dialog = 0
                            text_position = 0
                            current_dialog_complete = False
                        else:
                            fade_out = True
                    else:
                        # Jika dialog belum selesai, tampilkan semua teks dialog saat ini
                        current_dialog_complete = True
                        current_line_in_dialog = dialog_structure[current_dialog_index]["line_count"] - 1
                        text_position = len(dialog_structure[current_dialog_index]["wrapped_lines"][current_line_in_dialog])
        
        # Menangani fade in/out
        if fade_in:
            fade_alpha = max(0, fade_alpha - fade_speed)
            if fade_alpha <= 0:
                fade_in = False
        
        if fade_out:
            fade_alpha = min(255, fade_alpha + fade_speed)
            if fade_alpha >= 255:
                running = False
        
        # Update animasi teks
        if not current_dialog_complete:
            text_timer += 1
            if text_timer >= 60 / text_speed:
                text_timer = 0
                text_position += 1
                
                # Jika baris saat ini selesai
                if text_position > len(dialog_structure[current_dialog_index]["wrapped_lines"][current_line_in_dialog]):
                    text_position = len(dialog_structure[current_dialog_index]["wrapped_lines"][current_line_in_dialog])
                    
                    # Jika masih ada baris lain dalam dialog ini
                    if current_line_in_dialog < dialog_structure[current_dialog_index]["line_count"] - 1:
                        current_line_in_dialog += 1
                        text_position = 0
                    else:
                        # Dialog saat ini selesai
                        current_dialog_complete = True
        
        # Gambar latar belakang dengan efek parallax sederhana
        offset_x = int(math.sin(time_passed * 0.0005) * 10)
        offset_y = int(math.cos(time_passed * 0.0003) * 5)
        screen.blit(background, (offset_x, offset_y))
        
        # Overlay gelap semi-transparan untuk seluruh layar
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))  # Hitam dengan 150/255 opacity
        screen.blit(overlay, (0, 0))
        
        # Gambar judul dengan efek bayangan
        shadow_offset = 2
        shadow_color = (0, 0, 0)
        title_shadow = title_font.render(title, True, shadow_color)
        title_surface = title_font.render(title, True, (255, 255, 255))
        
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 100))
        shadow_rect = title_shadow.get_rect(center=(SCREEN_WIDTH // 2 + shadow_offset, 100 + shadow_offset))
        
        screen.blit(title_shadow, shadow_rect)
        screen.blit(title_surface, title_rect)
        
        # Hitung berapa banyak baris yang perlu ditampilkan untuk dialog saat ini dan sebelumnya
        lines_before_current = sum(d["line_count"] for d in dialog_structure[:current_dialog_index])
        lines_in_current = current_line_in_dialog + 1
        
        # Hitung total baris yang perlu ditampilkan
        total_lines = lines_before_current + lines_in_current
        
        # Batasi jumlah baris yang ditampilkan
        visible_lines = min(total_lines, max_visible_lines)
        
        # Hitung tinggi kotak dialog berdasarkan jumlah baris yang ditampilkan
        dialog_padding = 80  # Padding atas dan bawah
        dialog_height = dialog_padding + (visible_lines * line_spacing)
        
        # Pastikan kotak dialog tidak terlalu tinggi
        max_dialog_height = SCREEN_HEIGHT - 200  # Batas maksimum tinggi kotak dialog
        dialog_height = min(dialog_height, max_dialog_height)
        
        # Gambar kotak dialog
        dialog_width = SCREEN_WIDTH - 100
        dialog_box = pygame.Surface((dialog_width, dialog_height), pygame.SRCALPHA)
        dialog_box.fill((0, 0, 0, 180))  # Hitam dengan 180/255 opacity
        
        # Posisikan kotak dialog di bagian bawah layar
        dialog_box_rect = dialog_box.get_rect()
        dialog_box_rect.centerx = SCREEN_WIDTH // 2
        dialog_box_rect.bottom = SCREEN_HEIGHT - 50  # Jarak dari bawah layar
        
        # Tambahkan border ke kotak dialog
        pygame.draw.rect(dialog_box, (255, 255, 255, 50), dialog_box.get_rect(), 2)
        
        screen.blit(dialog_box, dialog_box_rect.topleft)
        
        # Hitung offset untuk scrolling jika ada terlalu banyak baris
        scroll_offset = 0
        if total_lines > max_visible_lines:
            scroll_offset = total_lines - max_visible_lines
        
        # Gambar dialog
        y_offset = 40  # Offset awal dari atas kotak dialog
        
        # Gambar dialog-dialog sebelumnya (yang sudah selesai)
        line_count = 0
        for d_idx in range(current_dialog_index):
            dialog_data = dialog_structure[d_idx]
            speaker = dialog_data["speaker"]
            
            for line in dialog_data["wrapped_lines"]:
                if line_count >= scroll_offset:
                    # Determine text color based on the speaker
                    text_color = (200, 200, 200)  # Default light gray for previous dialogues
                    if speaker == "Narator":
                        text_color = (0, 200, 0)  # Darker green for narrator in previous dialogues
                    elif speaker == "Mangki":
                        text_color = (100, 180, 220)  # Darker light blue for Mangki in previous dialogues
                    
                    text_surface = font.render(line, True, text_color)
                    text_rect = text_surface.get_rect(midleft=(dialog_box_rect.left + 40, dialog_box_rect.top + y_offset))
                    screen.blit(text_surface, text_rect)
                    y_offset += line_spacing
                line_count += 1
        
        # Gambar dialog saat ini
        current_dialog_data = dialog_structure[current_dialog_index]
        current_speaker = current_dialog_data["speaker"]
        
        for l_idx in range(current_line_in_dialog + 1):
            if line_count >= scroll_offset:
                if l_idx < current_line_in_dialog:
                    # Baris yang sudah selesai dalam dialog saat ini
                    line = current_dialog_data["wrapped_lines"][l_idx]
                    
                    # Determine text color based on the speaker
                    text_color = (255, 255, 255)  # Default white
                    if current_speaker == "Narator":
                        text_color = (0, 255, 0)  # Green for narrator
                    elif current_speaker == "Mangki":
                        text_color = (135, 206, 250)  # Light blue for Mangki
                    
                    text_surface = font.render(line, True, text_color)
                    text_rect = text_surface.get_rect(midleft=(dialog_box_rect.left + 40, dialog_box_rect.top + y_offset))
                    screen.blit(text_surface, text_rect)
                else:
                    # Baris yang sedang ditampilkan dengan animasi
                    line = current_dialog_data["wrapped_lines"][l_idx]
                    current_text = line[:text_position]
                    
                    # Determine text color based on the speaker
                    text_color = (255, 255, 255)  # Default white
                    if current_speaker == "Narator":
                        text_color = (0, 255, 0)  # Green for narrator
                    elif current_speaker == "Mangki":
                        text_color = (135, 206, 250)  # Light blue for Mangki
                    
                    text_surface = font.render(current_text, True, text_color)
                    text_rect = text_surface.get_rect(midleft=(dialog_box_rect.left + 40, dialog_box_rect.top + y_offset))
                    screen.blit(text_surface, text_rect)
                y_offset += line_spacing
            line_count += 1
        
        # Gambar indikator "tekan spasi" yang berkedip
        if current_dialog_complete:
            if (time_passed // 500) % 2 == 0:  # Berkedip setiap 500ms
                continue_text = font.render("Tekan SPASI untuk melanjutkan...", True, (255, 255, 255))
                continue_rect = continue_text.get_rect(center=(SCREEN_WIDTH // 2, dialog_box_rect.bottom - 30))
                screen.blit(continue_text, continue_rect)
        
        # Gambar overlay fade
        if fade_in or fade_out:
            fade_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            fade_surface.fill((0, 0, 0, fade_alpha))
            screen.blit(fade_surface, (0, 0))
        
        pygame.display.flip()
    
    # Kembali ke game
    return
