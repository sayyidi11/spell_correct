import streamlit as st
import pandas as pd


df = pd.read_excel("Data_Berita_Pariwisata.excel")
st.dataframe(df)
