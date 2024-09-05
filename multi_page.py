import streamlit as st

lab1_page = st.Page("Lab 1.py", title = "Lab 1", default = True)
lab2_page = st.Page("Lab 2.py", title = "Lab 2")

pg = st.navigation([lab1_page, lab2_page])
st.set_page_config(page_title="Lab Manager")
pg.run()