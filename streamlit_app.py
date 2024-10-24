import streamlit as st

home = st.Page("Home.py", title = "Home Page", default = True)
lab1_page = st.Page("Lab_1.py", title = "Lab 1")
lab2_page = st.Page("Lab_2.py", title = "Lab 2")
lab3_page = st.Page("Lab_3.py", title = "Lab 3")
lab4_page = st.Page("Lab_4.py", title = "Lab 4")
lab5_page = st.Page("Lab_5.py", title = "Lab 5")
labcorrectness_page = st.Page("Lab_correctness.py", title = "Lab Correctness Benchmark")

pg = st.navigation([
    home, 
    lab1_page, 
    lab2_page, 
    lab3_page, 
    lab4_page,
    lab5_page,
    labcorrectness_page
    ])
st.set_page_config(page_title="Lab Manager")
pg.run()