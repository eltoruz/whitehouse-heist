import pygame
import math

class Laser:
    def __init__(self, x1, y1, x2, y2, color=(255, 0, 0), thickness=2, blink_speed=500):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.color = color
        self.thickness = thickness
        self.blink_speed = blink_speed
        self.active = True
        self.timer = 0
        self.triggered = False
        self.trigger_cooldown = 0
        self.trigger_duration = 3000  # 3 detik cooldown setelah trigger
        
        # Hitung bounding box untuk deteksi tabrakan
        self.rect = self._calculate_rect()
        
    def _calculate_rect(self):
        # Buat rect yang mencakup seluruh laser
        left = min(self.x1, self.x2)
        top = min(self.y1, self.y2)
        width = abs(self.x2 - self.x1)
        height = abs(self.y2 - self.y1)
        
        # Pastikan rect memiliki lebar dan tinggi minimal
        if width < 10:
            width = 10
            left -= 5
        if height < 10:
            height = 10
            top -= 5
            
        return pygame.Rect(left, top, width, height)
    
    def update(self, dt, player):
        self.timer += dt
        
        # Blink effect
        if self.timer >= self.blink_speed:
            self.timer = 0
            self.active = not self.active
        
        # Kurangi cooldown jika sedang dalam cooldown
        if self.trigger_cooldown > 0:
            self.trigger_cooldown -= dt
            if self.trigger_cooldown <= 0:
                self.triggered = False
        
        # Cek tabrakan dengan player jika laser aktif
        if self.active and not self.triggered and player:
            # Deteksi tabrakan dengan rect sederhana
            if self.rect.colliderect(player.get_rect()):
                # Deteksi tabrakan yang lebih akurat dengan garis
                player_rect = player.get_rect()
                player_lines = [
                    (player_rect.left, player_rect.top, player_rect.right, player_rect.top),
                    (player_rect.right, player_rect.top, player_rect.right, player_rect.bottom),
                    (player_rect.right, player_rect.bottom, player_rect.left, player_rect.bottom),
                    (player_rect.left, player_rect.bottom, player_rect.left, player_rect.top)
                ]
                
                # Cek apakah garis laser berpotongan dengan salah satu garis player
                for line in player_lines:
                    if self._lines_intersect((self.x1, self.y1, self.x2, self.y2), line):
                        self.triggered = True
                        self.trigger_cooldown = self.trigger_duration
                        return True
        
        return False
    
    def _lines_intersect(self, line1, line2):
        # Implementasi sederhana untuk mengecek apakah dua garis berpotongan
        x1, y1, x2, y2 = line1
        x3, y3, x4, y4 = line2
        
        # Hitung determinan
        den = (y4 - y3) * (x2 - x1) - (x4 - x3) * (y2 - y1)
        
        # Jika determinan 0, garis sejajar atau kolinear
        if den == 0:
            return False
        
        # Hitung parameter t dan u
        ua = ((x4 - x3) * (y1 - y3) - (y4 - y3) * (x1 - x3)) / den
        ub = ((x2 - x1) * (y1 - y3) - (y2 - y1) * (x1 - x3)) / den
        
        # Jika 0 <= ua <= 1 dan 0 <= ub <= 1, garis berpotongan
        return 0 <= ua <= 1 and 0 <= ub <= 1
    
    def draw(self, surface):
        if self.active:
            # Gambar garis laser
            pygame.draw.line(surface, self.color, (self.x1, self.y1), (self.x2, self.y2), self.thickness)
            
            # Gambar titik-titik di ujung laser
            pygame.draw.circle(surface, self.color, (self.x1, self.y1), self.thickness + 2)
            pygame.draw.circle(surface, self.color, (self.x2, self.y2), self.thickness + 2)
            
            # Tambahkan efek glow
            glow_surface = pygame.Surface((surface.get_width(), surface.get_height()), pygame.SRCALPHA)
            for i in range(3):
                thickness = self.thickness + i*2
                alpha = 100 - i*30
                glow_color = self.color + (alpha,)
                pygame.draw.line(glow_surface, glow_color, (self.x1, self.y1), (self.x2, self.y2), thickness)
            
            surface.blit(glow_surface, (0, 0), special_flags=pygame.BLEND_ADD)
