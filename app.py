import streamlit as st
from pages.GNRC import GNRC
from pages.extraction import extraction


pages = {
    "GNRC": GNRC,
    "Extraction": extraction
}

st.sidebar.title("Navigation")
selection = st.sidebar.radio("Go to", list(pages.keys()))

page = pages[selection]
page()
