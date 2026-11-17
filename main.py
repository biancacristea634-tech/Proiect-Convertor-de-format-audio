import os
import tkinter as tk
from tkinter import filedialog, messagebox
from pydub import AudioSegment
import imageio_ffmpeg

# Setează motorul ffmpeg
AudioSegment.converter = imageio_ffmpeg.get_ffmpeg_exe()

def converteste_fisier():
    input_path = entry_file.get()
    if not input_path or not os.path.exists(input_path):
        messagebox.showerror("Eroare", "Te rog selectează un fișier audio valid!")
        return
    
    format_ales = var_format.get()
    bitrate_ales = var_bitrate.get()
    sample_rate_ales = int(var_sr.get())
    
    try:
        print("Se procesează semnalul audio...")
        audio = AudioSegment.from_file(input_path)
        
        # Prelucrarea semnalului: Modificarea ratei de eșantionare (Sample Rate)
        audio = audio.set_frame_rate(sample_rate_ales)
        
        base_name = os.path.splitext(input_path)[0]
        output_path = f"{base_name}_procesat.{format_ales}"
        
        # Exportul cu bitrate-ul ales
        if format_ales == "mp3":
            audio.export(output_path, format=format_ales, bitrate=bitrate_ales)
        else:
            audio.export(output_path, format=format_ales)
            
        messagebox.showinfo("Succes!", f"Fișierul a fost salvat ca:\n{output_path}")
    except Exception as e:
        messagebox.showerror("Eroare de procesare", str(e))

def selecteaza_fisier():
    file_path = filedialog.askopenfilename(filetypes=[("Fisiere audio", "*.wav *.mp3 *.flac")])
    if file_path:
        entry_file.delete(0, tk.END)
        entry_file.insert(0, file_path)

# --- Interfața Grafică (GUI) ---
root = tk.Tk()
root.title("Convertor & Prelucrare Semnale Audio")
root.geometry("450x380")
root.resizable(False, False)

# 1. Selectare fișier
tk.Label(root, text="Fișier audio sursă:", font=("Arial", 10, "bold")).pack(pady=5)
frame_file = tk.Frame(root)
frame_file.pack(pady=5)

entry_file = tk.Entry(frame_file, width=35)
entry_file.pack(side=tk.LEFT, padx=5)
tk.Button(frame_file, text="Caută...", command=selecteaza_fisier).pack(side=tk.LEFT)

# 2. Alegere Format Ieșire
tk.Label(root, text="Format de ieșire:", font=("Arial", 10, "bold")).pack(pady=5)
var_format = tk.StringVar(value="mp3")
frame_format = tk.Frame(root)
frame_format.pack()
tk.Radiobutton(frame_format, text="MP3", variable=var_format, value="mp3").pack(side=tk.LEFT, padx=10)
tk.Radiobutton(frame_format, text="WAV", variable=var_format, value="wav").pack(side=tk.LEFT, padx=10)

# 3. Alegere Rată de Eșantionare (Sample Rate)
tk.Label(root, text="Rată de eșantionare (Sample Rate):", font=("Arial", 10, "bold")).pack(pady=5)
var_sr = tk.StringVar(value="44100")
sr_menu = tk.OptionMenu(root, var_sr, "8000", "16000", "22050", "44100", "48000")
sr_menu.pack()

# 4. Alegere Bitrate / Calitate
tk.Label(root, text="Calitate (Bitrate MP3):", font=("Arial", 10, "bold")).pack(pady=5)
var_bitrate = tk.StringVar(value="192k")
bit_menu = tk.OptionMenu(root, var_bitrate, "64k", "128k", "192k", "320k")
bit_menu.pack()

# 5. Buton Conversie
tk.Button(root, text="Convertește și Procesează", bg="green", fg="white", font=("Arial", 11, "bold"), command=converteste_fisier).pack(pady=15)

root.mainloop()