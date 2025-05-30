import os
import wave
import struct
import numpy as np

def create_placeholder_menu_music():
    """Buat file musik menu placeholder jika belum ada"""
    if not os.path.exists("game/assets/sound/menu.wav"):
        # Pastikan direktori ada
        os.makedirs("game/assets/sound", exist_ok=True)
        
        # Buat file WAV sederhana dengan nada yang berulang
        sample_rate = 44100
        duration = 10  # 10 detik
        
        # Buat array numpy untuk data audio
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        
        # Buat nada yang berulang (chord sederhana)
        note1 = np.sin(2 * np.pi * 440 * t)  # A4
        note2 = np.sin(2 * np.pi * 523.25 * t)  # C5
        note3 = np.sin(2 * np.pi * 659.25 * t)  # E5
        
        # Gabungkan nada dengan amplitudo yang berbeda
        audio = 0.3 * note1 + 0.2 * note2 + 0.2 * note3
        
        # Tambahkan fade in dan fade out
        fade_duration = int(sample_rate * 0.5)  # 0.5 detik
        fade_in = np.linspace(0, 1, fade_duration)
        fade_out = np.linspace(1, 0, fade_duration)
        
        audio[:fade_duration] *= fade_in
        audio[-fade_duration:] *= fade_out
        
        # Normalisasi audio ke range -1 sampai 1
        audio = audio / np.max(np.abs(audio))
        
        # Konversi ke format WAV (16-bit PCM)
        audio = (audio * 32767).astype(np.int16)
        
        # Tulis ke file WAV
        with wave.open("game/assets/sound/menu.wav", "w") as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 2 bytes (16-bit)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(audio.tobytes())
        
        print("Berhasil membuat file musik menu placeholder")

def create_placeholder_alert_sound():
    """Buat file suara alert placeholder jika belum ada"""
    if not os.path.exists("game/assets/sound/alert.wav"):
        # Pastikan direktori ada
        os.makedirs("game/assets/sound", exist_ok=True)
        
        # Buat file WAV sederhana dengan nada alert
        sample_rate = 44100
        duration = 0.5  # 0.5 detik
        
        # Buat array numpy untuk data audio
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        
        # Buat nada alert (frekuensi tinggi yang naik)
        freq = np.linspace(800, 1200, len(t))
        audio = np.sin(2 * np.pi * freq * t)
        
        # Tambahkan sedikit noise untuk efek dramatis
        noise = np.random.uniform(-0.1, 0.1, len(t))
        audio = audio + noise
        
        # Tambahkan envelope (ADSR)
        attack = int(sample_rate * 0.05)
        decay = int(sample_rate * 0.1)
        sustain = int(sample_rate * 0.2)
        release = int(sample_rate * 0.15)
        
        envelope = np.ones(len(audio))
        # Attack
        envelope[:attack] = np.linspace(0, 1, attack)
        # Decay
        envelope[attack:attack+decay] = np.linspace(1, 0.8, decay)
        # Sustain sudah diatur ke 0.8 oleh decay
        # Release
        envelope[-release:] = np.linspace(0.8, 0, release)
        
        audio = audio * envelope
        
        # Normalisasi audio ke range -1 sampai 1
        audio = audio / np.max(np.abs(audio))
        
        # Konversi ke format WAV (16-bit PCM)
        audio = (audio * 32767).astype(np.int16)
        
        # Tulis ke file WAV
        with wave.open("game/assets/sound/alert.wav", "w") as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 2 bytes (16-bit)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(audio.tobytes())
        
        print("Berhasil membuat file suara alert placeholder")

def create_placeholder_game_music():
    """Buat file musik in-game placeholder jika belum ada"""
    if not os.path.exists("game/assets/sound/game.wav"):
        # Pastikan direktori ada
        os.makedirs("game/assets/sound", exist_ok=True)
        
        # Buat file WAV sederhana dengan nada yang berulang
        sample_rate = 44100
        duration = 15  # 15 detik
        
        # Buat array numpy untuk data audio
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        
        # Buat nada yang berulang (chord sederhana dengan ritme berbeda dari menu)
        # Gunakan nada minor untuk suasana tegang/misterius
        note1 = np.sin(2 * np.pi * 220 * t)  # A3
        note2 = np.sin(2 * np.pi * 261.63 * t)  # C4
        note3 = np.sin(2 * np.pi * 329.63 * t)  # E4
        
        # Tambahkan modulasi amplitudo untuk efek detak jantung
        heartbeat = 0.5 + 0.5 * np.sin(2 * np.pi * 0.8 * t)
        
        # Gabungkan nada dengan amplitudo yang berbeda
        audio = 0.2 * note1 + 0.15 * note2 + 0.15 * note3
        
        # Tambahkan efek detak jantung
        audio = audio * (0.7 + 0.3 * heartbeat)
        
        # Tambahkan sedikit noise untuk efek misterius
        noise = np.random.uniform(-0.05, 0.05, len(t))
        audio = audio + noise
        
        # Tambahkan fade in dan fade out
        fade_duration = int(sample_rate * 1.0)  # 1 detik
        fade_in = np.linspace(0, 1, fade_duration)
        fade_out = np.linspace(1, 0, fade_duration)
        
        audio[:fade_duration] *= fade_in
        audio[-fade_duration:] *= fade_out
        
        # Normalisasi audio ke range -1 sampai 1
        audio = audio / np.max(np.abs(audio))
        
        # Konversi ke format WAV (16-bit PCM)
        audio = (audio * 32767).astype(np.int16)
        
        # Tulis ke file WAV
        with wave.open("game/assets/sound/game.wav", "w") as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 2 bytes (16-bit)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(audio.tobytes())
        
        print("Berhasil membuat file musik in-game placeholder")

if __name__ == "__main__":
    create_placeholder_menu_music()
    create_placeholder_alert_sound()
    create_placeholder_game_music()
    print("Semua file suara placeholder telah dibuat")
