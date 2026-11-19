# Convertor și Player Audio Digital — Proiect de Prelucrarea Semnalelor Audio (PSA)

Acest proiect a fost dezvoltat în cadrul disciplinei **Prelucrarea Semnalelor Audio (PSA)** și reprezintă o aplicație desktop în **Python** pentru încărcarea, redarea, conversia, prelucrarea și verificarea proprietăților semnalelor audio. Scopul aplicației nu este doar schimbarea extensiei unui fișier, ci analiza practică a modului în care parametrii de semnal și compresie influențează calitatea audio percepută, structura semnalului și dimensiunea fișierului rezultat.

---

## 🚀 Funcționalități principale

1. **Interfață Grafică Dedicată (GUI):**
   * Construită cu `tkinter` și `ttk`, cu selecție rapidă a fișierului audio sursă prin dialogul nativ al sistemului (`filedialog`).
   * Procesarea și verificarea rulează pe un fir de execuție separat (`threading`), însoțită de o bară de progres (`Progressbar`) și mesaje de stare, astfel încât interfața să rămână receptivă.

2. **Player Audio Integrat (`▶ Play` / `⏹ Stop`):**
   * Permite ascultarea fișierului selectat direct din aplicație — atât a fișierului original, cât și a fișierului convertit/procesat — pentru comparație auditivă „înainte și după”.
   * Decodarea se realizează prin FFmpeg (furnizat de `imageio-ffmpeg`) într-un fișier WAV temporar, iar redarea asincronă și oprirea se fac prin `winsound` (pe Windows), cu curățarea fișierului temporar la oprire sau la închiderea ferestrei.

3. **Conversie și Prelucrare a Semnalului Audio:**
   * **Formate de ieșire suportate:** `MP3` (`libmp3lame`), `WAV` (PCM), `FLAC` și `OGG` (`libvorbis`).
   * **Modificarea ratei de eșantionare (*Sample Rate*):** resamplare la valori configurabile (`8000 Hz`, `16000 Hz`, `22050 Hz`, `32000 Hz`, `44100 Hz`, `48000 Hz`, `96000 Hz`).
   * **Controlul calității (*Bitrate*):** setare de la `64k` până la `320k` pentru formatele cu compresie cu pierderi (`MP3`, `OGG`), opțiune dezactivată automat pentru formatele fără pierderi (`WAV`, `FLAC`).
   * **Configurare canale audio:** păstrarea structurii inițiale (`Original`) sau conversia la `Mono` (1 canal) ori `Stereo` (2 canale).
   * **Normalizarea volumului:** ajustarea nivelului semnalului prin `pydub.effects.normalize`.

4. **Verificare Automată și Test Sintetic (`Test automat`):**
   * Inspectează proprietățile reale ale fișierului sursă și ale fișierului exportat folosind `ffmpeg -i` și afișează un tabel comparativ (`Așteptat` vs. `Obținut`) pentru: existența fișierului, format/codec, rată de eșantionare, număr de canale, durată și bitrate, alături de comparația dimensiunii în MB (`Original` vs. `Rezultat` și procentul din dimensiunea inițială).
   * Butonul **Test automat** generează un semnal sinusoidal pur de `440 Hz` (durată `3 s`, `44100 Hz`, stereo) și verifică întregul flux de conversie și validare fără a necesita un fișier extern.

---

## 🛠️ Tehnologii și Biblioteci Utilizate

* **Python 3.x** – Limbajul de programare principal.
* **Tkinter / ttk** – Realizarea interfeței grafice desktop și a tabelului de verificare (`Treeview`).
* **Pydub** – Manipularea obiectelor audio (`AudioSegment`), modificarea ratei de eșantionare și a canalelor, normalizarea semnalului (`normalize`) și generarea undei sinusoidale de test (`Sine`).
* **Imageio-ffmpeg** – Furnizează executabilul `ffmpeg` fără configurare manuală în sistem, utilizat pentru decodarea fișierelor audio (evitând dependența de `ffprobe`), export și citirea proprietăților reale ale fișierelor.
* **Winsound** (modul standard Python pe Windows) – Redarea asincronă și oprirea sunetului din interfață.



## 📂 Structura Proiectului

* **`main.py`** — Interfața grafică, logica de decodare/procesare, player-ul audio și verificarea.
* **`README.md`** — Documentația detaliată a proiectului.
* **`requirements.txt`** — Lista dependențelor Python externe.
* **`melodie.wav`** — Fișier audio de test / sursă (opțional, pot fi folosite și alte fișiere audio).