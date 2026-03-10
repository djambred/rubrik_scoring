import csv
import os
from datetime import datetime

import matplotlib.pyplot as plt
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


def load_saved_results(path):
    if not os.path.exists(path):
        return []

    with open(path, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


def parse_score(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def build_radar_chart(row):
    labels = list(PL_LABELS.keys())
    values = [
        parse_score(row.get("score_pl01")),
        parse_score(row.get("score_pl02")),
        parse_score(row.get("score_pl03")),
        parse_score(row.get("score_pl04")),
        parse_score(row.get("score_pl05")),
    ]

    labels_closed = labels + [labels[0]]
    values_closed = values + [values[0]]

    angles = [n / float(len(labels_closed)) * 2 * 3.141592653589793 for n in range(len(labels_closed))]

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    ax.plot(angles, values_closed, linewidth=2)
    ax.fill(angles, values_closed, alpha=0.25)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels)

    max_score = max(values) if values else 1
    upper = max(2, int(max_score + 1))
    ax.set_ylim(0, upper)
    ax.set_yticks(range(0, upper + 1, max(1, upper // 5)))
    ax.set_title("Radar Chart Pemetaan PL", pad=16)
    return fig


def get_max_scores_per_pl():
    max_scores = {pl: 0 for pl in PL_LABELS}
    for q_idx in MAPPING:
        utama, pendukung = MAPPING[q_idx]
        max_scores[utama] += 2
        max_scores[pendukung] += 1
    return max_scores


def get_score_dict_from_row(row):
    return {
        "PL01": parse_score(row.get("score_pl01")),
        "PL02": parse_score(row.get("score_pl02")),
        "PL03": parse_score(row.get("score_pl03")),
        "PL04": parse_score(row.get("score_pl04")),
        "PL05": parse_score(row.get("score_pl05")),
    }


def profile_summary(top_pl):
    summaries = {
        "PL01": "Cenderung kuat di perancangan dan pembangunan solusi sistem secara teknis.",
        "PL02": "Cenderung kuat di evaluasi kontrol, audit, ketelitian, dan rekomendasi perbaikan.",
        "PL03": "Cenderung kuat di pengolahan data, analitik, dan penyajian insight berbasis data.",
        "PL04": "Cenderung kuat sebagai penghubung kebutuhan bisnis ke spesifikasi teknis sistem.",
        "PL05": "Cenderung kuat pada proses bisnis terintegrasi dan solusi ERP lintas fungsi.",
    }
    return summaries.get(top_pl, "Profil kompetensi belum terdeteksi dengan jelas.")


def persistence_tips(top_pl):
    tips = {
        "PL01": [
            "Bangun 1 proyek aplikasi nyata setiap semester sebagai bukti kompetensi.",
            "Konsisten latihan desain arsitektur sederhana dan code review mingguan.",
            "Pilih topik tugas akhir yang langsung terkait pengembangan sistem.",
        ],
        "PL02": [
            "Latih kebiasaan audit mini pada proyek kampus: kontrol, risiko, dan temuan.",
            "Perkuat dokumentasi temuan agar argumentasi rekomendasi lebih tajam.",
            "Ambil studi kasus audit TI untuk portofolio tugas akhir.",
        ],
        "PL03": [
            "Targetkan 1 mini project analitik atau dashboard setiap semester.",
            "Latih alur end-to-end: data cleaning, analisis, visualisasi, dan narasi hasil.",
            "Perkuat statistik terapan agar model analitik lebih akurat.",
        ],
        "PL04": [
            "Biasakan menulis dokumen kebutuhan dan user story pada tiap proyek tim.",
            "Latih fasilitasi diskusi antara user dan tim teknis untuk validasi requirement.",
            "Fokuskan tugas akhir pada analisis kebutuhan dan desain solusi sistem.",
        ],
        "PL05": [
            "Perdalam pemodelan proses bisnis lintas divisi dan integrasi data.",
            "Latih skenario implementasi ERP kecil beserta rencana pengujian.",
            "Bangun portofolio studi kasus optimasi proses berbasis ERP.",
        ],
    }
    return tips.get(top_pl, [])


def on_time_graduation_tips():
    return [
        "Susun peta semester sampai lulus: mata kuliah wajib, prasyarat, magang, dan tugas akhir.",
        "Kunci ritme mingguan 2-3 jam per hari untuk progres akademik dan proyek portofolio.",
        "Tetapkan target IP per semester dan lakukan evaluasi bulanan dengan dosen wali.",
        "Mulai topik tugas akhir maksimal 2 semester sebelum target lulus.",
        "Gunakan indikator peringatan dini: nilai turun, tugas menumpuk, atau progres TA stagnan >2 minggu.",
    ]


def development_focus_areas(score_dict, max_scores):
    weak = []
    for pl, score in score_dict.items():
        max_score = max_scores.get(pl, 1)
        ratio = (score / max_score) if max_score else 0
        if ratio < 0.45:
            weak.append(pl)
    return weak


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

st.divider()
st.markdown("### Dashboard Radar Chart")

saved_rows = load_saved_results(OUTPUT_CSV)
if not saved_rows:
    st.info("Belum ada data pengisian. Silakan isi kuesioner terlebih dahulu.")
else:
    options = []
    for idx, row in enumerate(saved_rows):
        label = f"{row.get('nim', '-')} - {row.get('nama', '-')} ({row.get('timestamp', '-')})"
        options.append((label, idx))

    selected_label = st.selectbox(
        "Pilih responden",
        options=[item[0] for item in options],
        index=len(options) - 1,
    )
    selected_idx = next(item[1] for item in options if item[0] == selected_label)
    selected_row = saved_rows[selected_idx]

    fig = build_radar_chart(selected_row)
    st.pyplot(fig)

    score_dict = get_score_dict_from_row(selected_row)
    ranked = sorted(score_dict.items(), key=lambda item: item[1], reverse=True)
    top_pl = ranked[0][0]
    second_pl = ranked[1][0]
    max_scores = get_max_scores_per_pl()
    weak_areas = development_focus_areas(score_dict, max_scores)

    st.markdown("#### Detail Interpretasi Mahasiswa")
    st.write(f"Profil dominan: {top_pl} - {PL_LABELS[top_pl]}")
    st.write(f"Profil pendukung: {second_pl} - {PL_LABELS[second_pl]}")
    st.write(profile_summary(top_pl))

    st.markdown("#### Cara Bertahan Pada Pilihan Profesi")
    for item in persistence_tips(top_pl):
        st.write(f"- {item}")

    st.markdown("#### Fokus Penguatan")
    if weak_areas:
        weak_text = ", ".join([f"{pl} ({PL_LABELS[pl]})" for pl in weak_areas])
        st.write(f"Area yang masih perlu diperkuat: {weak_text}.")
        st.write("Strategi: ambil proyek/magang yang sengaja melatih area lemah agar profil kompetensi lebih seimbang.")
    else:
        st.write("Tidak ada area lemah yang menonjol. Pertahankan konsistensi latihan dan dokumentasi portofolio.")

    st.markdown("#### Strategi Lulus Tepat Waktu")
    for tip in on_time_graduation_tips():
        st.write(f"- {tip}")