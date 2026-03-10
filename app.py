import csv
import os
from datetime import datetime

import streamlit as st
from sklearn.neighbors import KNeighborsClassifier

st.set_page_config(page_title="Kuesioner Pemetaan PL SI", page_icon="📊", layout="wide")

QUESTIONS = [
    "Apakah Anda mampu menganalisis kebutuhan strategis bisnis dan menurunkannya menjadi kebutuhan arsitektur SI?",
    "Apakah Anda mampu melakukan gap analysis kondisi saat ini dan target arsitektur organisasi?",
    "Apakah Anda mampu menyusun roadmap implementasi arsitektur SI yang realistis dan terukur?",
    "Apakah Anda mampu merancang solusi aplikasi/sistem berdasarkan standar pengembangan perangkat lunak?",
    "Apakah Anda mampu menyusun rencana audit TI berbasis risiko dan tujuan pengendalian?",
    "Apakah Anda mampu mengevaluasi rancangan dan efektivitas kontrol TI secara sistematis?",
    "Apakah Anda mampu menyusun laporan hasil audit TI beserta rekomendasi perbaikan yang dapat ditindaklanjuti?",
    "Apakah Anda mampu mengidentifikasi masalah bisnis dan merumuskannya menjadi pertanyaan analitik?",
    "Apakah Anda mampu melakukan pengolahan data (pembersihan, transformasi, validasi) sebelum analisis?",
    "Apakah Anda mampu membangun model analitik sederhana untuk mendukung keputusan berbasis data?",
    "Apakah Anda mampu memvisualisasikan hasil analisis data menjadi dashboard/laporan yang mudah dipahami pemangku kepentingan?",
    "Apakah Anda mampu menerjemahkan kebutuhan bisnis menjadi spesifikasi kebutuhan sistem/perangkat lunak?",
    "Apakah Anda mampu memfasilitasi komunikasi antara pengguna bisnis dan tim teknis dalam pengembangan sistem?",
    "Apakah Anda mampu menganalisis proses bisnis untuk menentukan kebutuhan solusi ERP terintegrasi?",
    "Apakah Anda mampu merencanakan pengujian dan memastikan implementasi ERP berjalan efektif sesuai kebutuhan organisasi?",
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

OUTPUT_CSV = os.path.join(os.path.dirname(__file__), "hasil_kuisioner_pl.csv")


def answer_to_numeric(answer):
    return 1 if answer == "Ya" else 0


def answers_to_vector(answers):
    return [answer_to_numeric(answers[i]) for i in range(1, 16)]


def calculate_scores(answers):
    scores = {pl: 0 for pl in PL_LABELS}
    for idx, answer in answers.items():
        if answer != "Ya":
            continue
        utama, pendukung = MAPPING[idx]
        scores[utama] += 2
        scores[pendukung] += 1
    return scores


def train_knn_from_csv(path, n_neighbors=3):
    if not os.path.exists(path):
        return None, "Belum ada dataset historis untuk melatih KNN."

    x_train = []
    y_train = []

    with open(path, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            label = (row.get("top1_pl") or "").strip()
            if label not in PL_LABELS:
                continue

            try:
                features = []
                for i in range(1, 16):
                    value = (row.get(f"q{i}") or "").strip().lower()
                    if value in ["ya", "1", "true"]:
                        features.append(1)
                    elif value in ["tidak", "0", "false"]:
                        features.append(0)
                    else:
                        raise ValueError("invalid answer")
            except ValueError:
                continue

            x_train.append(features)
            y_train.append(label)

    if len(x_train) < n_neighbors:
        return None, "Data training KNN belum cukup. Minimal data valid >= nilai k."

    model = KNeighborsClassifier(n_neighbors=n_neighbors)
    model.fit(x_train, y_train)
    return model, None


def predict_with_knn(answers, model):
    vector = answers_to_vector(answers)
    predicted = model.predict([vector])[0]
    proba = model.predict_proba([vector])[0]
    classes = model.classes_

    confidence = {classes[i]: float(proba[i]) for i in range(len(classes))}
    ranked = sorted(confidence.items(), key=lambda item: item[1], reverse=True)
    return predicted, ranked


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
        "kelas",
        "angkatan",
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
        identity["kelas"],
        identity["angkatan"],
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
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        nim = st.text_input("NIM *")
    with col2:
        nama = st.text_input("Nama Lengkap *")
    with col3:
        kelas = st.text_input("Kelas")
    with col4:
        angkatan = st.text_input("Angkatan")

    st.subheader("Pertanyaan")
    method = st.selectbox(
        "Metode pemetaan",
        options=["Rule-Based Matrix", "KNN (berbasis data historis)"],
        index=0,
        help="KNN membutuhkan data jawaban historis dengan label top1_pl yang valid.",
    )

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
        "kelas": kelas.strip(),
        "angkatan": angkatan.strip(),
    }

    if not identity["nim"] or not identity["nama"]:
        st.error("NIM dan Nama wajib diisi.")
    else:
        scores = calculate_scores(answers)
        ranking = ranked_results(scores)

        used_method = method
        knn_ranked = None

        if method == "KNN (berbasis data historis)":
            knn_model, knn_error = train_knn_from_csv(OUTPUT_CSV, n_neighbors=3)
            if knn_model is None:
                st.warning(f"KNN tidak bisa digunakan saat ini: {knn_error} Sistem memakai Rule-Based Matrix.")
                used_method = "Rule-Based Matrix"
            else:
                _, knn_ranked = predict_with_knn(answers, knn_model)
                ranking = [(pl, int(round(prob * 100))) for pl, prob in knn_ranked]

        ensure_csv_header(OUTPUT_CSV)
        append_result(OUTPUT_CSV, identity, answers, scores, ranking)

        st.success("Hasil berhasil dihitung dan disimpan ke CSV.")
        st.info(f"Metode yang digunakan: {used_method}")

        top1_pl, top1_score = ranking[0]
        top2_pl, top2_score = ranking[1]

        m1, m2 = st.columns(2)
        with m1:
            metric_label = "Skor" if used_method == "Rule-Based Matrix" else "Kedekatan"
            metric_unit = "poin" if used_method == "Rule-Based Matrix" else "%"
            st.metric("Rekomendasi Utama", f"{top1_pl} - {PL_LABELS[top1_pl]}", f"{metric_label} {top1_score} {metric_unit}")
        with m2:
            st.metric("Rekomendasi Alternatif", f"{top2_pl} - {PL_LABELS[top2_pl]}", f"{metric_label} {top2_score} {metric_unit}")

        st.markdown("### Detail Skor")
        detail_col = "Skor" if used_method == "Rule-Based Matrix" else "Kedekatan (%)"
        score_rows = [
            {"Kode PL": pl, "Profesi": PL_LABELS[pl], detail_col: score}
            for pl, score in ranking
        ]
        st.dataframe(score_rows, use_container_width=True)

        st.caption(f"File tersimpan: {OUTPUT_CSV}")

st.divider()
st.markdown("### Tentang Aplikasi")
st.markdown("Aplikasi ini digunakan untuk memetakan profesi lulusan berdasarkan jawaban kuesioner. Sistem menghitung skor otomatis dan menyimpan data mahasiswa ke CSV.")