import pygame
from game.utils.constants import *

class Player:
    def __init__(self, x, y, frames, crouch_frames):
        self.x = x
        self.y = y
        self.frames = frames
        self.crouch_frames = crouch_frames
        self.direction = 'down'
        self.frame_index = 0
        self.anim_timer = 0
        self.speed = WALK_SPEED
        self.width = 24 * SCALE
        self.height = 32 * SCALE
        self.is_crouching = False
        self.stealth_bonus = 0
        
        # Tambahkan atribut stamina
        self.max_stamina = 100
        self.stamina = self.max_stamina
        self.stamina_regen_rate = 0.5  # Regenerasi stamina per frame saat jalan/diam
        self.stamina_depletion_rate = 1.0  # Pengurangan stamina per frame saat lari
        self.is_exhausted = False  # Status kelelahan

    def get_rect(self):
        # Adjust collider when crouching (lower height)
        if self.is_crouching:
            return pygame.Rect(self.x + 10, self.y + self.height - 15, self.width - 20, 13)
        else:
            # Regular collider
            return pygame.Rect(self.x + 10, self.y + self.height - 20, self.width - 20, 18)

    def move(self, dx, dy, colliders):
        # Periksa gerakan horizontal
        if dx != 0:
            next_rect = self.get_rect().move(dx, 0)
            if not any(next_rect.colliderect(c) for c in colliders):
                self.x += dx
            else:
                # Coba geser sedikit ke atas atau ke bawah untuk menghindari nyangkut
                slide_amount = 3  # Jumlah piksel untuk mencoba geser
                
                # Coba geser ke atas
                up_rect = self.get_rect().move(dx, -slide_amount)
                if not any(up_rect.colliderect(c) for c in colliders):
                    self.x += dx
                    self.y -= slide_amount
                    return
                
                # Coba geser ke bawah
                down_rect = self.get_rect().move(dx, slide_amount)
                if not any(down_rect.colliderect(c) for c in colliders):
                    self.x += dx
                    self.y += slide_amount
                    return

        # Periksa gerakan vertikal
        if dy != 0:
            next_rect = self.get_rect().move(0, dy)
            if not any(next_rect.colliderect(c) for c in colliders):
                self.y += dy
            else:
                # Coba geser sedikit ke kiri atau ke kanan untuk menghindari nyangkut
                slide_amount = 3  # Jumlah piksel untuk mencoba geser
                
                # Coba geser ke kiri
                left_rect = self.get_rect().move(-slide_amount, dy)
                if not any(left_rect.colliderect(c) for c in colliders):
                    self.x -= slide_amount
                    self.y += dy
                    return
                
                # Coba geser ke kanan
                right_rect = self.get_rect().move(slide_amount, dy)
                if not any(right_rect.colliderect(c) for c in colliders):
                    self.x += slide_amount
                    self.y += dy
                    return

    def toggle_crouch(self):
        self.is_crouching = not self.is_crouching
        if self.is_crouching:
            # When crouching, reduce speed and increase stealth
            self.speed = min(self.speed, CROUCH_SPEED)
            self.stealth_bonus = 50  # Harder for guards to see
        else:
            # When standing up, reset to walk speed if not running
            if self.speed <= CROUCH_SPEED:
                self.speed = WALK_SPEED
            self.stealth_bonus = 0

    def update(self, dt, mouse_held, mouse_pos, colliders):
        # Update stamina
        if self.speed >= RUN_SPEED and mouse_held:
            # Kurangi stamina saat berlari
            self.stamina = max(0, self.stamina - self.stamina_depletion_rate * (dt / 16.67))
            
            # Jika stamina habis, paksa kembali ke kecepatan jalan
            if self.stamina <= 0:
                self.speed = WALK_SPEED
                self.is_exhausted = True
        else:
            # Regenerasi stamina saat tidak berlari
            self.stamina = min(self.max_stamina, self.stamina + self.stamina_regen_rate * (dt / 16.67))
            
            # Jika stamina sudah cukup, pemain tidak lagi kelelahan
            if self.stamina > self.max_stamina * 0.3:
                self.is_exhausted = False
        
        if mouse_held:
            dx = mouse_pos[0] - self.x
            dy = mouse_pos[1] - self.y
            distance = (dx**2 + dy**2)**0.5
            if distance != 0:
                dir_x = dx / distance
                dir_y = dy / distance
                
                # Jika kelelahan, paksa kecepatan jalan
                if self.is_exhausted and self.speed > WALK_SPEED:
                    self.speed = WALK_SPEED
                
                move_x = dir_x * self.speed
                move_y = dir_y * self.speed
                self.move(move_x, move_y, colliders)

                if abs(dx) > abs(dy):
                    self.direction = 'right' if dx > 0 else 'left'
                else:
                    self.direction = 'down' if dy > 0 else 'up'

                self.anim_timer += dt
                if self.anim_timer >= 150:
                    self.frame_index = (self.frame_index + 1) % len(self.frames[self.direction])
                    self.anim_timer = 0
        else:
            self.anim_timer = 0
            self.frame_index = 1

    def draw(self, surface):
        # Use crouch frames if crouching, otherwise use regular frames
        if self.is_crouching:
            frame = self.crouch_frames[self.direction][self.frame_index]
        else:
            frame = self.frames[self.direction][self.frame_index]
        surface.blit(frame, (self.x, self.y))
        
    def draw_stamina_bar(self, surface):
        # Gambar bar stamina di bawah pemain
        bar_width = 40
        bar_height = 5
        bar_x = self.x + (self.width - bar_width) // 2
        bar_y = self.y + self.height + 5
        
        # Background bar (abu-abu)
        pygame.draw.rect(surface, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
        
        # Stamina bar (hijau/kuning/merah berdasarkan level)
        stamina_width = int(bar_width * (self.stamina / self.max_stamina))
        
        # Warna berubah berdasarkan level stamina
        if self.stamina > self.max_stamina * 0.7:
            color = (0, 255, 0)  # Hijau
        elif self.stamina > self.max_stamina * 0.3:
            color = (255, 255, 0)  # Kuning
        else:
            color = (255, 0, 0)  # Merah
            
        pygame.draw.rect(surface, color, (bar_x, bar_y, stamina_width, bar_height))
