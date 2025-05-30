import pygame
from game.utils.constants import *
from game.entities.player import Player
from game.utils.asset_loader import get_frames
from game.maps.room1 import Room1
from game.maps.room2 import Room2
from game.maps.room3 import Room3
from game.maps.room4 import Room4
from game.cutscenes.room1_intro import run_cutscene_room1
from game.cutscenes.room2_intro import run_cutscene_room2
from game.cutscenes.room3_intro import run_cutscene_room3
from game.cutscenes.room4_intro import run_cutscene_room4
from game.cutscenes.intro_mission import run_cutscene_intro_mission

class GameManager:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Stealth Game Mansion with Thief and Guards")
        self.clock = pygame.time.Clock()
        
        # Initialize game variables
        self.game_over = False
        self.game_over_timer = 0
        self.game_over_duration = 3000
        self.game_completed = False
        self.score = 0
        self.mouse_held = False
        self.mouse_pos = (0, 0)
        
        # Load player
        self.load_player()
        
        # Initialize rooms
        self.rooms = []
        self.current_room_index = 0
        
        # Create rooms
        self.setup_rooms()
        self.current_room = self.rooms[self.current_room_index]
        
        # Load and play in-game background music
        self.load_background_music()
    
    def load_background_music(self):
        """Load and play in-game background music"""
        try:
            pygame.mixer.music.load("game/assets/sound/game.wav")
            pygame.mixer.music.set_volume(0.3)  # Set volume ke 30%
            pygame.mixer.music.play(-1)  # -1 berarti loop tanpa batas
        except pygame.error as e:
            print(f"Tidak dapat memuat file musik in-game: {e}")
    
    def load_player(self):
        # Load player sprite
        sprite_sheet = pygame.image.load("game/assets/player_img/thief.png").convert_alpha()
        FRAME_WIDTH, FRAME_HEIGHT = 24, 32
        frames = {
            'down': get_frames(sprite_sheet, 2, 3, FRAME_WIDTH, FRAME_HEIGHT),
            'left': get_frames(sprite_sheet, 3, 3, FRAME_WIDTH, FRAME_HEIGHT),
            'right': get_frames(sprite_sheet, 1, 3, FRAME_WIDTH, FRAME_HEIGHT),
            'up': get_frames(sprite_sheet, 0, 3, FRAME_WIDTH, FRAME_HEIGHT)
        }

        # Create crouching frames
        crouch_frames = {}
        for direction, direction_frames in frames.items():
            crouch_frames[direction] = []
            for frame in direction_frames:
                crouch_frame = frame.copy()
                new_height = int(frame.get_height() * 0.8)
                crouch_frame = pygame.transform.scale(crouch_frame, (frame.get_width(), new_height))
                final_frame = pygame.Surface((frame.get_width(), frame.get_height()), pygame.SRCALPHA)
                final_frame.blit(crouch_frame, (0, frame.get_height() - new_height))
                crouch_frames[direction].append(final_frame)
        
        # Initialize player
        self.player = Player(9 * TILE_SIZE, 11 * TILE_SIZE, frames, crouch_frames)
        self.player.direction = 'up'
    
    def setup_rooms(self):

        # Create rooms
        
        self.rooms.append(Room1(self))
        self.rooms.append(Room2(self))
        self.rooms.append(Room3(self))
        self.rooms.append(Room4(self))
        
 
        # More rooms can be added here
    
    def show_room_cutscene(self, room_index):
        # Pause background music during cutscene
        pygame.mixer.music.pause()
        
        # Show appropriate cutscene based on room index
        if room_index == 0:
            run_cutscene_room1()
        elif room_index == 1:
            run_cutscene_room2()
        elif room_index == 2:
            run_cutscene_room3()
        elif room_index == 3:
            run_cutscene_room4()
        # Add more cutscenes for additional rooms here
        
        # Resume background music after cutscene
        pygame.mixer.music.unpause()
    
    def stop_all_alert_sounds(self):
        """Hentikan semua suara alert dari semua guard di semua ruangan"""
        for room in self.rooms:
            for guard in room.guards:
                # Hentikan suara alert jika sedang diputar
                if hasattr(guard, 'alert_sound_played') and guard.alert_sound_played:
                    if hasattr(guard, 'alert_sound_channel') and guard.alert_sound_channel and guard.alert_sound_channel.get_busy():
                        guard.alert_sound_channel.stop()
                    guard.alert_sound_played = False
                
                # Reset status emote
                guard.show_emote = False
                guard.emote_timer = 0
    
    def reset_guard_states_in_previous_room(self, previous_room_index):
        """Reset status guard di ruangan sebelumnya ke mode patrol"""
        if 0 <= previous_room_index < len(self.rooms):
            previous_room = self.rooms[previous_room_index]
            for guard in previous_room.guards:
                # Reset status guard ke patrol
                guard.state = "patrol"
                guard.alert_level = 0
                guard.show_emote = False
                guard.emote_timer = 0
                guard.alert_sound_played = False
                
                # Hentikan suara alert jika sedang diputar
                if hasattr(guard, 'alert_sound_channel') and guard.alert_sound_channel and guard.alert_sound_channel.get_busy():
                    guard.alert_sound_channel.stop()
    
    def transition_to_room(self, room_index):
        # Simpan indeks ruangan sebelumnya
        previous_room_index = self.current_room_index
        
        # Hentikan semua suara alert
        self.stop_all_alert_sounds()
        
        # Reset status guard di ruangan sebelumnya
        self.reset_guard_states_in_previous_room(previous_room_index)
        
        # Cleanup resources in the previous room
        if 0 <= previous_room_index < len(self.rooms):
            if hasattr(self.rooms[previous_room_index], 'cleanup'):
                self.rooms[previous_room_index].cleanup()
        
        # Change current room
        self.current_room_index = room_index
        self.current_room = self.rooms[room_index]
        
        # Show cutscene for the room
        self.show_room_cutscene(room_index)
        
        # Position player according to room
        if room_index == 0:  # Room 1
            # If from room 2, position at right door
            if self.player.x < TILE_SIZE * 2:  # If from left (room 2)
                self.player.x = SCREEN_WIDTH - TILE_SIZE * 2
                self.player.y = 5 * TILE_SIZE
        elif room_index == 1:  # Room 2
            # If from room 1, position at right door
            if self.player.x > SCREEN_WIDTH - TILE_SIZE * 2:  # If from right (room 1)
                self.player.x = TILE_SIZE * 2
                self.player.y = 5 * TILE_SIZE
            # If from room 3, position at bottom door
            elif self.player.y < TILE_SIZE * 2:  # If from top (room 3)
                self.player.x = 9 * TILE_SIZE
                self.player.y = 10 * TILE_SIZE
        elif room_index == 2:  # Room 3
            # If from room 2, position at bottom door
            if self.player.y > SCREEN_HEIGHT - TILE_SIZE * 2:  # If from bottom (room 2)
                self.player.x = 9 * TILE_SIZE
                self.player.y = TILE_SIZE * 2
    
    def reset_game(self):
        # Reset player
        self.player.x = 9 * TILE_SIZE
        self.player.y = 11 * TILE_SIZE
        self.player.direction = 'up'
        
        # Hentikan semua suara alert
        self.stop_all_alert_sounds()
        
        # Reset rooms
        self.rooms = []
        self.setup_rooms()
        self.current_room_index = 0
        self.current_room = self.rooms[self.current_room_index]
        
        # Reset game variables
        self.game_over = False
        self.game_over_timer = 0
        self.game_completed = False
        self.score = 0
        
        # Restart background music
        self.load_background_music()
        
        # Show cutscene for first room
        self.show_room_cutscene(self.current_room_index)
    
    def set_game_over(self):
        """Set game over state and stop all sounds"""
        self.game_over = True
        
        # Fade out music
        pygame.mixer.music.fadeout(500)
        
        # Stop all sound effects (termasuk alert)
        pygame.mixer.stop()
    
    def run(self):
        # Font for UI
        font = pygame.font.SysFont(None, 24)
        big_font = pygame.font.SysFont(None, 72)
        
        # Game loop
        running = True
        while running:
            dt = self.clock.tick(60)
            self.mouse_pos = pygame.mouse.get_pos()
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    if event.key == pygame.K_d:
                        self.current_room.show_debug = not self.current_room.show_debug
                    elif event.key == pygame.K_c:
                        # Toggle crouch
                        if self.current_room.player_is_hidden and self.current_room.current_hiding_spot:
                            # Return player to last position before hiding
                            if self.current_room.current_hiding_spot.name in self.current_room.last_positions_before_hiding:
                                saved_x, saved_y = self.current_room.last_positions_before_hiding[self.current_room.current_hiding_spot.name]
                                self.player.x = saved_x
                                self.player.y = saved_y
                                
                                # Remove saved position after using it
                                del self.current_room.last_positions_before_hiding[self.current_room.current_hiding_spot.name]
                            else:
                                # Fallback if no saved position
                                exit_x = self.current_room.current_hiding_spot.rect.centerx
                                exit_y = self.current_room.current_hiding_spot.rect.bottom + 10
                                
                                # Move player to exit position
                                self.player.x = exit_x - self.player.width // 2
                                self.player.y = exit_y
                            
                            # Make sure player is no longer crouching
                            self.player.is_crouching = False
                            self.player.stealth_bonus = 0
                            if self.player.speed <= CROUCH_SPEED:
                                self.player.speed = WALK_SPEED
                        else:
                            # Normal toggle crouch behavior
                            self.player.toggle_crouch()
                        
                        # Update speed based on mouse button
                        if self.mouse_held:
                            if pygame.mouse.get_pressed()[2]:  # Right mouse button
                                if not self.player.is_crouching and not self.player.is_exhausted:
                                    self.player.speed = RUN_SPEED
                            else:  # Left mouse button
                                if not self.player.is_crouching:
                                    self.player.speed = WALK_SPEED
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if not self.player.is_crouching:
                            self.player.speed = WALK_SPEED
                        self.mouse_held = True
                    elif event.button == 3:
                        if not self.player.is_crouching and not self.player.is_exhausted:
                            self.player.speed = RUN_SPEED
                        self.mouse_held = True
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button in (1, 3):
                        self.mouse_held = False
            
            # If game over, show message and reset after a few seconds
            if self.game_over:
                self.game_over_timer += dt
                if self.game_over_timer >= self.game_over_duration:
                    self.reset_game()
                
                # Render game over screen
                self.screen.fill((0, 0, 0))
                self.current_room.draw()
                
                # Draw game over message
                game_over_text = big_font.render("GAME OVER", True, (255, 0, 0))
                text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
                self.screen.blit(game_over_text, text_rect)
                
                # Draw score
                score_text = font.render(f"Score: {self.score}", True, (255, 255, 255))
                self.screen.blit(score_text, (SCREEN_WIDTH//2 - 50, SCREEN_HEIGHT//2 + 50))
                
                pygame.display.flip()
                continue
            
            # If game completed, show victory message
            if self.game_completed:
                # Fade out music when game completed
                pygame.mixer.music.fadeout(1000)
                
                # Render game completed screen
                self.screen.fill((0, 0, 0))
                
                # Draw completion message
                complete_text = big_font.render("LEVEL COMPLETE!", True, (0, 255, 0))
                text_rect = complete_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
                self.screen.blit(complete_text, text_rect)
                
                # Draw score
                score_text = font.render(f"Final Score: {self.score}", True, (255, 255, 255))
                self.screen.blit(score_text, (SCREEN_WIDTH//2 - 70, SCREEN_HEIGHT//2 + 50))
                
                # Draw continue message
                continue_text = font.render("Press ESC to exit", True, (255, 255, 255))
                self.screen.blit(continue_text, (SCREEN_WIDTH//2 - 80, SCREEN_HEIGHT//2 + 100))
                
                pygame.display.flip()
                continue
            
            # Update current room
            self.current_room.update(dt, self.mouse_held, self.mouse_pos)
            
            # Render
            self.screen.fill((0, 0, 0))
            self.current_room.draw()
            
            pygame.display.flip()
        
        # Stop music when exiting game
        pygame.mixer.music.stop()
        pygame.quit()
