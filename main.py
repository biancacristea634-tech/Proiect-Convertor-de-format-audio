from pydub import AudioSegment
import os
import imageio_ffmpeg

# Leagă pydub de FFmpeg-ul instalat automat
AudioSegment.converter = imageio_ffmpeg.get_ffmpeg_exe()

def converteste_audio(input_file, output_format="mp3", bitrate="192k", sample_rate=None):
    if not os.path.exists(input_file):
        print(f"Eroare: Fișierul {input_file} nu există!")
        return

    print(f"Se procesează fișierul: {input_file}...")
    
    # 1. Încărcarea fișierului audio
    audio = AudioSegment.from_file(input_file)
    
    # 2. Modificarea ratei de eșantionare (Sample Rate)
    if sample_rate:
        audio = audio.set_frame_rate(sample_rate)
        print(f"-> Rata de eșantionare setată la: {sample_rate} Hz")

    # Generarea numelui de ieșire
    base_name = os.path.splitext(input_file)[0]
    output_file = f"{base_name}_conversie.{output_format}"

    # 3. Exportul în MP3
    if output_format == "mp3":
        audio.export(output_file, format=output_format, bitrate=bitrate)
        print(f"-> Calitate (Bitrate) setată la: {bitrate}")
    else:
        audio.export(output_file, format=output_format)

    print(f"Succes! Fișierul a fost salvat ca: {output_file}\n")

if __name__ == "__main__":
    fisier_intrare = "melodie.wav" 
    converteste_audio(fisier_intrare, output_format="mp3", bitrate="320k", sample_rate=44100)