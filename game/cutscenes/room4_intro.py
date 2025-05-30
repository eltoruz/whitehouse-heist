import pygame
import sys
import math
from game.utils.constants import *

def run_cutscene_room4():
    # Setup screen
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Whitehouse Heist - Cutscene Ruangan 4")
    
    # Load background image (use room1 image as placeholder)
    try:
        background = pygame.image.load("game/assets/background/cutscene_ruangan4.png")
        background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))
    except pygame.error:
        # Fallback if image doesn't exist
        background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        background.fill((0, 0, 0))  # Black background as fallback
    
    # Load font
    font = pygame.font.Font("game/assets/font/Share_Tech_Mono/ShareTechMono-Regular.ttf", 24)
    title_font = pygame.font.Font("game/assets/font/Share_Tech_Mono/ShareTechMono-Regular.ttf", 36)
    
    # Cutscene text with funny dialogue
    title = "Ruangan 4: Ruang MENCEKAM"
    dialogue = [
    "Mangki: \"Ruangan terakhir! Aku mencium bau dokumen rahasia!\"",
    "Narator: \"Ini Ruang Oval. Ada penjaga khusus dengan rambut... unik.\"",
    "Mangki: \"Wow! Rambutnya seperti sarang burung oranye! Apa itu asli?\"",
    "Narator: \"Fokus, Mangki! Dokumen ada di tengah ruangan.\"",
    "Mangki: \"Tapi serius, apa rambutnya tidak pernah terbakar saat dekat api?\"",
    "Narator: \"MANGKI!\"",
    "Mangki: \"Oke, oke! Operasi 'Curi Dokumen dari Orang Rambut Api' dimulai!\"",
    "Narator: \"*menghela napas* Kenapa aku selalu dapat agen seperti ini...\""
    ]   
    
    # Function to wrap long text into multiple lines
    def wrap_text(text, font, max_width):
        words = text.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            # Try to add word to current line
            test_line = ' '.join(current_line + [word])
            test_width = font.size(test_line)[0]
            
            if test_width <= max_width:
                current_line.append(word)
            else:
                # If current line is full, start a new line
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    # If word is too long for one line, split the word
                    if font.size(word)[0] > max_width:
                        # Split word character by character
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
        
        # Add the last line
        if current_line:
            lines.append(' '.join(current_line))
            
        return lines
    
    # Process dialogue to wrap long text
    max_line_width = SCREEN_WIDTH - 300  # Reduced from 200 to 300 to leave more margin
    
    # Data structure to store original dialogue and wrapped lines
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
    
    # Variables to manage dialogue
    current_dialog_index = 0  # Current dialogue index
    current_line_in_dialog = 0  # Current line index in current dialogue
    text_position = 0  # Character position in current line
    text_speed = 45  # Characters per frame
    text_timer = 0
    line_spacing = 30  # Spacing between lines
    
    # Fade effect variables
    fade_alpha = 255  # Start with full black
    fade_speed = 3
    fade_in = True
    fade_out = False
    
    # Variables for visual effects
    time_passed = 0
    
    # Variables to manage dialogue display
    max_visible_lines = 12  # Maximum lines displayed at once
    
    # Main loop
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
                        # Move to next dialogue
                        if current_dialog_index < len(dialog_structure) - 1:
                            current_dialog_index += 1
                            current_line_in_dialog = 0
                            text_position = 0
                            current_dialog_complete = False
                        else:
                            fade_out = True
                    else:
                        # If dialogue not complete, show all text of current dialogue
                        current_dialog_complete = True
                        current_line_in_dialog = dialog_structure[current_dialog_index]["line_count"] - 1
                        text_position = len(dialog_structure[current_dialog_index]["wrapped_lines"][current_line_in_dialog])
        
        # Handle fade in/out
        if fade_in:
            fade_alpha = max(0, fade_alpha - fade_speed)
            if fade_alpha <= 0:
                fade_in = False
        
        if fade_out:
            fade_alpha = min(255, fade_alpha + fade_speed)
            if fade_alpha >= 255:
                running = False
        
        # Update text animation
        if not current_dialog_complete:
            text_timer += 1
            if text_timer >= 60 / text_speed:
                text_timer = 0
                text_position += 1
                
                # If current line is complete
                if text_position > len(dialog_structure[current_dialog_index]["wrapped_lines"][current_line_in_dialog]):
                    text_position = len(dialog_structure[current_dialog_index]["wrapped_lines"][current_line_in_dialog])
                    
                    # If there are more lines in this dialogue
                    if current_line_in_dialog < dialog_structure[current_dialog_index]["line_count"] - 1:
                        current_line_in_dialog += 1
                        text_position = 0
                    else:
                        # Current dialogue is complete
                        current_dialog_complete = True
        
        # Draw background with simple parallax effect
        offset_x = int(math.sin(time_passed * 0.0005) * 10)
        offset_y = int(math.cos(time_passed * 0.0003) * 5)
        screen.blit(background, (offset_x, offset_y))
        
        # Semi-transparent dark overlay for entire screen
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))  # Black with 150/255 opacity
        screen.blit(overlay, (0, 0))
        
        # Draw title with shadow effect
        shadow_offset = 2
        shadow_color = (0, 0, 0)
        title_shadow = title_font.render(title, True, shadow_color)
        title_surface = title_font.render(title, True, (255, 255, 255))
        
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 100))
        shadow_rect = title_shadow.get_rect(center=(SCREEN_WIDTH // 2 + shadow_offset, 100 + shadow_offset))
        
        screen.blit(title_shadow, shadow_rect)
        screen.blit(title_surface, title_rect)
        
        # Calculate how many lines need to be displayed for current and previous dialogues
        lines_before_current = sum(d["line_count"] for d in dialog_structure[:current_dialog_index])
        lines_in_current = current_line_in_dialog + 1
        
        # Calculate total lines to be displayed
        total_lines = lines_before_current + lines_in_current
        
        # Limit number of lines displayed
        visible_lines = min(total_lines, max_visible_lines)
        
        # Calculate dialogue box height based on number of lines displayed
        dialog_padding = 80  # Top and bottom padding
        dialog_height = dialog_padding + (visible_lines * line_spacing)
        
        # Ensure dialogue box is not too tall
        max_dialog_height = SCREEN_HEIGHT - 200  # Maximum dialogue box height
        dialog_height = min(dialog_height, max_dialog_height)
        
        # Draw dialogue box
        dialog_width = SCREEN_WIDTH - 100
        dialog_box = pygame.Surface((dialog_width, dialog_height), pygame.SRCALPHA)
        dialog_box.fill((0, 0, 0, 180))  # Black with 180/255 opacity
        
        # Position dialogue box at bottom of screen
        dialog_box_rect = dialog_box.get_rect()
        dialog_box_rect.centerx = SCREEN_WIDTH // 2
        dialog_box_rect.bottom = SCREEN_HEIGHT - 50  # Distance from bottom of screen
        
        # Add border to dialogue box
        pygame.draw.rect(dialog_box, (255, 255, 255, 50), dialog_box.get_rect(), 2)
        
        screen.blit(dialog_box, dialog_box_rect.topleft)
        
        # Calculate offset for scrolling if there are too many lines
        scroll_offset = 0
        if total_lines > max_visible_lines:
            scroll_offset = total_lines - max_visible_lines
        
        # Draw dialogue
        y_offset = 40  # Initial offset from top of dialogue box
        
        # Draw previous dialogues (completed)
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
        
        # Draw current dialogue
        current_dialog_data = dialog_structure[current_dialog_index]
        current_speaker = current_dialog_data["speaker"]
        
        for l_idx in range(current_line_in_dialog + 1):
            if line_count >= scroll_offset:
                if l_idx < current_line_in_dialog:
                    # Completed lines in current dialogue
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
                    # Line currently being displayed with animation
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
        
        # Draw "press space" indicator that blinks
        if current_dialog_complete:
            if (time_passed // 500) % 2 == 0:  # Blink every 500ms
                continue_text = font.render("Tekan SPASI untuk melanjutkan...", True, (255, 255, 255))
                continue_rect = continue_text.get_rect(center=(SCREEN_WIDTH // 2, dialog_box_rect.bottom - 30))
                screen.blit(continue_text, continue_rect)
        
        # Draw fade overlay
        if fade_in or fade_out:
            fade_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            fade_surface.fill((0, 0, 0, fade_alpha))
            screen.blit(fade_surface, (0, 0))
        
        pygame.display.flip()
    
    # Return to game
    return
