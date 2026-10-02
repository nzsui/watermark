# Auto Watermark Bot

Bot sederhana untuk menempelkan logo watermark otomatis ke banyak foto sekaligus.

- Watermark di **bawah tengah** foto
- Ukuran logo menyesuaikan lebar foto (~22%)
- **Format file tetap sama** (HEIC tetap HEIC, JPG tetap JPG)
- Support: `.heic`, `.heif`, `.jpg`, `.jpeg`, `.png`, `.webp`, `.tif`, `.bmp`

---

## Struktur folder

```text
watermark/
├── watermark.png   # logo watermark kamu
├── foto/           # taruh foto yang mau di-watermark di sini
├── output/         # hasil otomatis muncul di sini
├── watermark_bot.py
├── run.sh
└── requirements.txt
```

---

## Instalasi (macOS / Linux)

### 1. Persyaratan

- Python 3.10 atau lebih baru
- Git

Cek Python:

```bash
python3 --version
```

### 2. Clone repository

```bash
git clone https://github.com/nzsui/watermark.git
cd watermark
```

> Ganti `USERNAME` dengan username GitHub pemilik repo.

### 3. Buat virtual environment & install dependency

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 4. Siapkan file

1. Ganti `watermark.png` dengan logo kamu (PNG transparan lebih bagus)
2. Masukkan foto ke folder `foto/`

### 5. Jalankan

Cara cepat:

```bash
chmod +x run.sh
./run.sh
```

Atau manual:

```bash
source .venv/bin/activate
python watermark_bot.py
```

Hasil ada di folder `output/`.

---

## Instalasi (Windows)

### 1. Install Python

Download dari [python.org](https://www.python.org/downloads/)  
Centang **"Add Python to PATH"** saat install.

### 2. Clone & setup

Di PowerShell / CMD:

```bat
git clone https://github.com/nzsui/watermark.git
cd watermark
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Jalankan

1. Taruh logo sebagai `watermark.png`
2. Taruh foto di folder `foto`
3. Jalankan:

```bat
python watermark_bot.py
```

---

## Opsi tambahan

```bash
# watermark lebih kecil / lebih besar
./run.sh --scale 0.15
./run.sh --scale 0.30

# posisi
./run.sh --position bottom-left
./run.sh --position bottom-right
./run.sh --position bottom-center

# transparansi (0.0 - 1.0)
./run.sh --opacity 0.8

# folder custom
./run.sh --input ./foto --output ./output --watermark ./watermark.png
```

---

## Troubleshooting

**`Tidak ada foto di ...`**  
Pastikan file ada di folder `foto/` dan ekstensinya didukung.

**Error saat buka HEIC**  
Pastikan `pillow-heif` terinstall:

```bash
pip install pillow-heif
```

**Watermark terlalu kecil / besar**  
Atur dengan `--scale`, contoh:

```bash
./run.sh --scale 0.25
```

**Permission denied di `./run.sh`**

```bash
chmod +x run.sh
```

---

## Lisensi

Bebas dipakai untuk keperluan pribadi maupun bisnis.
