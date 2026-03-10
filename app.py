import csv
import os
from datetime import datetime

import streamlit as st

st.set_page_config(page_title="Kuesioner Pemetaan PL SI", page_icon="📊", layout="wide")

QUESTIONS = [
    "Apakah Anda suka menulis kode program (coding) untuk membuat aplikasi?",
    "Apakah Anda lebih suka mencari kesalahan dalam sistem orang lain daripada membangun dari nol?",
    "Apakah Anda merasa antusias saat bekerja dengan angka, data, dan statistik?",
    "Apakah Anda senang menjadi penengah atau komunikator antara tim teknis dan pengguna?",
    "Apakah Anda tertarik pada proses bisnis perusahaan seperti keuangan, stok barang, dan akuntansi?",
    "Apakah Anda sering memperhatikan detail kecil yang orang lain lewatkan?",
    "Apakah Anda suka memvisualisasikan data dalam bentuk grafik atau dashboard?",
    "Apakah Anda merasa mudah menjelaskan hal rumit dengan bahasa sederhana?",
    "Apakah Anda suka membayangkan gambaran besar (big picture) bagaimana semua sistem terhubung?",
    "Apakah Anda tertarik mengikuti perkembangan teknologi terbaru?",
    "Apakah Anda lebih suka bekerja mandiri daripada berkelompok?",
    "Apakah Anda sering diminta teman untuk membantu masalah teknis komputer/laptop?",
    "Apakah Anda suka membaca laporan keuangan atau memahami laporan laba-rugi?",
    "Apakah Anda suka membuat alur proses (flowchart) atau diagram untuk memecahkan masalah?",
    "Apakah Anda merasa puas ketika menemukan pola atau insight dari data mentah?",
]

PL_LABELS = {
    "PL01": "Information System Developer",
    "PL02": "IT Consultan",
    "PL03": "Data Spesialist",
    "PL04": "Business & System Analyst",
    "PL05": "Entrepreneurship Resource Planning Architect",
}

MAPPING = {
    1: ("PL01", "PL04"),
    2: ("PL02", "PL04"),
    3: ("PL03", "PL02"),
    4: ("PL04", "PL02"),
    5: ("PL05", "PL04"),
    6: ("PL02", "PL03"),
    7: ("PL03", "PL04"),
    8: ("PL04", "PL02"),
    9: ("PL05", "PL04"),
    10: ("PL01", "PL05"),
    11: ("PL03", "PL01"),
    12: ("PL01", "PL02"),
    13: ("PL05", "PL03"),
    14: ("PL04", "PL05"),
    15: ("PL03", "PL02"),
}

OUTPUT_CSV = os.path.join(os.path.dirname(__file__), "dataset", "hasil_kuesioner_pl.csv")


def calculate_scores(answers):
    scores = {pl: 0 for pl in PL_LABELS}
    for idx, answer in answers.items():
        if answer != "Ya":
            continue
        utama, pendukung = MAPPING[idx]
        scores[utama] += 2
        scores[pendukung] += 1
    return scores


def ranked_results(scores):
    return sorted(scores.items(), key=lambda item: item[1], reverse=True)


def ensure_csv_header(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if os.path.exists(path):
        return

    headers = [
        "timestamp",
        "nim",
        "nama",
    ]
    headers.extend([f"q{i}" for i in range(1, 16)])
    headers.extend([f"score_{pl.lower()}" for pl in PL_LABELS])
    headers.extend(["top1_pl", "top1_profesi", "top2_pl", "top2_profesi"])

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)


def append_result(path, identity, answers, scores, top_two):
    row = [
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        identity["nim"],
        identity["nama"],
    ]
    row.extend([answers[i] for i in range(1, 16)])
    row.extend([scores[pl] for pl in PL_LABELS])

    top1_pl, _ = top_two[0]
    top2_pl, _ = top_two[1]
    row.extend([
        top1_pl,
        PL_LABELS[top1_pl],
        top2_pl,
        PL_LABELS[top2_pl],
    ])

    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(row)


st.title("📊 Kuesioner Pemetaan Profesi Lulusan (PL) SI")
st.caption("Jawab Ya/Tidak, sistem menghitung skor otomatis dan menyimpan data mahasiswa ke CSV.")

with st.form("form_kuesioner_pl"):
    st.subheader("Identitas Mahasiswa")
    col1, col2 = st.columns(2)
    with col1:
        nim = st.text_input("NIM *")
    with col2:
        nama = st.text_input("Nama Lengkap *")

    st.subheader("Pertanyaan")
    answers = {}
    for i, question in enumerate(QUESTIONS, start=1):
        answers[i] = st.radio(
            f"{i}. {question}",
            options=["Ya", "Tidak"],
            index=1,
            horizontal=True,
            key=f"q_{i}",
        )

    submitted = st.form_submit_button("Hitung & Simpan", type="primary")

if submitted:
    identity = {
        "nim": nim.strip(),
        "nama": nama.strip(),
    }

    if not identity["nim"] or not identity["nama"]:
        st.error("NIM dan Nama wajib diisi.")
    else:
        scores = calculate_scores(answers)
        ranking = ranked_results(scores)

        ensure_csv_header(OUTPUT_CSV)
        append_result(OUTPUT_CSV, identity, answers, scores, ranking)

        st.success("Hasil berhasil dihitung dan disimpan ke CSV.")

        top1_pl, top1_score = ranking[0]
        top2_pl, top2_score = ranking[1]

        m1, m2 = st.columns(2)
        with m1:
            st.metric("Rekomendasi Utama", f"{top1_pl} - {PL_LABELS[top1_pl]}", f"Skor {top1_score}")
        with m2:
            st.metric("Rekomendasi Alternatif", f"{top2_pl} - {PL_LABELS[top2_pl]}", f"Skor {top2_score}")

        st.markdown("### Detail Skor")
        score_rows = [
            {"Kode PL": pl, "Profesi": PL_LABELS[pl], "Skor": score}
            for pl, score in ranking
        ]
        st.dataframe(score_rows, use_container_width=True)

        st.caption(f"File tersimpan: {OUTPUT_CSV}")

st.divider()
st.markdown("### Tentang Aplikasi")
st.markdown("Aplikasi ini digunakan untuk memetakan profesi lulusan berdasarkan jawaban kuesioner. Sistem menghitung skor otomatis dan menyimpan data mahasiswa ke CSV.")