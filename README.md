# Convertor și Player Audio Digital — Proiect de Prelucrarea Semnelor Audio (PSA)

Acest proiect a fost dezvoltat în cadrul disciplinei **Prelucrarea Semnelor Audio (PSA)** și reprezintă o aplicație desktop completă în **Python** pentru conversia, procesarea și redarea fișierelor audio, punând în practică concepte fundamentale de inginerie a sunetului și eșantionare a semnalelor.



## 🚀 Funcționalități principale

1. **Interfață Grafică Dedicată (GUI):**
   * Construită nativ în Python folosind biblioteca `tkinter`, oferind o experiență de utilizator intuitivă și accesibilă.
   * Permite selectarea rapidă a fișierelor de intrare prin intermediul unui dialog nativ de sistem (`filedialog`).

2. **Player Multimedia Integrat:**
   * Butoane dedicate de **Play** și **Stop** bazate pe bibliotecile `simpleaudio` și `pydub`, oferind posibilitatea de a asculta semnalul audio direct din aplicație înainte sau după procesare.

3. **Conversie și Procesare a Semnalului:**
   * **Schimbarea ratei de eșantionare (*Sample Rate*):** Permite resamplarea semnalului audio (valori configurabile precum 8000 Hz, 16000 Hz, 22050 Hz, 44100 Hz, 48000 Hz). Această operațiune reflectă direct conceptele teoretice de lățime de bandă și eșantionare.
   * **Controlul calității (*Bitrate*):** Setarea ratei de biți pentru compresie (de la 64 kbps până la 320 kbps).
   * **Suport pentru multiple formate:** Conversie flexibilă între formate necomprimate (`.wav`) și comprimate cu pierderi (`.mp3`).

---

## 🛠️ Tehnologii și Biblioteci Utilizate

* **Python 3.x** – Limbajul de programare principal.
* **Tkinter** – Pentru crearea interfeței grafice de tip desktop.
* **Pydub** – Pentru decodarea, manipularea obiectelor audio (`AudioSegment`) și exportul în diferite formate.
* **Imageio-ffmpeg** – Asigură motorul executabil FFmpeg nativ, necesar pentru decodarea și codarea fluxurilor comprimate (cum ar fi MP3), eliminând necesitatea configurării manuale a variabilelor de mediu în sistem.
* **Simpleaudio** – Pentru redarea în timp real a segmentelor audio din interfață.



## Structura Proiectului

```text
Proiect-Audio-Converter/
│
├── main.py             # Codul sursă principal (Interfața grafică și logica de procesare)
├── README.md           # Documentația detaliată a proiectului
└── melodie.wav         # Fișier audio de test / sursă