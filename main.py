import os
import re
import subprocess
import tempfile
import threading
import warnings
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# Evită avertismentele pydub la import înainte de setarea executabilului FFmpeg
warnings.filterwarnings("ignore", category=RuntimeWarning)

import imageio_ffmpeg
from pydub import AudioSegment
from pydub.effects import normalize
from pydub.generators import Sine

# Configurare FFmpeg prin imageio-ffmpeg (nu trebuie instalat separat în sistem)
FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()
AudioSegment.converter = FFMPEG_EXE
AudioSegment.ffmpeg = FFMPEG_EXE

if os.name == "nt":
    import winsound

# extensie -> (format_ffmpeg, codec, are_bitrate, prefix_codec_verificare)
FORMATE = {
    "mp3": ("mp3", "libmp3lame", True, "mp3"),
    "wav": ("wav", None, False, "pcm_"),
    "flac": ("flac", None, False, "flac"),
    "ogg": ("ogg", "libvorbis", True, "vorbis"),
}

fisier_temp_redare = None


# ---------------------------------------------------------------- LOGICA AUDIO
def optiuni_subprocess():
    """Ascunde fereastra de consolă a FFmpeg pe Windows."""
    return {"creationflags": subprocess.CREATE_NO_WINDOW} if os.name == "nt" else {}


def incarca_audio(cale_fisier):
    """Încarcă orice format audio fără să aibă nevoie de ffprobe.

    imageio-ffmpeg conține doar FFmpeg, nu și ffprobe, iar pydub folosește ffprobe
    când citește fișiere non-WAV. De aceea decodăm întâi cu FFmpeg într-un WAV
    temporar, pe care pydub îl poate citi direct.
    """
    if cale_fisier.lower().endswith(".wav"):
        try:
            return AudioSegment.from_wav(cale_fisier)
        except Exception:
            pass  # WAV neobișnuit (ex. float) -> îl decodăm cu FFmpeg

    folder_tmp = tempfile.mkdtemp()
    wav_tmp = os.path.join(folder_tmp, "decodat.wav")
    rezultat = subprocess.run(
        [FFMPEG_EXE, "-y", "-i", cale_fisier, "-vn", "-acodec", "pcm_s16le", wav_tmp],
        capture_output=True,
        **optiuni_subprocess(),
    )
    if rezultat.returncode != 0 or not os.path.exists(wav_tmp):
        raise RuntimeError("FFmpeg nu a putut decoda fișierul. Este un fișier audio valid?")
    try:
        return AudioSegment.from_wav(wav_tmp)
    finally:
        try:
            os.remove(wav_tmp)
            os.rmdir(folder_tmp)
        except Exception:
            pass


def citeste_info_audio(cale_fisier):
    """Citește proprietățile reale ale unui fișier audio folosind FFmpeg."""
    iesire = subprocess.run(
        [FFMPEG_EXE, "-i", cale_fisier],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        **optiuni_subprocess(),
    ).stderr

    info = {"codec": None, "sr": None, "canale": None, "durata": None, "bitrate": None}

    durata_match = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", iesire)
    if durata_match:
        info["durata"] = (
            int(durata_match.group(1)) * 3600
            + int(durata_match.group(2)) * 60
            + float(durata_match.group(3))
        )

    bitrate_match = re.search(r"bitrate:\s*(\d+)\s*kb/s", iesire)
    if bitrate_match:
        info["bitrate"] = int(bitrate_match.group(1))

    format_match = re.search(r"Audio:\s*(\w+)[^\n]*?(\d+)\s*Hz,\s*([^,\n]+)", iesire)
    if format_match:
        info["codec"] = format_match.group(1).lower()
        info["sr"] = int(format_match.group(2))
        canale_text = format_match.group(3).strip().lower()
        info["canale"] = 1 if canale_text == "mono" else 2 if canale_text == "stereo" else 2

    return info


def converteste_si_proceseaza(setari):
    """Încarcă, prelucrează și exportă fișierul audio. Returnează calea fișierului rezultat."""
    sursa_curata = os.path.abspath(setari["input"].strip().strip('"'))
    if not os.path.isfile(sursa_curata):
        raise FileNotFoundError(f"Fișierul sursă nu există: {sursa_curata}")

    audio = incarca_audio(sursa_curata)

    # Prelucrarea semnalului audio
    audio = audio.set_frame_rate(int(setari["sr"]))
    if setari["canale"] == "Mono":
        audio = audio.set_channels(1)
    elif setari["canale"] == "Stereo":
        audio = audio.set_channels(2)
    if setari["normalizare"]:
        audio = normalize(audio)

    format_ffmpeg, codec, are_bitrate, _ = FORMATE[setari["format"]]
    cale_iesire = setari.get("output") or (
        f"{os.path.splitext(sursa_curata)[0]}_procesat.{setari['format']}"
    )
    cale_iesire = os.path.abspath(cale_iesire)

    parametri = {"format": format_ffmpeg}
    if codec:
        parametri["codec"] = codec
    if are_bitrate:
        parametri["bitrate"] = setari["bitrate"]

    audio.export(cale_iesire, **parametri)
    return cale_iesire


def verifica_rezultat(setari, cale_iesire):
    """Compară parametrii aleși cu proprietățile reale ale fișierului exportat."""
    sursa_curata = os.path.abspath(setari["input"].strip().strip('"'))
    sursa = citeste_info_audio(sursa_curata)
    rezultat = citeste_info_audio(cale_iesire)
    randuri = []

    exista = os.path.exists(cale_iesire) and os.path.getsize(cale_iesire) > 0
    randuri.append(("Fișier creat", "da", "da" if exista else "nu", "ok" if exista else "fail"))

    prefix_codec = FORMATE[setari["format"]][3]
    codec_real = rezultat["codec"] or "?"
    randuri.append((
        "Format / codec",
        setari["format"].upper(),
        codec_real,
        "ok" if codec_real.startswith(prefix_codec) else "fail",
    ))

    randuri.append((
        "Rată de eșantionare",
        f"{setari['sr']} Hz",
        f"{rezultat['sr']} Hz" if rezultat["sr"] else "?",
        "ok" if rezultat["sr"] == int(setari["sr"]) else "fail",
    ))

    canale_asteptate = {"Mono": 1, "Stereo": 2}.get(setari["canale"], sursa["canale"])
    randuri.append((
        "Canale",
        str(canale_asteptate) if canale_asteptate else "?",
        str(rezultat["canale"]) if rezultat["canale"] else "?",
        "ok" if rezultat["canale"] == canale_asteptate else "fail",
    ))

    if sursa["durata"] and rezultat["durata"]:
        durata_ok = abs(sursa["durata"] - rezultat["durata"]) <= 0.15
        randuri.append((
            "Durată",
            f"{sursa['durata']:.2f} s",
            f"{rezultat['durata']:.2f} s",
            "ok" if durata_ok else "fail",
        ))

    if FORMATE[setari["format"]][2] and rezultat["bitrate"]:
        bitrate_cerut = int(setari["bitrate"].replace("k", ""))
        bitrate_ok = abs(rezultat["bitrate"] - bitrate_cerut) <= bitrate_cerut * 0.25
        randuri.append((
            "Calitate (bitrate)",
            f"{bitrate_cerut} kb/s",
            f"{rezultat['bitrate']} kb/s",
            "ok" if bitrate_ok else "warn",
        ))

    return randuri


# ---------------------------------------------------------------- PLAYER AUDIO
def citeste_cale():
    """Returnează calea curată din câmpul de text, sau '' dacă e gol."""
    text = entry_file.get().strip().strip('"')
    return os.path.abspath(text) if text else ""


def reda_audio():
    """Redă fișierul audio selectat în interfață."""
    global fisier_temp_redare

    cale_fisier = citeste_cale()
    if not cale_fisier or not os.path.isfile(cale_fisier):
        messagebox.showerror("Eroare", "Te rog selectează un fișier audio valid!")
        return

    opreste_audio()

    try:
        audio = incarca_audio(cale_fisier)
        fisier_temp_redare = os.path.join(tempfile.gettempdir(), "convertor_psa_redare.wav")
        audio.set_channels(2).set_frame_rate(44100).export(fisier_temp_redare, format="wav")

        if os.name == "nt":
            winsound.PlaySound(fisier_temp_redare, winsound.SND_FILENAME | winsound.SND_ASYNC)
            status.set(f"Se redă: {os.path.basename(cale_fisier)}")
        else:
            messagebox.showwarning("Redare indisponibilă", "Redarea nativă este configurată pentru Windows.")
    except Exception as e:
        messagebox.showerror("Eroare la redare", f"Nu s-a putut reda fișierul:\n{e}")


def opreste_audio():
    """Oprește redarea audio activă și curăță fișierul temporar."""
    global fisier_temp_redare

    if os.name == "nt":
        try:
            winsound.PlaySound(None, winsound.SND_PURGE)
        except Exception:
            pass

    if fisier_temp_redare and os.path.exists(fisier_temp_redare):
        try:
            os.remove(fisier_temp_redare)
        except Exception:
            pass
        fisier_temp_redare = None

    status.set("Redare oprită.")


# ------------------------------------------------------------------- INTERFAȚĂ
def citeste_setari(mod_test=False):
    return {
        "input": entry_file.get().strip().strip('"'),
        "format": var_format.get(),
        "bitrate": var_bitrate.get(),
        "sr": int(var_sr.get()),
        "canale": var_canale.get(),
        "normalizare": var_normalizare.get(),
        "test": mod_test,
    }


def porneste_conversie():
    cale_fisier = citeste_cale()
    if not cale_fisier or not os.path.isfile(cale_fisier):
        messagebox.showerror("Eroare", "Te rog selectează un fișier audio valid!")
        return
    porneste_procesare(citeste_setari(mod_test=False))


def porneste_test_automat():
    """Generează un ton de test de 440 Hz și verifică procesarea/conversia."""
    porneste_procesare(citeste_setari(mod_test=True))


def porneste_procesare(setari):
    opreste_audio()
    buton_conv.config(state="disabled")
    buton_test.config(state="disabled")
    progres.start(10)
    status.set("Se procesează și se verifică semnalul audio...")
    threading.Thread(target=executa_in_fundal, args=(setari,), daemon=True).start()


def executa_in_fundal(setari):
    try:
        if setari["test"]:
            folder_tmp = tempfile.mkdtemp()
            sursa_tmp = os.path.join(folder_tmp, "sunet_test_440hz.wav")
            Sine(440).to_audio_segment(duration=3000).set_frame_rate(44100).set_channels(2).export(
                sursa_tmp, format="wav"
            )
            setari["input"] = sursa_tmp
            setari["output"] = os.path.join(folder_tmp, f"sunet_test_procesat.{setari['format']}")

        cale_iesire = converteste_si_proceseaza(setari)
        randuri = verifica_rezultat(setari, cale_iesire)
        root.after(0, finalizeaza_procesarea, True, setari, cale_iesire, randuri)
    except Exception as e:
        root.after(0, finalizeaza_procesarea, False, setari, None, str(e))


def finalizeaza_procesarea(succes, setari, cale_iesire, rezultat):
    progres.stop()
    buton_conv.config(state="normal")
    buton_test.config(state="normal")
    tabel.delete(*tabel.get_children())

    if not succes:
        status.set("A apărut o eroare la procesare.")
        marime.set("")
        messagebox.showerror("Eroare de procesare", rezultat)
        return

    simbol = {"ok": "✔ corect", "warn": "⚠ diferă", "fail": "✘ greșit"}
    for nume, asteptat, obtinut, stare in rezultat:
        tabel.insert("", tk.END, values=(nume, asteptat, obtinut, simbol[stare]), tags=(stare,))

    reusite = sum(1 for r in rezultat if r[3] == "ok")
    esecuri = sum(1 for r in rezultat if r[3] == "fail")
    mb_in = os.path.getsize(setari["input"]) / 1024 / 1024
    mb_out = os.path.getsize(cale_iesire) / 1024 / 1024
    procent = (mb_out / mb_in * 100) if mb_in > 0 else 0
    marime.set(f"Original: {mb_in:.2f} MB  →  Rezultat: {mb_out:.2f} MB ({procent:.0f}% din original)")

    if esecuri:
        status.set(f"Verificare: {reusite}/{len(rezultat)} corecte, {esecuri} greșite.")
    else:
        status.set(f"Verificare reușită: {reusite}/{len(rezultat)} corecte.")

    if not setari["test"]:
        messagebox.showinfo("Succes!", f"Fișierul a fost salvat ca:\n{cale_iesire}")


def selecteaza_fisier():
    cale_fisier = filedialog.askopenfilename(
        filetypes=[
            ("Fișiere audio", "*.wav *.mp3 *.flac *.ogg *.m4a *.aac"),
            ("Toate fișierele", "*.*"),
        ]
    )
    if cale_fisier:
        entry_file.delete(0, tk.END)
        entry_file.insert(0, os.path.normpath(cale_fisier))


def actualizeaza_bitrate(*_):
    """Bitrate-ul se activează doar pentru formatele cu compresie cu pierderi (MP3, OGG)."""
    bit_menu.config(state="normal" if FORMATE[var_format.get()][2] else "disabled")


def la_inchidere():
    opreste_audio()
    root.destroy()


root = tk.Tk()
root.title("Convertor & Player Audio - Prelucrarea Semnalelor Audio")
root.geometry("540x780")
root.resizable(False, False)
root.protocol("WM_DELETE_WINDOW", la_inchidere)

# 1. Selectare fișier audio
tk.Label(root, text="Fișier audio sursă:", font=("Arial", 10, "bold")).pack(pady=(10, 4))
frame_file = tk.Frame(root)
frame_file.pack(pady=2)
entry_file = tk.Entry(frame_file, width=42)
entry_file.pack(side=tk.LEFT, padx=5)
tk.Button(frame_file, text="Caută...", command=selecteaza_fisier).pack(side=tk.LEFT)

# 2. Butoane Play / Stop
frame_player = tk.Frame(root)
frame_player.pack(pady=8)
tk.Button(
    frame_player,
    text="▶ Play",
    bg="#1f5eff",
    fg="white",
    font=("Arial", 10, "bold"),
    width=11,
    command=reda_audio,
).pack(side=tk.LEFT, padx=10)
tk.Button(
    frame_player,
    text="⏹ Stop",
    bg="#d92b2b",
    fg="white",
    font=("Arial", 10, "bold"),
    width=11,
    command=opreste_audio,
).pack(side=tk.LEFT, padx=10)

# 3. Format de ieșire
tk.Label(root, text="Format de ieșire:", font=("Arial", 10, "bold")).pack(pady=4)
var_format = tk.StringVar(value="mp3")
frame_format = tk.Frame(root)
frame_format.pack()
for fmt in FORMATE:
    tk.Radiobutton(
        frame_format,
        text=fmt.upper(),
        variable=var_format,
        value=fmt,
        command=actualizeaza_bitrate,
    ).pack(side=tk.LEFT, padx=8)

# 4. Rată de eșantionare (Sample Rate)
tk.Label(root, text="Rată de eșantionare (Sample Rate):", font=("Arial", 10, "bold")).pack(pady=4)
var_sr = tk.StringVar(value="44100")
tk.OptionMenu(root, var_sr, "8000", "16000", "22050", "32000", "44100", "48000", "96000").pack()

# 5. Calitate / Bitrate
tk.Label(root, text="Calitate (Bitrate MP3/OGG):", font=("Arial", 10, "bold")).pack(pady=4)
var_bitrate = tk.StringVar(value="192k")
bit_menu = tk.OptionMenu(root, var_bitrate, "64k", "128k", "192k", "256k", "320k")
bit_menu.pack()

# 6. Canale și normalizare
tk.Label(root, text="Canale audio:", font=("Arial", 10, "bold")).pack(pady=4)
var_canale = tk.StringVar(value="Original")
tk.OptionMenu(root, var_canale, "Original", "Mono", "Stereo").pack()
var_normalizare = tk.BooleanVar(value=False)
tk.Checkbutton(root, text="Normalizează volumul", variable=var_normalizare).pack(pady=4)

# 7. Butoane acțiune și bară de progres
frame_butoane = tk.Frame(root)
frame_butoane.pack(pady=8)
buton_conv = tk.Button(
    frame_butoane,
    text="Convertește și Procesează",
    bg="green",
    fg="white",
    font=("Arial", 11, "bold"),
    command=porneste_conversie,
)
buton_conv.pack(side=tk.LEFT, padx=6)
buton_test = tk.Button(
    frame_butoane,
    text="Test automat",
    bg="#1565c0",
    fg="white",
    font=("Arial", 11, "bold"),
    command=porneste_test_automat,
)
buton_test.pack(side=tk.LEFT, padx=6)

progres = ttk.Progressbar(root, mode="indeterminate", length=320)
progres.pack(pady=4)

# 8. Tabel verificare
tk.Label(root, text="Rezultatul verificării:", font=("Arial", 10, "bold")).pack(pady=(8, 2))
tabel = ttk.Treeview(
    root,
    columns=("verificare", "asteptat", "obtinut", "stare"),
    show="headings",
    height=6,
)
for col, titlu, latime in (
    ("verificare", "Verificare", 145),
    ("asteptat", "Așteptat", 100),
    ("obtinut", "Obținut", 100),
    ("stare", "Rezultat", 95),
):
    tabel.heading(col, text=titlu)
    tabel.column(col, width=latime, anchor="center")

tabel.tag_configure("ok", foreground="#2e7d32")
tabel.tag_configure("warn", foreground="#ef6c00")
tabel.tag_configure("fail", foreground="#c62828")
tabel.pack(padx=10)

marime = tk.StringVar(value="")
tk.Label(root, textvariable=marime).pack(pady=4)
status = tk.StringVar(value="Gata de lucru.")
tk.Label(root, textvariable=status, fg="gray").pack()

actualizeaza_bitrate()
root.mainloop()