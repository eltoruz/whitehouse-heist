import pygame
import math
import random
from game.utils.constants import *

class Guard:
    def __init__(self, x, y, guard_type, patrol_route, frames, guard_data, colliders):
        # Atribut posisi dan tampilan (public)
        self.x = x
        self.y = y
        self.guard_type = guard_type
        self.frames = frames
        self.direction = 'down'
        self.frame_index = 0
        self.anim_timer = 0
        
        # Atribut yang di-enkapsulasi (private/protected)
        self.__speed = guard_data["speed"]  # Private - kecepatan dasar guard
        self.__vision_range = guard_data["vision_range"]  # Private - jangkauan penglihatan
        self.__vision_color = guard_data["color"]  # Private - warna vision cone
        self.__alert_level = 0  # Private - level kewaspadaan (0-100)
        self.__state = "patrol"  # Private - status guard (patrol, alert, chase, search, return)
        
        # Atribut protected (bisa diakses subclass tapi tidak dari luar)
        self._alert_decay_rate = 0.5  # Protected - tingkat penurunan kewaspadaan
        self._alert_threshold = 70  # Protected - batas untuk beralih ke chase
        self._suspicion_threshold = 30  # Protected - batas untuk beralih ke alert
        self._hearing_range = 150  # Protected - jangkauan pendengaran
        self._sound_alert_increase = 20  # Protected - peningkatan kewaspadaan dari suara
        
        # Atribut public yang tetap bisa diakses langsung
        self.width = 24 * SCALE
        self.height = 32 * SCALE
        self.colliders = colliders
        
        # Rute patroli
        self.patrol_route = patrol_route
        self.current_target = 0
        self.wait_timer = 0
        self.wait_duration = 2000
        self.is_waiting = False
        
        # Konversi rute patroli dari koordinat tile ke koordinat pixel
        for i in range(len(self.patrol_route)):
            self.patrol_route[i] = (
                self.patrol_route[i][0] * TILE_SIZE + TILE_SIZE // 2,
                self.patrol_route[i][1] * TILE_SIZE + TILE_SIZE // 2
            )
        
        # Variabel untuk status "alert" (private)
        self.__alert_timer = 0  # Private
        self.__alert_duration = 3000  # Private
        self.last_known_player_pos = None
        
        # Variabel untuk status "search" (private)
        self.__search_points = []  # Private
        self.__current_search_point = 0  # Private
        self.__search_radius = 150  # Private
        self.__search_duration = 10000  # Private
        self.__search_timer = 0  # Private
        
        # Variabel untuk status "return"
        self.return_point = None
        self.return_route_index = 0
        
        # Variabel untuk memanggil bantuan (private)
        self.__can_call_backup = True  # Private
        self.__backup_called = False  # Private
        self.__backup_call_range = 300  # Private
        self.__backup_call_timer = 0  # Private
        self.__backup_call_cooldown = 5000  # Private
        
        # Variabel untuk pathfinding sederhana
        self.path = []
        self.path_index = 0
        self.path_recalculate_timer = 0
        self.path_recalculate_interval = 500
        self.stuck_timer = 0
        self.stuck_threshold = 1000
        self.last_position = (self.x, self.y)

        # Tambahkan atribut untuk emote
        self.show_emote = False
        self.emote_type = "none"
        self.emote_timer = 0
        self.emote_duration = 2000
        
        # Tambahkan atribut untuk suara alert
        self.alert_sound = None
        self.alert_sound_played = False
        self.alert_sound_channel = None
        try:
            self.alert_sound = pygame.mixer.Sound("game/assets/sound/alert.wav")
            self.alert_sound.set_volume(0.7)
        except pygame.error as e:
            print(f"Tidak dapat memuat file suara alert: {e}")

    # GETTER METHODS untuk atribut private
    def get_speed(self):
        """Getter untuk kecepatan guard"""
        return self.__speed
    
    def get_vision_range(self):
        """Getter untuk jangkauan penglihatan"""
        return self.__vision_range
    
    def get_vision_color(self):
        """Getter untuk warna vision cone"""
        return self.__vision_color
    
    def get_alert_level(self):
        """Getter untuk level kewaspadaan"""
        return self.__alert_level
    
    def get_state(self):
        """Getter untuk status guard"""
        return self.__state
    
    def get_alert_timer(self):
        """Getter untuk alert timer"""
        return self.__alert_timer
    
    def get_search_timer(self):
        """Getter untuk search timer"""
        return self.__search_timer
    
    def is_backup_called(self):
        """Getter untuk status backup call"""
        return self.__backup_called
    
    def can_call_backup(self):
        """Getter untuk kemampuan memanggil backup"""
        return self.__can_call_backup

    # SETTER METHODS untuk atribut private (dengan validasi)
    def set_speed(self, speed):
        """Setter untuk kecepatan guard dengan validasi"""
        if speed > 0:
            self.__speed = speed
    
    def set_vision_range(self, range_value):
        """Setter untuk jangkauan penglihatan dengan validasi"""
        if range_value > 0:
            self.__vision_range = range_value
    
    def set_alert_level(self, level):
        """Setter untuk level kewaspadaan dengan validasi"""
        self.__alert_level = max(0, min(100, level))  # Clamp between 0-100
    
    def set_state(self, new_state):
        """Setter untuk status guard dengan validasi"""
        valid_states = ["patrol", "alert", "chase", "search", "return"]
        if new_state in valid_states:
            self.__state = new_state
    
    def reset_alert_timer(self):
        """Method untuk reset alert timer"""
        self.__alert_timer = 0
    
    def reset_search_timer(self):
        """Method untuk reset search timer"""
        self.__search_timer = 0
    
    def set_backup_called(self, called):
        """Setter untuk status backup call"""
        self.__backup_called = called
    
    def set_can_call_backup(self, can_call):
        """Setter untuk kemampuan memanggil backup"""
        self.__can_call_backup = can_call

    # PRIVATE METHODS (internal use only)
    def __increase_alert_level(self, amount):
        """Private method untuk meningkatkan alert level"""
        self.__alert_level = min(100, self.__alert_level + amount)
    
    def __decrease_alert_level(self, amount):
        """Private method untuk menurunkan alert level"""
        self.__alert_level = max(0, self.__alert_level - amount)
    
    def __reset_backup_timer(self):
        """Private method untuk reset backup timer"""
        self.__backup_call_timer = self.__backup_call_cooldown

    # PROTECTED METHODS (bisa diakses subclass)
    def _generate_search_points(self):
        """Protected method untuk membuat titik pencarian"""
        self.__search_points = []
        if self.last_known_player_pos:
            center_x, center_y = self.last_known_player_pos
            for _ in range(5):
                angle = random.uniform(0, 2 * math.pi)
                distance = random.uniform(30, self.__search_radius)
                x = center_x + math.cos(angle) * distance
                y = center_y + math.sin(angle) * distance
                
                x = max(50, min(SCREEN_WIDTH - 50, x))
                y = max(50, min(SCREEN_HEIGHT - 50, y))
                
                self.__search_points.append((x, y))
                
            self.__current_search_point = 0

    # Existing methods dengan modifikasi untuk menggunakan getter/setter
    def get_rect(self):
        return pygame.Rect(self.x + 10, self.y + self.height - 20, self.width - 20, 18)

    def move(self, dx, dy):
        # Periksa gerakan horizontal
        if dx != 0:
            next_rect = self.get_rect().move(dx, 0)
            if not any(next_rect.colliderect(c) for c in self.colliders):
                self.x += dx
            else:
                up_rect = self.get_rect().move(dx, -5)
                down_rect = self.get_rect().move(dx, 5)
                
                if not any(up_rect.colliderect(c) for c in self.colliders):
                    self.x += dx
                    self.y -= 5
                elif not any(down_rect.colliderect(c) for c in self.colliders):
                    self.x += dx
                    self.y += 5

        # Periksa gerakan vertikal
        if dy != 0:
            next_rect = self.get_rect().move(0, dy)
            if not any(next_rect.colliderect(c) for c in self.colliders):
                self.y += dy
            else:
                left_rect = self.get_rect().move(-5, dy)
                right_rect = self.get_rect().move(5, dy)
                
                if not any(left_rect.colliderect(c) for c in self.colliders):
                    self.x -= 5
                    self.y += dy
                elif not any(right_rect.colliderect(c) for c in self.colliders):
                    self.x += 5
                    self.y += dy

    def update(self, dt, player=None, guards=None, hiding_spots=None):
        # Deteksi jika penjaga terjebak
        current_pos = (self.x, self.y)
        if self.__state == "chase":
            dx = current_pos[0] - self.last_position[0]
            dy = current_pos[1] - self.last_position[1]
            movement = math.sqrt(dx*dx + dy*dy)
            
            if movement < 1:
                self.stuck_timer += dt
                if self.stuck_timer > self.stuck_threshold:
                    self.set_state("search")
                    self._generate_search_points()
                    self.stuck_timer = 0
            else:
                self.stuck_timer = 0
        
        self.last_position = current_pos
        
        # Cek perubahan state untuk menghentikan suara alert jika perlu
        previous_state = self.__state
        
        # Update berdasarkan status penjaga
        if self.__state == "patrol":
            self.update_patrol(dt)
        elif self.__state == "alert":
            self.update_alert(dt, player)
        elif self.__state == "chase":
            self.update_chase(dt, player)
        elif self.__state == "search":
            self.update_search(dt)
        elif self.__state == "return":
            self.update_return(dt)
        
        # Jika state berubah dari chase ke state lain, hentikan suara alert
        if previous_state == "chase" and self.__state != "chase":
            self.stop_alert_sound()
            
        # Update emote timer
        if self.show_emote:
            self.emote_timer += dt
            if self.emote_timer >= self.emote_duration:
                self.show_emote = False
                self.emote_timer = 0
                self.alert_sound_played = False
    
        # Cek deteksi pemain jika pemain ada
        if player:
            player_is_hidden = False
            if hiding_spots:
                for spot in hiding_spots:
                    if spot.contains_player(player):
                        player_is_hidden = True
                        break
        
            if not player_is_hidden:
                self.check_player_detection(player, dt)
            
                if self.__alert_level >= self._alert_threshold and self.__state == "chase":
                    self.show_emote = True
                    self.emote_type = "alert"
                    
                    if not self.alert_sound_played and self.alert_sound:
                        self.alert_sound_channel = self.alert_sound.play()
                        self.alert_sound_played = True
                    
                    self.emote_timer = 0
                
            elif self.__state == "chase" and self.__alert_level > 0:
                self.__decrease_alert_level(self._alert_decay_rate * 3 * (dt / 16.67))
            
                if not self.show_emote or self.emote_type != "confused":
                    self.show_emote = True
                    self.emote_type = "confused"
                    self.emote_timer = 0
                    
                    self.stop_alert_sound()
            
        # Update animasi
        self.update_animation(dt)
        
        # Update timer untuk memanggil bantuan
        if self.__backup_call_timer > 0:
            self.__backup_call_timer -= dt
            
        # Kurangi level kewaspadaan secara bertahap jika tidak dalam pengejaran
        if self.__state != "chase" and self.__alert_level > 0:
            self.__decrease_alert_level(self._alert_decay_rate * (dt / 16.67))
            
            if self.__alert_level < self._suspicion_threshold and self.alert_sound_played:
                self.stop_alert_sound()
            
        # Reset status jika level kewaspadaan turun di bawah ambang batas
        if self.__state == "alert" and self.__alert_level < self._suspicion_threshold:
            self.set_state("patrol")
            
    def stop_alert_sound(self):
        """Hentikan suara alert jika sedang diputar"""
        if self.alert_sound_played and self.alert_sound_channel and self.alert_sound_channel.get_busy():
            self.alert_sound_channel.stop()
        self.alert_sound_played = False
            
    def update_animation(self, dt):
        if self.__state != "waiting":
            self.anim_timer += dt
            if self.anim_timer >= 150:
                self.frame_index = (self.frame_index + 1) % len(self.frames[self.direction])
                self.anim_timer = 0
                
    def update_patrol(self, dt):
        if self.is_waiting:
            self.wait_timer += dt
            if self.wait_timer >= self.wait_duration:
                self.is_waiting = False
                self.wait_timer = 0
                self.current_target = (self.current_target + 1) % len(self.patrol_route)
            return
        
        target_x, target_y = self.patrol_route[self.current_target]
        
        dx = target_x - (self.x + self.width // 2)
        dy = target_y - (self.y + self.height // 2)
        distance = (dx**2 + dy**2)**0.5
        
        if distance < 5:
            self.is_waiting = True
            return
        
        if distance > 0:
            dir_x = dx / distance
            dir_y = dy / distance
            
            if abs(dx) > abs(dy):
                self.direction = 'right' if dx > 0 else 'left'
            else:
                self.direction = 'down' if dy > 0 else 'up'
            
            move_x = dir_x * self.__speed
            move_y = dir_y * self.__speed
            self.move(move_x, move_y)
            
    def update_alert(self, dt, player):
        self.__alert_timer += dt
        
        rotation_speed = 0.003
        rotation_angle = (self.__alert_timer * rotation_speed) % (2 * math.pi)
        
        if rotation_angle < math.pi/4 or rotation_angle > 7*math.pi/4:
            self.direction = 'right'
        elif rotation_angle < 3*math.pi/4:
            self.direction = 'down'
        elif rotation_angle < 5*math.pi/4:
            self.direction = 'left'
        else:
            self.direction = 'up'
            
        if self.__alert_level >= self._alert_threshold:
            self.set_state("chase")
            self.last_known_player_pos = (player.x + player.width // 2, player.y + player.height // 2)
            return
            
        if self.__alert_timer >= self.__alert_duration:
            if self.last_known_player_pos:
                self.set_state("search")
                self._generate_search_points()
                self.reset_search_timer()
            else:
                self.set_state("patrol")
            self.reset_alert_timer()
            
    def find_path_around_obstacle(self, start_x, start_y, target_x, target_y):
        potential_points = []
        for angle in range(0, 360, 45):
            rad = math.radians(angle)
            offset_x = math.cos(rad) * TILE_SIZE
            offset_y = math.sin(rad) * TILE_SIZE
            
            test_rect = pygame.Rect(target_x + offset_x - 10, target_y + offset_y - 10, 20, 20)
            if not any(test_rect.colliderect(c) for c in self.colliders):
                potential_points.append((target_x + offset_x, target_y + offset_y))
        
        if potential_points:
            best_point = min(potential_points, key=lambda p: 
                            ((p[0] - target_x)**2 + (p[1] - target_y)**2))
            return [best_point]
        
        return [(start_x, start_y)]
            
    def update_chase(self, dt, player):
        if not player or self.__alert_level < self._suspicion_threshold:
            self.set_state("search")
            self._generate_search_points()
            self.reset_search_timer()
            
            self.stop_alert_sound()
            
            return
            
        self.last_known_player_pos = (player.x + player.width // 2, player.y + player.height // 2)
        
        dx = self.last_known_player_pos[0] - (self.x + self.width // 2)
        dy = self.last_known_player_pos[1] - (self.y + self.height // 2)
        distance = (dx**2 + dy**2)**0.5
        
        if distance < 20:
            return
        
        self.path_recalculate_timer += dt
        if self.path_recalculate_timer > self.path_recalculate_interval or not self.path:
            guard_center_x = self.x + self.width // 2
            guard_center_y = self.y + self.height // 2
            
            direct_path_blocked = False
            for collider in self.colliders:
                if collider.clipline(guard_center_x, guard_center_y, 
                                    self.last_known_player_pos[0], self.last_known_player_pos[1]):
                    direct_path_blocked = True
                    break
            
            if direct_path_blocked:
                self.path = self.find_path_around_obstacle(
                    guard_center_x, guard_center_y,
                    self.last_known_player_pos[0], self.last_known_player_pos[1]
                )
            else:
                self.path = [self.last_known_player_pos]
            
            self.path_index = 0
            self.path_recalculate_timer = 0
            
        if self.path and self.path_index < len(self.path):
            target_x, target_y = self.path[self.path_index]
            
            dx = target_x - (self.x + self.width // 2)
            dy = target_y - (self.y + self.height // 2)
            path_point_distance = (dx**2 + dy**2)**0.5
            
            if path_point_distance < 10:
                self.path_index += 1
                if self.path_index >= len(self.path):
                    self.path = []
                    return
            
            if path_point_distance > 0:
                dir_x = dx / path_point_distance
                dir_y = dy / path_point_distance
                
                if abs(dx) > abs(dy):
                    self.direction = 'right' if dx > 0 else 'left'
                else:
                    self.direction = 'down' if dy > 0 else 'up'
                
                chase_speed = self.__speed * 2.2
                move_x = dir_x * chase_speed
                move_y = dir_y * chase_speed
                self.move(move_x, move_y)
            
    def update_search(self, dt):
        self.__search_timer += dt
        
        if self.__search_timer >= self.__search_duration:
            self.set_state("return")
            self.find_closest_patrol_point()
            return
            
        if not self.__search_points:
            self._generate_search_points()
            return
            
        target_x, target_y = self.__search_points[self.__current_search_point]
        
        dx = target_x - (self.x + self.width // 2)
        dy = target_y - (self.y + self.height // 2)
        distance = (dx**2 + dy**2)**0.5
        
        if distance < 10:
            self.__current_search_point = (self.__current_search_point + 1) % len(self.__search_points)
            self.is_waiting = True
            self.wait_timer = 0
            self.wait_duration = 1000
            return
            
        if self.is_waiting:
            self.wait_timer += dt
            if self.wait_timer >= self.wait_duration:
                self.is_waiting = False
            return
            
        if distance > 0:
            dir_x = dx / distance
            dir_y = dy / distance
            
            if abs(dx) > abs(dy):
                self.direction = 'right' if dx > 0 else 'left'
            else:
                self.direction = 'down' if dy > 0 else 'up'
            
            search_speed = self.__speed * 1.2
            move_x = dir_x * search_speed
            move_y = dir_y * search_speed
            self.move(move_x, move_y)
            
    def find_closest_patrol_point(self):
        min_distance = float('inf')
        closest_index = 0
        
        for i, point in enumerate(self.patrol_route):
            dx = point[0] - (self.x + self.width // 2)
            dy = point[1] - (self.y + self.height // 2)
            distance = (dx**2 + dy**2)**0.5
            
            if distance < min_distance:
                min_distance = distance
                closest_index = i
                
        self.return_route_index = closest_index
        self.return_point = self.patrol_route[closest_index]
            
    def update_return(self, dt):
        if not self.return_point:
            self.find_closest_patrol_point()
            
        target_x, target_y = self.return_point
        
        dx = target_x - (self.x + self.width // 2)
        dy = target_y - (self.y + self.height // 2)
        distance = (dx**2 + dy**2)**0.5
        
        if distance < 10:
            self.set_state("patrol")
            self.current_target = self.return_route_index
            self.return_point = None
            self.is_waiting = True
            self.wait_timer = 0
            return
            
        if distance > 0:
            dir_x = dx / distance
            dir_y = dy / distance
            
            if abs(dx) > abs(dy):
                self.direction = 'right' if dx > 0 else 'left'
            else:
                self.direction = 'down' if dy > 0 else 'up'
            
            move_x = dir_x * self.__speed
            move_y = dir_y * self.__speed
            self.move(move_x, move_y)
            
    def check_player_detection(self, player, dt):
        can_see = self.can_see_player(player)
        can_hear = self.can_hear_player(player)
        
        if can_see:
            player_center_x = player.x + player.width // 2
            player_center_y = player.y + player.height // 2
            guard_center_x = self.x + self.width // 2
            guard_center_y = self.y + self.height // 2
            
            dx = player_center_x - guard_center_x
            dy = player_center_y - guard_center_y
            distance = (dx**2 + dy**2)**0.5
            
            distance_factor = 1 - min(1, distance / self.__vision_range)
            alert_increase = 2 + (8 * distance_factor)
            
            if player.is_crouching:
                alert_increase *= 0.5
                
            self.__increase_alert_level(alert_increase * (dt / 16.67))
            
            self.last_known_player_pos = (player_center_x, player_center_y)
            
            if self.__alert_level >= self._suspicion_threshold and self.__state == "patrol":
                self.set_state("alert")
                self.reset_alert_timer()
                
            if self.__alert_level >= self._alert_threshold:
                self.set_state("chase")
                
            if self.__alert_level >= 80 and self.__can_call_backup and not self.__backup_called:
                self.call_for_backup()
                
        elif can_hear:
            self.__increase_alert_level(self._sound_alert_increase * (dt / 16.67))
            
            if self.__alert_level >= self._suspicion_threshold and self.__state == "patrol":
                self.set_state("alert")
                self.reset_alert_timer()
                
                player_center_x = player.x + player.width // 2
                player_center_y = player.y + player.height // 2
                self.last_known_player_pos = (player_center_x, player_center_y)
                
        if not can_see and not can_hear and self.__state == "chase" and self.alert_sound_played:
            self.stop_alert_sound()
                
    def can_see_player(self, player):
        player_center_x = player.x + player.width // 2
        player_center_y = player.y + player.height // 2
        guard_center_x = self.x + self.width // 2
        guard_center_y = self.y + self.height // 2
        
        dx = player_center_x - guard_center_x
        dy = player_center_y - guard_center_y
        distance = (dx**2 + dy**2)**0.5
        
        effective_range = self.__vision_range
        if player.is_crouching:
            effective_range = max(self.__vision_range - player.stealth_bonus, self.__vision_range * 0.7)
        
        if distance > effective_range:
            return False
        
        angle_to_player = math.atan2(dy, dx)
        
        if self.direction == 'up':
            guard_angle = math.atan2(-1, 0)
        elif self.direction == 'down':
            guard_angle = math.atan2(1, 0)
        elif self.direction == 'left':
            guard_angle = math.atan2(0, -1)
        else:
            guard_angle = math.atan2(0, 1)
        
        angle_diff = abs(angle_to_player - guard_angle)
        angle_diff = min(angle_diff, 2 * math.pi - angle_diff)
        
        fov_rad = math.radians(60) / 2
        
        if angle_diff <= fov_rad:
            segments = 10
            for i in range(1, segments + 1):
                segment_x = guard_center_x + (dx * i / segments)
                segment_y = guard_center_y + (dy * i / segments)
                
                segment_rect = pygame.Rect(segment_x - 2, segment_y - 2, 4, 4)
                
                for collider in self.colliders:
                    if segment_rect.colliderect(collider):
                        return False
                        
            return True
            
        return False
        
    def can_hear_player(self, player):
        player_center_x = player.x + player.width // 2
        player_center_y = player.y + player.height // 2
        guard_center_x = self.x + self.width // 2
        guard_center_y = self.y + self.height // 2
        
        dx = player_center_x - guard_center_x
        dy = player_center_y - guard_center_y
        distance = (dx**2 + dy**2)**0.5
        
        effective_range = self._hearing_range
        
        if player.speed >= RUN_SPEED:
            effective_range *= 1.5
        elif player.is_crouching:
            effective_range *= 0.6
            
        return distance <= effective_range
        
    def call_for_backup(self, guards=None):
        if not self.__can_call_backup or self.__backup_called or self.__backup_call_timer > 0:
            return
            
        self.set_backup_called(True)
        self.__reset_backup_timer()
        
        if guards:
            player_pos = self.last_known_player_pos
            for guard in guards:
                if guard != self:
                    guard_center_x = guard.x + guard.width // 2
                    guard_center_y = guard.y + guard.height // 2
                    
                    dx = guard_center_x - (self.x + self.width // 2)
                    dy = guard_center_y - (self.y + self.height // 2)
                    distance = (dx**2 + dy**2)**0.5
                    
                    if distance <= self.__backup_call_range:
                        guard.set_alert_level(max(guard.get_alert_level(), self._suspicion_threshold))
                        guard.last_known_player_pos = player_pos
                        
                        if guard.get_state() == "patrol":
                            guard.set_state("alert")
                            guard.reset_alert_timer()

    def draw(self, surface):
        self.draw_vision_cone(surface)
        
        frame = self.frames[self.direction][self.frame_index]
        surface.blit(frame, (self.x, self.y))
        
        if self.show_emote:
            emote_x = self.x + self.width + 5
            emote_y = self.y - 10
        
            font = pygame.font.SysFont(None, 24)
            if self.emote_type == "alert":
                emote_text = font.render("!!", True, (255, 0, 0))
            elif self.emote_type == "confused":
                emote_text = font.render("??", True, (255, 255, 0))
        
            surface.blit(emote_text, (emote_x, emote_y))
    
        if self.__alert_level > 0:
            bar_width = 40
            bar_height = 5
            bar_x = self.x + (self.width - bar_width) // 2
            bar_y = self.y - 10
            
            pygame.draw.rect(surface, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
            
            alert_width = int(bar_width * (self.__alert_level / 100))
            
            if self.__alert_level < self._suspicion_threshold:
                color = (0, 255, 0)
            elif self.__alert_level < self._alert_threshold:
                color = (255, 255, 0)
            else:
                color = (255, 0, 0)
                
            pygame.draw.rect(surface, color, (bar_x, bar_y, alert_width, bar_height))
    
    def draw_vision_cone(self, surface):
        center_x = self.x + self.width // 2
        center_y = self.y + self.height // 2
        
        if self.direction == 'up':
            dir_x, dir_y = 0, -1
        elif self.direction == 'down':
            dir_x, dir_y = 0, 1
        elif self.direction == 'left':
            dir_x, dir_y = -1, 0
        else:
            dir_x, dir_y = 1, 0
        
        vision_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        
        angle = math.atan2(dir_y, dir_x)
        fov_rad = math.radians(60)
        
        points = [(center_x, center_y)]
        for i in range(21):
            a = angle - fov_rad/2 + (fov_rad * i / 20)
            end_x = center_x + math.cos(a) * self.__vision_range
            end_y = center_y + math.sin(a) * self.__vision_range
            points.append((end_x, end_y))
        
        if self.__state == "patrol":
            color = self.__vision_color + (30,)
        elif self.__state == "alert":
            color = (255, 255, 0, 40)
        elif self.__state == "chase":
            color = (255, 0, 0, 50)
        else:
            color = (255, 165, 0, 40)
            
        pygame.draw.polygon(vision_surface, color, points)
        surface.blit(vision_surface, (0, 0))

    # Compatibility properties untuk backward compatibility
    @property
    def state(self):
        """Property untuk akses backward compatibility"""
        return self.__state
    
    @state.setter
    def state(self, value):
        """Property setter untuk backward compatibility"""
        self.set_state(value)
    
    @property
    def alert_level(self):
        """Property untuk akses backward compatibility"""
        return self.__alert_level
    
    @alert_level.setter
    def alert_level(self, value):
        """Property setter untuk backward compatibility"""
        self.set_alert_level(value)
    
    @property
    def speed(self):
        """Property untuk akses backward compatibility"""
        return self.__speed
    
    @property
    def vision_range(self):
        """Property untuk akses backward compatibility"""
        return self.__vision_range
