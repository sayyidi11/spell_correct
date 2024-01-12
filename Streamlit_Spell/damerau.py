import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import re
import string
import time


with st.sidebar:
    selected = option_menu("Damerau Levenshtein Distance",
                           ["Damerau Levenshtein Distance with Distribusi Kamus",
                            "Damerau Levenshtein Distance with Cache"])

    default_index = 0

if (selected == "Damerau Levenshtein Distance with Distribusi Kamus"):

    st.title("Koreksi Ejaan Damerau")

    df = pd.read_csv("../data_fix.csv")
    # st.dataframe(df.head())

    df["Panjang"] = df["a-beta"].apply(len)
    # st.dataframe(df.head(5))

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
                    d[i][j] = min(d[i][j], d[i - 2][j - 2] +
                                  cost)  # Transposisi

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

    queryku = st.text_input('Masukkan Query')

    if st.button("Koreksi"):
        start_time = time.time()
        queryku = queryku.casefold()
        queryku = cleaning_proses(queryku)
        queryku = queryku.split()
        # st.write(queryku)

        saran_kata = []
        for kata in queryku:
            if kata in df["a-beta"].values:
                saran_kata.append(kata)
            else:
                kamus_damerau2 = df
                # df['Damerau_Levenshtein_Distance'] = df['Kata'].apply(lambda c: damerau_levenshtein_distance(c, kata_target))
                kamus_damerau2["Nilai Jarak"] = kamus_damerau2["a-beta"].apply(
                    lambda x: damerau_levenshtein_distance(x, kata))
                nilai_jarak = kamus_damerau2[kamus_damerau2["Nilai Jarak"] <= 2]
                if len(nilai_jarak) == 0:
                    saran_kata.append(kata)
                else:
                    if (nilai_jarak["Nilai Jarak"] == 1).any():
                        nilai_jarak = nilai_jarak[nilai_jarak["Nilai Jarak"] == 1]
                        nilai_jarak["Cosine"] = nilai_jarak["a-beta"].apply(
                            lambda c: perhitungan_cosine(c, kata))
                        nilai_cosine_tertinggi = nilai_jarak['Cosine'].idxmax()
                        nilai_cosine_tertinggi = nilai_jarak.at[nilai_cosine_tertinggi, 'a-beta']
                    # nama_tertinggi_usia = df.at[indeks_max_usia, 'Nama']
                    # saran_kata.append(nilai_cosine_tertinggi)
                        saran_kata.append(nilai_cosine_tertinggi)
                    else:
                        nilai_jarak["Cosine"] = nilai_jarak["a-beta"].apply(
                            lambda c: perhitungan_cosine(c, kata))
                        nilai_cosine_tertinggi = nilai_jarak['Cosine'].idxmax()
                        nilai_cosine_tertinggi = nilai_jarak.at[nilai_cosine_tertinggi, 'a-beta']
                        saran_kata.append(nilai_cosine_tertinggi)

        saran_kata = ' '.join(saran_kata)
        st.text(saran_kata)

        end_time = time.time()
        final_time = end_time - start_time
        st.write(f"Lama Proses = {final_time} Detik")


if (selected == "Damerau Levenshtein Distance with Cache"):
    st.write("Halo")
