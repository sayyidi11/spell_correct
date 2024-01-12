import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import re
import string
import time
import json
import math

with st.sidebar:
    selected = option_menu("Koreksi Ejaan Query Damerau Levenshtein Distance",
                           ["Dashboard",
                            "Damerau Levenshtein Distance with Distribusi Kamus & Cache",
                            "Damerau Levenshtein Distance with Distribusi Kamus",
                            "Damerau Levenshtein Distance with Cache"])

    default_index = 0

with open("data_cache.json", "r") as json_file:
    data_cache = json.load(json_file)

df = pd.read_csv("data_fix.csv")
df["Panjang"] = df["a-beta"].apply(len)

df_judul_berita = pd.read_excel("../Data_Berita_Pariwisata.xlsx")


def validasi_kata(query_input):
    kamus_baru = df.query(f'Panjang == {len(query_input)}')["a-beta"]
    kamus_baru = pd.DataFrame(kamus_baru)
    return (kamus_baru)


def kamus_damerau(query_input):
    kamus_baru_damerau = df.query(
        f'Panjang >= {len(query_input)-2} & Panjang <= {len(query_input)+2}')["a-beta"]
    kamus_baru_damerau = pd.DataFrame(kamus_baru_damerau)
    return (kamus_baru_damerau)


def cleaning_proses(query_input):
    # Menghapus angka dari string
    result = re.sub(r'\d+', '', query_input)
    # Menghapus tanda baca
    result = result.translate(str.maketrans('', '', string.punctuation))
    return result


def damerau_levenshtein_distance(str1, str2):
    len_str1 = len(str1) + 1
    len_str2 = len(str2) + 1
    d = [[0 for _ in range(len_str2)] for _ in range(len_str1)]

    for i in range(len_str1):
        d[i][0] = i

    for j in range(len_str2):
        d[0][j] = j

    for i in range(1, len_str1):
        for j in range(1, len_str2):
            cost = 0 if str1[i - 1] == str2[j - 1] else 1
            d[i][j] = min(
                d[i - 1][j] + 1,  # Hapus
                d[i][j - 1] + 1,  # Sisip
                d[i - 1][j - 1] + cost,  # Ganti
            )
            if i > 1 and j > 1 and str1[i - 1] == str2[j - 2] and str1[i - 2] == str2[j - 1]:
                d[i][j] = min(d[i][j], d[i - 2][j - 2] + cost)  # Transposisi

    return d[len_str1 - 1][len_str2 - 1]


def perhitungan_cosine(str1, str2):
    # Membuat DataFrame kosong dengan 1 kolom untuk karakter
    atribut_cosine = pd.DataFrame(columns=["Karakter"])

    # Menginisialisasi kolom karakter dengan alfabet dari a hingga z
    atribut_cosine["Karakter"] = list("abcdefghijklmnopqrstuvwxyz")

    # Menginisialisasi kolom Jumlah dengan nilai 0
    atribut_cosine["Jumlah"] = 0
    atribut_cosine["Jumlah2"] = 0

    # Menghitung jumlah kemunculan karakter dalam kata "bagus"
    for huruf in str1:
        jumlah_kemunculan = str1.count(huruf)
        atribut_cosine.loc[atribut_cosine["Karakter"]
                           == huruf, "Jumlah"] = jumlah_kemunculan
    for huruf2 in str2:
        jumlah_kemunculan = str2.count(huruf2)
        atribut_cosine.loc[atribut_cosine["Karakter"]
                           == huruf2, "Jumlah2"] = jumlah_kemunculan
    hasil = atribut_cosine["Jumlah"] * atribut_cosine["Jumlah2"]
    hasill = hasil.sum()
    hasil2 = atribut_cosine["Jumlah"]**2
    hasilku2 = hasil2.sum()
    hasil3 = atribut_cosine["Jumlah2"]**2
    hasilku = hasil3.sum()
    hasil4 = hasilku**0.5
    hasil5 = hasilku2**0.5
    nilai_cosine = hasill/(hasil4*hasil5)
    return (nilai_cosine)


def tokenize(text):
    return text.lower().split()


def create_vector(tokens, vocabulary):
    vector = [tokens.count(word) for word in vocabulary]
    return vector


def cosine_similarity(vector1, vector2):
    dot_product = sum(x * y for x, y in zip(vector1, vector2))
    magnitude1 = math.sqrt(sum(x ** 2 for x in vector1))
    magnitude2 = math.sqrt(sum(y ** 2 for y in vector2))

    if magnitude1 == 0 or magnitude2 == 0:
        return 0

    similarity = dot_product / (magnitude1 * magnitude2)
    return similarity

# # Object notation
# Home, tab1, tab2, tab3, tab4 = st.tabs(
#     ["Home", "Damerau with Distribusi Kamus & Cache", "Damearu with Distirbusi Kamus", "Damerau with Cache", "Konten"])

# with Home:


# page_bg_image = """
# <style>
# [class="css-6qob1r e1akgbir3"]{
# color: #FFFFFF;
# background-color: #FFFFFF;
# }
# </style>"""

# st.markdown(page_bg_image, unsafe_allow_html=True)
if (selected == "Dashboard"):

    st.title("Koreksi Ejaan Query Menggunakan Metode Damerau Levenshtein Distance")
    st.write("Aplikasi ini Merupakan Implementasi Metode Damerau Levenshtein Distance Untuk Koreksi Ejaan Pada Query yang Dimasukkan Dalam Search Engine. Pada Aplikasi Ini Menambahkan 2 Pendekatan Yaitu:")
    st.write("1. Distirbusi Kamus Pada Dataset Kamus Bahasa Indonesia yang Digunakan")
    st.write(
        "2. Penggunaan Cache yang Menyimpan Ejaab Query yang Pernah Dilakukan Koreksi")
    st.write("Dua Pendekatan yang Dilakukan Berfungsi Untuk Meningkatkan Kecepatan Proses Waktu Koreksi yang Dilakukan.")

if (selected == "Damerau Levenshtein Distance with Distribusi Kamus & Cache"):
    st.title("Koreksi Ejaan Damerau with Distibusi Kamus & Cache")

    st.header("_______________________________________")

    if st.button("Data Cache"):
        st.json(data_cache)

    queryku = st.text_input('Masukkan Query')

    if st.button("Koreksi Query"):
        start_time = time.time()
        queryku = queryku.casefold()
        queryku = cleaning_proses(queryku)
        queryku = queryku.split()
        cache = {}
        saran_kata = []  # saran kata = []
        kata_benar = []
        dalam_cache = []
        koreksi_damerau = []
        for kata in queryku:  # For Query
            cek_kata_benar = validasi_kata(kata)  # Validasi Kata Benar
            if kata in cek_kata_benar.values:
                saran_kata.append(kata)
                kata_benar.append(kata)
            elif kata in data_cache:  # Cek Kata Pada Cache
                saran_kata.append(data_cache[kata])
                dalam_cache.append(data_cache[kata])
            else:
                kamus_damerau2 = kamus_damerau(kata)
                # df['Damerau_Levenshtein_Distance'] = df['Kata'].apply(lambda c: damerau_levenshtein_distance(c, kata_target))
                kamus_damerau2["Nilai Jarak"] = kamus_damerau2["a-beta"].apply(
                    lambda x: damerau_levenshtein_distance(x, kata))
                nilai_jarak = kamus_damerau2[kamus_damerau2["Nilai Jarak"] <= 2]
                if len(nilai_jarak) == 0:
                    saran_kata.append(kata)
                    koreksi_damerau.append(kata)
                elif (nilai_jarak["Nilai Jarak"] == 1).any():
                    nilai_jarak = nilai_jarak[nilai_jarak["Nilai Jarak"] == 1]
                    nilai_jarak["Cosine"] = nilai_jarak["a-beta"].apply(
                        lambda c: perhitungan_cosine(c, kata))
                    nilai_cosine_tertinggi = nilai_jarak['Cosine'].idxmax()
                    nilai_cosine_tertinggi = nilai_jarak.at[nilai_cosine_tertinggi, 'a-beta']
                    # nama_tertinggi_usia = df.at[indeks_max_usia, 'Nama']
                    # saran_kata.append(nilai_cosine_tertinggi)
                    saran_kata.append(nilai_cosine_tertinggi)
                    koreksi_damerau.append(nilai_cosine_tertinggi)
                    cache.update({kata: nilai_cosine_tertinggi})
                else:
                    nilai_jarak["Cosine"] = nilai_jarak["a-beta"].apply(
                        lambda c: perhitungan_cosine(c, kata))
                    nilai_cosine_tertinggi = nilai_jarak['Cosine'].idxmax()
                    nilai_cosine_tertinggi = nilai_jarak.at[nilai_cosine_tertinggi, 'a-beta']
                    saran_kata.append(nilai_cosine_tertinggi)
                    koreksi_damerau.append(nilai_cosine_tertinggi)
                    cache.update({kata: nilai_cosine_tertinggi})

        saran_kata = ' '.join(saran_kata)
        st.text(saran_kata)

        end_time = time.time()
        final_time = end_time - start_time
        st.write(f"Lama Proses = {final_time} Detik")

        data_cache.update(cache)
        with open("data_cache.json", "w") as json_file:
            json.dump(data_cache, json_file)

        st.header("_______________________________")
        st.header("List Berita")

        saran_kata = tokenize(saran_kata)
        df_judul_berita["tokens"] = df_judul_berita['Judul'].apply(
            tokenize)

        vocabulary = list(
            set(saran_kata + df_judul_berita["tokens"].explode().unique().tolist()))

        # Membuat vektor untuk setiap data
        data1_vector = create_vector(saran_kata, vocabulary)
        df_judul_berita['vector'] = df_judul_berita['tokens'].apply(
            lambda tokens: create_vector(tokens, vocabulary))

        df_judul_berita['similarity_score'] = df_judul_berita['vector'].apply(
            lambda vector: cosine_similarity(data1_vector, vector))

        df_sorted = df_judul_berita.sort_values(
            by='similarity_score', ascending=False)

        df_sorted = df_sorted.head(5)

        for index, row in df_sorted.iterrows():
            st.markdown(
                f'<h3><a style="color: #FFFFFF;" href="{row["Link"]}">{row["Judul"]}</a></h3>', unsafe_allow_html=True)
            st.markdown(row["Konten"][:200])

        st.header("_______________________________")
        st.header("Detail Koreksi Query")
        st.text(f"Kata Yang Sudah Benar : {kata_benar}")
        st.text(f"Kata Dalam Cache : {dalam_cache}")
        st.text(f"Kata Hasil Proses Koreksi Damerau : {koreksi_damerau}")

if (selected == "Damerau Levenshtein Distance with Distribusi Kamus"):
    st.title("Koreksi Ejaan Damerau with Distibusi Kamus")

    st.header("_______________________________________")

    queryku = st.text_input('Masukkan Query  ')

    if st.button("Koreksi Query  "):
        start_time = time.time()
        queryku = queryku.casefold()
        queryku = cleaning_proses(queryku)
        queryku = queryku.split()
        saran_kata = []  # saran kata = []
        kata_benar = []
        koreksi_damerau = []
        for kata in queryku:  # For Query
            cek_kata_benar = validasi_kata(kata)  # Validasi Kata Benar
            if kata in cek_kata_benar.values:
                saran_kata.append(kata)
                kata_benar.append(kata)
            else:
                kamus_damerau2 = kamus_damerau(kata)
                # df['Damerau_Levenshtein_Distance'] = df['Kata'].apply(lambda c: damerau_levenshtein_distance(c, kata_target))
                kamus_damerau2["Nilai Jarak"] = kamus_damerau2["a-beta"].apply(
                    lambda x: damerau_levenshtein_distance(x, kata))
                nilai_jarak = kamus_damerau2[kamus_damerau2["Nilai Jarak"] <= 2]
                if len(nilai_jarak) == 0:
                    saran_kata.append(kata)
                    koreksi_damerau.append(kata)
                elif (nilai_jarak["Nilai Jarak"] == 1).any():
                    nilai_jarak = nilai_jarak[nilai_jarak["Nilai Jarak"] == 1]
                    nilai_jarak["Cosine"] = nilai_jarak["a-beta"].apply(
                        lambda c: perhitungan_cosine(c, kata))
                    nilai_cosine_tertinggi = nilai_jarak['Cosine'].idxmax()
                    nilai_cosine_tertinggi = nilai_jarak.at[nilai_cosine_tertinggi, 'a-beta']
                    # nama_tertinggi_usia = df.at[indeks_max_usia, 'Nama']
                    # saran_kata.append(nilai_cosine_tertinggi)
                    saran_kata.append(nilai_cosine_tertinggi)
                    koreksi_damerau.append(nilai_cosine_tertinggi)
                else:
                    nilai_jarak["Cosine"] = nilai_jarak["a-beta"].apply(
                        lambda c: perhitungan_cosine(c, kata))
                    nilai_cosine_tertinggi = nilai_jarak['Cosine'].idxmax()
                    nilai_cosine_tertinggi = nilai_jarak.at[nilai_cosine_tertinggi, 'a-beta']
                    saran_kata.append(nilai_cosine_tertinggi)
                    koreksi_damerau.append(nilai_cosine_tertinggi)

        saran_kata = ' '.join(saran_kata)
        st.text(saran_kata)

        end_time = time.time()
        final_time = end_time - start_time
        st.write(f"Lama Proses = {final_time} Detik")

        nilai_jarak

        st.header("_______________________________")
        st.header("List Berita")

        saran_kata = tokenize(saran_kata)
        df_judul_berita["tokens"] = df_judul_berita['Judul'].apply(
            tokenize)

        vocabulary = list(
            set(saran_kata + df_judul_berita["tokens"].explode().unique().tolist()))

        # Membuat vektor untuk setiap data
        data1_vector = create_vector(saran_kata, vocabulary)
        df_judul_berita['vector'] = df_judul_berita['tokens'].apply(
            lambda tokens: create_vector(tokens, vocabulary))

        df_judul_berita['similarity_score'] = df_judul_berita['vector'].apply(
            lambda vector: cosine_similarity(data1_vector, vector))

        df_sorted = df_judul_berita.sort_values(
            by='similarity_score', ascending=False)

        df_sorted = df_sorted.head(5)

        for index, row in df_sorted.iterrows():
            st.markdown(
                f'<h3><a style="color: #FFFFFF;" href="{row["Link"]}">{row["Judul"]}</a></h3>', unsafe_allow_html=True)
            st.markdown(row["Konten"][:200])

        df_sorted

        st.header("_______________________________")
        st.header("Detail Koreksi Query")
        st.text(f"Kata Yang Sudah Benar : {kata_benar}")
        st.text(f"Kata Hasil Proses Koreksi Damerau : {koreksi_damerau}")

if (selected == "Damerau Levenshtein Distance with Cache"):
    st.title("Koreksi Ejaan Damerau with Distibusi Kamus & Cache")

    st.header("_______________________________________")

    if st.button("Data Cache  "):
        st.json(data_cache)

    queryku = st.text_input('Masukkan Query ')

    if st.button("Koreksi Query "):
        start_time = time.time()
        queryku = queryku.casefold()
        queryku = cleaning_proses(queryku)
        queryku = queryku.split()
        cache = {}
        saran_kata = []  # saran kata = []
        kata_benar = []
        dalam_cache = []
        koreksi_damerau = []
        for kata in queryku:  # For Query
            cek_kata_benar = validasi_kata(kata)  # Validasi Kata Benar
            if kata in cek_kata_benar.values:
                saran_kata.append(kata)
                kata_benar.append(kata)
            elif kata in data_cache:  # Cek Kata Pada Cache
                saran_kata.append(data_cache[kata])
                dalam_cache.append(data_cache[kata])
            else:
                kamus_damerau2 = df
                # df['Damerau_Levenshtein_Distance'] = df['Kata'].apply(lambda c: damerau_levenshtein_distance(c, kata_target))
                kamus_damerau2["Nilai Jarak"] = kamus_damerau2["a-beta"].apply(
                    lambda x: damerau_levenshtein_distance(x, kata))
                nilai_jarak = kamus_damerau2[kamus_damerau2["Nilai Jarak"] <= 2]
                if len(nilai_jarak) == 0:
                    saran_kata.append(kata)
                    koreksi_damerau.append(kata)
                elif (nilai_jarak["Nilai Jarak"] == 1).any():
                    nilai_jarak = nilai_jarak[nilai_jarak["Nilai Jarak"] == 1]
                    nilai_jarak["Cosine"] = nilai_jarak["a-beta"].apply(
                        lambda c: perhitungan_cosine(c, kata))
                    nilai_cosine_tertinggi = nilai_jarak['Cosine'].idxmax()
                    nilai_cosine_tertinggi = nilai_jarak.at[nilai_cosine_tertinggi, 'a-beta']
                    # nama_tertinggi_usia = df.at[indeks_max_usia, 'Nama']
                    # saran_kata.append(nilai_cosine_tertinggi)
                    saran_kata.append(nilai_cosine_tertinggi)
                    koreksi_damerau.append(nilai_cosine_tertinggi)
                    cache.update({kata: nilai_cosine_tertinggi})
                else:
                    nilai_jarak["Cosine"] = nilai_jarak["a-beta"].apply(
                        lambda c: perhitungan_cosine(c, kata))
                    nilai_cosine_tertinggi = nilai_jarak['Cosine'].idxmax()
                    nilai_cosine_tertinggi = nilai_jarak.at[nilai_cosine_tertinggi, 'a-beta']
                    saran_kata.append(nilai_cosine_tertinggi)
                    koreksi_damerau.append(nilai_cosine_tertinggi)
                    cache.update({kata: nilai_cosine_tertinggi})

        saran_kata = ' '.join(saran_kata)
        st.text(saran_kata)

        end_time = time.time()
        final_time = end_time - start_time
        st.write(f"Lama Proses = {final_time} Detik")

        data_cache.update(cache)
        with open("data_cache.json", "w") as json_file:
            json.dump(data_cache, json_file)

        st.header("_______________________________")
        st.header("List Berita")

        saran_kata = tokenize(saran_kata)
        df_judul_berita["tokens"] = df_judul_berita['Judul'].apply(
            tokenize)

        vocabulary = list(
            set(saran_kata + df_judul_berita["tokens"].explode().unique().tolist()))

        # Membuat vektor untuk setiap data
        data1_vector = create_vector(saran_kata, vocabulary)
        df_judul_berita['vector'] = df_judul_berita['tokens'].apply(
            lambda tokens: create_vector(tokens, vocabulary))

        df_judul_berita['similarity_score'] = df_judul_berita['vector'].apply(
            lambda vector: cosine_similarity(data1_vector, vector))

        df_sorted = df_judul_berita.sort_values(
            by='similarity_score', ascending=False)

        df_sorted = df_sorted.head(5)

        for index, row in df_sorted.iterrows():
            st.markdown(
                f'<h3><a style="color: #FFFFFF;" href="{row["Link"]}">{row["Judul"]}</a></h3>', unsafe_allow_html=True)
            st.markdown(row["Konten"][:200])

        st.header("_______________________________")
        st.header("Detail Koreksi Query")
        st.text(f"Kata Yang Sudah Benar : {kata_benar}")
        st.text(f"Kata Dalam Cache : {dalam_cache}")
        st.text(f"Kata Hasil Proses Koreksi Damerau : {koreksi_damerau}")

# if (selected == "Konten"):
#     # Data dari DataFrame pandas
#     data1 = ['strategi', 'kerja', 'mesin', 'pencari']

#     # Contoh DataFrame pandas dengan judul berita
#     data2 = pd.DataFrame({
#         'judul_berita': [
#             'panduan lengkap cara kerja mesin pencari',
#             'implementasi algoritma pencarian informasi',
#             'teknologi pemrosesan bahasa alami',
#             'strategi optimasi mesin pencari',
#             'pengembangan algoritma pencarian terbaru'
#         ]
#     })

#     # Tokenisasi judul berita
#     data2['tokens'] = data2['judul_berita'].apply(tokenize)

#     # Membuat vocabulary
#     vocabulary = list(set(data1 + data2['tokens'].explode().unique().tolist()))

#     # Membuat vektor untuk setiap data
#     data1_vector = create_vector(data1, vocabulary)
#     data2['vector'] = data2['tokens'].apply(
#         lambda tokens: create_vector(tokens, vocabulary))

#     # Menghitung cosine similarity untuk setiap judul berita
#     data2['similarity_score'] = data2['vector'].apply(
#         lambda vector: cosine_similarity(data1_vector, vector))

#     # Menampilkan hasil
#     # print(data2[['judul_berita', 'similarity_score']])

#     df_sorted = data2.sort_values(by='similarity_score', ascending=False)
#     df_sorted["judul_berita"]

#     # Mendefinisikan tautan
#     link_url = "https://www.example.com"
#     link_text = "Kunjungi Website"

#     # Menampilkan tombol teks dengan tautan, mengganti warna dan menghilangkan underline
#     st.markdown(
#         f'<h3><a style="color: #FFFFFF; text-decoration: none;" href="{link_url}">{link_text}</a><h3/><br>', unsafe_allow_html=True)

#     st.dataframe(df_judul_berita[["Judul", "Link"]])
#     st.dataframe(df_sorted[["judul_berita", "similarity_score"]])

#     import streamlit as st
#     import pandas as pd

#     # Contoh DataFrame
#     data = {
#         'judul_berita': [
#             'Panduan Lengkap Cara Kerja Mesin Pencari',
#             'Implementasi Algoritma Pencarian Informasi',
#             'Teknologi Pemrosesan Bahasa Alami',
#             'Strategi Optimasi Mesin Pencari',
#             'Pengembangan Algoritma Pencarian Terbaru'
#         ],
#         'link': [
#             'https://example.com/panduan',
#             'https://example.com/implementasi',
#             'https://example.com/teknologi',
#             'https://example.com/strategi',
#             'https://example.com/pengembangan'
#         ]
#     }

#     df = pd.DataFrame(data)

#     # Menampilkan judul berita dan tombol
#     for index, row in df.iterrows():
#         st.markdown(
#             f'<a href="{row["link"]}">**{row["judul_berita"]}**</a>', unsafe_allow_html=True)

#     text = data["judul_berita"][0]
#     text = text[:5]
#     st.write(text)
