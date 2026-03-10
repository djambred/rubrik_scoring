# KUESIONER PEMETAAN PROFESI LULUSAN (PL) SI

## Tujuan
Kuesioner ini membantu memetakan kecenderungan profesi lulusan Program Studi Sistem Informasi (SI) berdasarkan jawaban **Ya/Tidak**.

Pertanyaan telah diselaraskan dengan kompetensi inti SKKNI level 6 untuk 5 Profil Lulusan (PL):
- PL01: Information System Developer
- PL02: IT Consultan
- PL03: Data Spesialist
- PL04: Business & System Analyst
- PL05: Entrepreneurship Resource Planning Architect

## Metode Pemetaan
Tersedia 2 mode pemetaan di aplikasi:
- Rule-Based Matrix: skoring PL utama +2 dan PL pendukung +1.
- KNN (berbasis data historis): klasifikasi menggunakan data jawaban terdahulu yang memiliki label `top1_pl` valid.

Catatan KNN:
- Membutuhkan data training historis yang cukup dan konsisten (kolom `q1..q15` dan `top1_pl`).
- Jika data belum cukup, aplikasi otomatis fallback ke Rule-Based Matrix.

## Instruksi
- Jawab setiap pertanyaan dengan **Ya** atau **Tidak** sesuai kondisi diri saat ini.
- Tidak ada jawaban benar/salah.
- Hasil menunjukkan **kecenderungan** profesi, bukan keputusan final.

## Daftar Pertanyaan
1. Apakah Anda suka menulis kode program (coding) untuk membuat aplikasi?
2. Apakah Anda lebih suka mencari kesalahan dalam sistem orang lain daripada membangun dari nol?
3. Apakah Anda merasa antusias saat bekerja dengan angka, data, dan statistik?
4. Apakah Anda senang menjadi penengah atau komunikator antara tim teknis dan pengguna?
5. Apakah Anda tertarik pada proses bisnis perusahaan seperti keuangan, stok barang, dan akuntansi?
6. Apakah Anda sering memperhatikan detail kecil yang orang lain lewatkan?
7. Apakah Anda suka memvisualisasikan data dalam bentuk grafik atau dashboard?
8. Apakah Anda merasa mudah menjelaskan hal rumit dengan bahasa sederhana?
9. Apakah Anda suka membayangkan gambaran besar (big picture) bagaimana semua sistem terhubung?
10. Apakah Anda tertarik mengikuti perkembangan teknologi terbaru?
11. Apakah Anda lebih suka bekerja mandiri daripada berkelompok?
12. Apakah Anda sering diminta teman untuk membantu masalah teknis komputer/laptop?
13. Apakah Anda suka membaca laporan keuangan atau memahami laporan laba-rugi?
14. Apakah Anda suka membuat alur proses (flowchart) atau diagram untuk memecahkan masalah?
15. Apakah Anda merasa puas ketika menemukan pola atau insight dari data mentah?

---

## Pemetaan Pertanyaan ke Profil Lulusan (PL)
Pemetaan ini diselaraskan dengan profil pada dataset PL:
- **PL01**: Information System Developer
- **PL02**: IT Consultan
- **PL03**: Data Spesialist
- **PL04**: Business & System Analyst
- **PL05**: Entrepreneurship Resource Planning Architect

### Tabel Pemetaan
| No | Fokus Kompetensi | PL Utama | PL Pendukung |
|---|---|---|---|
| 1 | Coding dan membangun aplikasi | PL01 | PL04 |
| 2 | Audit, quality check, evaluasi sistem | PL02 | PL04 |
| 3 | Angka, data, statistik | PL03 | PL02 |
| 4 | Komunikasi bisnis-teknis | PL04 | PL02 |
| 5 | Proses bisnis organisasi | PL05 | PL04 |
| 6 | Ketelitian dan detail | PL02 | PL03 |
| 7 | Visualisasi data/dashboard | PL03 | PL04 |
| 8 | Menjelaskan hal teknis secara sederhana | PL04 | PL02 |
| 9 | Big picture sistem terintegrasi | PL05 | PL04 |
| 10 | Adaptif terhadap tren teknologi | PL01 | PL05 |
| 11 | Preferensi kerja mandiri | PL03 | PL01 |
| 12 | Troubleshooting teknis | PL01 | PL02 |
| 13 | Laporan keuangan/bisnis | PL05 | PL03 |
| 14 | Flowchart/diagram/proses | PL04 | PL05 |
| 15 | Mencari pola dan insight data | PL03 | PL02 |

---

## Metode Skoring (Sederhana dan Praktis)
Gunakan bobot berikut untuk setiap jawaban:
- **Ya** pada PL Utama: +2 poin
- **Ya** pada PL Pendukung: +1 poin
- **Tidak**: +0 poin

Contoh: Pertanyaan nomor 1 dijawab Ya, maka:
- PL01 +2
- PL04 +1

### Langkah Hitung
1. Siapkan skor awal semua PL = 0.
2. Untuk setiap jawaban Ya, tambahkan poin sesuai tabel.
3. Jumlahkan seluruh skor per PL.
4. Urutkan dari skor tertinggi ke terendah.

---

## Interpretasi Hasil
- **Skor tertinggi**: profesi yang paling sesuai saat ini.
- **Skor kedua**: profesi alternatif/pendukung.
- Jika selisih skor 0–2 poin, berarti minat masih beririsan dan perlu validasi tambahan (portofolio, proyek, magang).

### Rekomendasi Penggunaan
- Gunakan hasil ini untuk rekomendasi topik proyek, peminatan, dan arah magang.
- Lakukan validasi dengan data tambahan:
  - nilai mata kuliah terkait,
  - pengalaman organisasi/proyek,
  - preferensi lingkungan kerja.

---

## Format Rekap (Siap Pakai)
| PL | Nama Profesi | Skor |
|---|---|---:|
| PL01 | Information System Developer |  |
| PL02 | IT Consultan |  |
| PL03 | Data Spesialist |  |
| PL04 | Business & System Analyst |  |
| PL05 | Entrepreneurship Resource Planning Architect |  |

### Kesimpulan Akhir
- Profesi utama: __________
- Profesi alternatif: __________
- Catatan pengembangan: __________


