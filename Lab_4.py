import streamlit as st
from openai import OpenAI
import openai
import os
from PyPDF2 import PdfReader

__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import chromadb 
chroma_client = chromadb.PersistentClient()

# Show title and description.
st.title("MY Lab 4 question answering chatbot with ChromaDB")
st.write(
    "Select your LLM Service from the sidebar"
)
st.write("Select Advanced Model for more expensive LLM Model")

# Ask user for their OpenAI API key via `st.text_input`.
# Alternatively, you can store the API key in `./.streamlit/secrets.toml` and access it
# via `st.secrets`, see https://docs.streamlit.io/develop/concepts/connections/secrets-management
#openai_api_key = st.text_input("OpenAI API Key", type="password")
if 'openai_client' not in st.session_state:
    openai_api_key = st.secrets["OPENAI_API_KEY"]
    st.session_state.openai_client = OpenAI(api_key=openai_api_key)

language_model = st.sidebar.radio("Select your LLM Service", 
                                  ["OpenAI"
                                   ])

adv_model = st.sidebar.checkbox("Select Advanced Model from Service", None)

topic = st.sidebar.selectbox("Topic", ("Select your topic", "Text Mining", "GenAI", "Data Science"))

if language_model and adv_model:
    st.subheader("You are having a conversation with gpt-4o")
else:
    st.subheader("You are having a conversation with gpt-4o-mini")

if topic == "Select your topic":
    st.warning("Select a topic from the sidebar to continue")
else:
    search = st.button(f"Click here to search for helpful documents related to {topic}")

    def add_to_collection(collection, texts, filename):
        openai_client = st.session_state.openai_client
        response = openai_client.embeddings.create(
            input = (texts),
            model = "text-embedding-3-small"
        )
        embedding = response.data[0].embedding
        collection.add(
            documents = [texts],
            ids = [filename],
            embeddings = [embedding]
        )

    def query_from_collection(collection, topic):
        openai_client = st.session_state.openai_client
        query_response = openai_client.embeddings.create(
            input = topic,
            model = "text-embedding-3-small"
        )
        query_embedding = query_response.data[0].embedding
        results = collection.query(
            query_embeddings = [query_embedding],
            n_results = 3
        )
        for i in range(len(results['documents'][0])):
            doc = results['documents'][0][i]
            doc_id = results['ids'][0][i]
            st.success(f"The following file syllabus may be helpful: {doc_id}")

    if 'Lab4_vectorDB' not in st.session_state:
        st.session_state['Lab4_vectorDB'] = chroma_client.get_or_create_collection(name = "Mycollection")

    folder_path = "datafiles/"
    for file in os.listdir(folder_path):
        file_extension = file.split('.')[-1]
        if file_extension.lower() == 'pdf':
            file_path = os.path.join(folder_path, file)
            texts = ""
            with open(file_path, "rb") as pdf_file:
                reader = PdfReader(pdf_file)
                for page_num in range(len(reader.pages)):
                    page = reader.pages[page_num]
                    text = page.extract_text()
                    texts += text
            add_to_collection(st.session_state['Lab4_vectorDB'], texts, file)

    if search:
        query_from_collection(st.session_state['Lab4_vectorDB'], topic)