<div align="center">

  <img src="" alt="Voralet - Personal Finance Vault Banner" width="100%" />

  <br/><br/>

  <h1>Voralet</h1>
  <p>
    <strong>Aplikasi Pencatat Keuangan Pribadi, Buku Kas, Manajemen Dompet, Pemindai Struk Offline &amp; Ekspor Excel (<code>.xlsx</code>)</strong>
  </p>
  <p>
    <em>100% Pure Offline • Zero Tracking Permissions • ChaCha20 Asset Vault • On Device ML Kit OCR</em>
  </p>

  <p>
    <a href="https://github.com/Bagas240/Voralet-pencatat-keuangan-pribadi-/releases">
      <img src="https://img.shields.io/badge/Version-v3.4.0-0EA5E9?style=for-the-badge&logo=android&logoColor=white" alt="Version v3.4.0"/>
    </a>
    <a href="LICENSE">
      <img src="https://img.shields.io/badge/License-Apache_2.0-2563EB?style=for-the-badge&logo=apache&logoColor=white" alt="License Apache 2.0"/>
    </a>
    <img src="https://img.shields.io/badge/Offline-100%25%20Local-10B981?style=for-the-badge&logo=shield&logoColor=white" alt="100% Offline"/>
    <img src="https://img.shields.io/badge/Kotlin-Android%20%2B%20React%2018-7F52FF?style=for-the-badge&logo=kotlin&logoColor=white" alt="Kotlin & React 18"/>
    <img src="https://img.shields.io/badge/Android-7.0%2B%20(API%2024--36)-3DDC84?style=for-the-badge&logo=android&logoColor=white" alt="Android 7.0+"/>
  </p>

  <p>
    <a href="#ringkasan">Ringkasan</a> •
    <a href="#fitur-utama">Fitur Utama</a> •
    <a href="#arsitektur-keamanan">Keamanan</a> •
    <a href="#instalasi-apk">Instalasi</a> •
    <a href="#membangun-dari-kode-sumber">Build dari Sumber</a> •
    <a href="#lisensi">Lisensi</a>
  </p>

</div>

---

## Ringkasan

**Voralet** adalah aplikasi pencatat keuangan pribadi untuk Android yang dirancang dengan prinsip **Privacy-First** dan **Zero Network Dependency**. Seluruh data transaksi, saldo dompet, catatan hutang-piutang, target tabungan, hingga pemindaian struk belanja diproses sepenuhnya di dalam perangkat tanpa server pihak ketiga, tanpa API key eksternal, dan tanpa koneksi internet.

Dibangun untuk tetap ringan, mulus di layar 60/90/120Hz, dan hemat baterai, Voralet v3.4.0 menggabungkan antarmuka modern dengan perlindungan keamanan berlapis (*ChaCha20-encrypted asset vault*, *R8 Full Mode*, dan *RASP*), serta dilengkapi generator **Workbook Excel (`.xlsx`) 5 Sheet** dan **Pemindai Struk Offline berbasis Google ML Kit**.

---

## Pratinjau Arsitektur & Fitur

<p align="center">
  <img src="docs/images/voralet-feature-showcase.svg" alt="Voralet Feature and Security Architecture" width="100%" />
</p>

---

## Fitur Utama

| Kategori | Kemampuan Utama |
| :--- | :--- |
| **Brankas PIN & Privasi** | Kunci aplikasi dengan **6-digit PIN lokal**, *Privacy Mode* untuk menyamarkan saldo dalam satu ketukan, serta perlindungan `FLAG_SECURE` pada build rilis untuk mencegah tangkapan dan perekaman layar dari aplikasi lain. |
| **Multi Dompet & Akun** | Kelola rekening Bank, E-Wallet, dan Tunai secara terpisah dengan perhitungan saldo real-time untuk Pemasukan, Pengeluaran, dan Transfer antar dompet. |
| **Scan Struk Offline (Auto-Catat)** | Pindai struk belanja melalui kamera atau galeri menggunakan **Google ML Kit Text Recognition** yang tertanam penuh di perangkat—tanpa memerlukan izin `CAMERA` ataupun akses internet. Mode **Auto-Catat** mengekstrak total harga, merchant, item belanja, dan kategori menjadi transaksi secara otomatis. |
| **Ekspor Excel (`.xlsx`) 5 Sheet** | Generator OOXML `.xlsx` murni Kotlin tanpa dependensi eksternal berat. Menghasilkan 5 sheet terformat rapi (**Ringkasan Keuangan**, **Mutasi Transaksi**, **Hutang & Piutang**, **Tabungan Impian**, **Daftar Dompet**) lengkap dengan format mata uang Rupiah, *freeze header*, serta penyimpanan langsung melalui Android Storage Access Framework (SAF). |
| **Laporan PDF & Backup Terverifikasi** | Ekspor ringkasan kas ke dokumen PDF secara offline dan cadangkan/pulihkan data lokal dengan verifikasi integritas HMAC-SHA256. |
| **Tabungan Impian, Hutang & Widget** | Pantau progres target tabungan, kelola catatan hutang/piutang beserta cicilan, jaga streak pencatatan harian, dan akses ringkasan langsung melalui Widget Home Screen Android (*Streak* & *Pet Companion*). |

---

## Arsitektur Keamanan

Voralet menerapkan pendekatan **Defense in Depth** untuk melindungi kode aplikasi dan data finansial pengguna:

1. **Encrypted Offline Asset Vault (`voralet_core.bin`)**
   - Bundel antarmuka dikompresi (`zlib`) dan dienkripsi saat *build time* menggunakan **ChaCha20** dengan skema **Encrypt-then-MAC (`HMAC-SHA256`)** ke dalam berkas biner `voralet_core.bin`.
   - Dekripsi dan verifikasi integritas dilakukan langsung di memori (RAM) saat runtime melalui `AssetVaultDecryptor`, tanpa mengekstrak berkas HTML/JS mentah ke penyimpanan.
2. **R8 Full Mode & Obfuskasi (`proguard-rules.pro`)**
   - Menggunakan `android.enableR8.fullMode=true`, `isMinifyEnabled = true`, dan `isShrinkResources = true` pada build rilis.
   - Menghapus informasi `SourceFile`, `LineNumberTable`, log debug (`android.util.Log`), serta membatasi aturan *keep* secara ketat pada antarmuka native bridge.
3. **Runtime Application Self-Protection (`AppSecurityGuard`)**
   - Mendeteksi keterikatan *debugger* (`Debug.isDebuggerConnected`, `TracerPid`), kerangka injeksi (*Frida*, *Xposed*, *LSPosed*, *Zygisk*), status *root*, serta memvalidasi tanda tangan sertifikat APK.
4. **Hardened Offline WebView & Zero-Permission Manifest**
   - `AndroidManifest.xml` tidak mendeklarasikan izin jaringan atau perangkat keras sensitif (`INTERNET`, `CAMERA`, `READ_EXTERNAL_STORAGE`, `WRITE_EXTERNAL_STORAGE`, `LOCATION`, `RECORD_AUDIO`).
   - WebView beroperasi melalui origin virtual `https://appassets.androidplatform.net/` dengan `allowFileAccess = false`, `allowContentAccess = false`, pemblokiran seluruh navigasi/permintaan eksternal di `VoraletWebViewClient`, serta `android:allowBackup="false"` dan `android:usesCleartextTraffic="false"`.

---

## Optimasi Performa & Baterai

- **Pre-Compiled ECMAScript**: Seluruh JSX ditranspilasi menjadi JavaScript native saat *build time* (`build_index.py`), sehingga startup berjalan instan tanpa overhead transpilasi runtime.
- **Background Animation Freezing**: Saat aplikasi masuk ke latar belakang (`onPause` / `document.hidden`), seluruh animasi CSS (`voralet-paused`) dan loop `requestAnimationFrame` dihentikan seketika untuk meminimalkan beban CPU/GPU.
- **GPU-Composited Animations**: Efek visual memanfaatkan properti *composited* (`transform` dan `opacity`) serta menghormati preferensi *Reduced Motion*.
- **Zero Background Services**: Tidak menggunakan *wakelock*, layanan latar belakang persisten, atau *polling* jaringan.

---

## Teknologi yang Digunakan

| Lapisan | Teknologi |
| :--- | :--- |
| **Android Native** | Kotlin, Android SDK 36, Jetpack Compose / Material 3, AppWidget, FileProvider & SAF |
| **Keamanan & Enkripsi** | ChaCha20 + HMAC-SHA256 Asset Vault, R8 Full Mode, `AppSecurityGuard` (RASP), `FLAG_SECURE` |
| **Offline OCR** | Google ML Kit Text Recognition (`com.google.mlkit:text-recognition:16.0.1` — *on-device model*) |
| **Ekspor Dokumen** | Pure-Kotlin OOXML `.xlsx` Exporter (`ZipOutputStream`) & `html2pdf.js` offline |
| **Antarmuka Web Engine** | Pre-compiled React 18, Bundled Tailwind CSS, Sandboxed Local Storage |
| **Pengujian & Audit** | JUnit 4, Robolectric, Roborazzi, dan `verify_master_security.py` |

---

## Struktur Proyek

```text
.
├── .github/workflows/          # Alur CI/CD build, audit keamanan, dan rilis APK
├── app/
│   ├── src/main/
│   │   ├── assets/             # Vault biner terenkripsi (voralet_core.bin) & aset vendor offline
│   │   ├── java/com/example/
│   │   │   ├── bridge/         # Native JS-Android bridge (AndroidNativeBridge)
│   │   │   ├── export/         # Generator workbook Excel OOXML multi-sheet (ExcelXlsxExporter)
│   │   │   ├── ocr/            # Mesin OCR struk offline (OfflineReceiptOcrEngine)
│   │   │   ├── security/       # RASP & dekriptor vault (AppSecurityGuard, AssetVaultDecryptor)
│   │   │   ├── webview/        # Konfigurasi & klien WebView terisolasi
│   │   │   ├── widget/         # Provider Widget Streak & Pet Companion
│   │   │   └── MainActivity.kt
│   │   └── res/                # Resource Android, layout widget, dan adaptive launcher icon
│   └── src/test/               # Unit test & Robolectric test (Vault, WebView, Excel, Security)
├── parts/                      # Modul sumber frontend sebelum kompilasi & enkripsi vault
├── build_index.py              # Script pre-kompilasi JSX & pembungkus vault ChaCha20
├── verify_master_security.py   # Audit keamanan & kepatuhan zero-network/zero-permission
├── LICENSE                     # Teks penuh Apache License 2.0
└── README.md
```

---

## Spesifikasi Perangkat

<details>
<summary><strong>Lihat Spesifikasi Minimum &amp; Rekomendasi</strong></summary>

### Spesifikasi Minimum
- **OS**: Android 7.0 (Nougat / API 24) atau lebih baru
- **WebView**: Android System WebView v80+
- **RAM**: 2 GB
- **Penyimpanan Kosong**: ± 35 MB
- **Layar**: HD (720 × 1280 px)

### Spesifikasi Rekomendasi
- **OS**: Android 11 – 16 (API 30 – 36)
- **RAM**: 3 GB atau lebih
- **Penyimpanan Kosong**: 100 MB
- **Layar**: FHD+ (1080 × 2400 px) @ 60Hz / 90Hz / 120Hz

</details>

---

## Instalasi APK

### Unduh Rilis Resmi
1. Buka halaman **[GitHub Releases](https://github.com/Bagas240/Voralet-pencatat-keuangan-pribadi-/releases)**.
2. Pilih versi rilis terbaru (misalnya **`v3.4.0`**) dan unduh berkas APK pada bagian **Assets**.
3. Jika menginstal di luar Google Play, aktifkan opsi *"Instal aplikasi tidak dikenal"* untuk browser atau file manager Anda pada Pengaturan Android.
4. Buka aplikasi Voralet, atur **6-digit PIN lokal**, dan aplikasi siap digunakan secara offline.

### Verifikasi Checksum (SHA-256)
Cocokkan nilai hash SHA-256 berkas APK yang diunduh dengan nilai pada catatan rilis untuk memastikan keutuhan berkas:

```bash
# Linux / macOS / Termux
sha256sum app-debug.apk

# Windows (PowerShell)
Get-FileHash .\app-debug.apk -Algorithm SHA256
```

---

## Membangun dari Kode Sumber

### Prasyarat
- **JDK 17+**
- **Android SDK** (`compileSdk = 36`, `minSdk = 24`)
- **Python 3.10+** & **Node.js 18+** (digunakan oleh `build_index.py` saat kompilasi aset)

### Langkah Build & Pengujian Lokal

```bash
# 1. Jalankan audit integritas keamanan & kebijakan offline
python3 verify_master_security.py

# 2. Pre-compile JSX & enkripsi aset ke app/src/main/assets/voralet_core.bin
python3 build_index.py

# 3. Jalankan unit test & Robolectric test
gradle :app:testDebugUnitTest

# 4. Bangun Debug APK
gradle assembleDebug
```

> **Catatan CI/CD**: Alur GitHub Actions pada `.github/workflows/build-apk.yml` menjalankan audit `verify_master_security.py`, kompilasi vault `build_index.py`, pengujian `:app:testDebugUnitTest`, hingga pembuatan artefak APK rilis secara otomatis pada setiap push atau tag `v*`.

---

## Kontribusi & Pelaporan Masalah

Kontribusi sangat terbuka untuk peningkatan kualitas, perbaikan bug, maupun penguatan keamanan:

1. *Fork* repositori ini dan buat *branch* fitur atau perbaikan baru (`git checkout -b fitur/nama-fitur`).
2. Pastikan seluruh pemeriksaan keamanan (`python3 verify_master_security.py`) dan pengujian (`gradle :app:testDebugUnitTest`) lolos tanpa error.
3. Ajukan *Pull Request* dengan deskripsi perubahan yang jelas.

Untuk melaporkan bug atau mengusulkan fitur baru, silakan buka tiket di halaman **[Issues](https://github.com/Bagas240/Voralet-pencatat-keuangan-pribadi-/issues)**.

> Dengan mengirimkan kontribusi ke repositori ini, Anda menyetujui bahwa kontribusi tersebut dilisensikan di bawah **Apache License 2.0**.

---

## Lisensi

Proyek ini dilisensikan di bawah **[Apache License, Version 2.0](LICENSE)**.

```text
Copyright 2026 Bagas240

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```
