import streamlit as st
from openai import OpenAI
import openai
from types import SimpleNamespace
import json
import os
import requests
from PyPDF2 import PdfReader

__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import chromadb 
chroma_client = chromadb.PersistentClient()

# --

# Show title and description.
st.title("MY Lab 4 question answering chatbot with ChromaDB")
language_model = st.sidebar.radio("Select your LLM Service", 
                                  ["OpenAI"
                                   ])
adv_model = st.sidebar.checkbox("Select Advanced Model from Service", None)
st.write(
    "Select your LLM Service from the sidebar"
)
if language_model and not adv_model:
    st.subheader("You are having a conversation with gpt-4o-mini")

st.write("Select Advanced Model for more expensive LLM Model")
if language_model and adv_model:
    st.subheader("You are having a conversation with gpt-4o")

# Assigning the api_key to st.session_state to only run it once. 
if 'openai_client' not in st.session_state:
    openai_api_key = st.secrets["OPENAI_API_KEY"]
    st.session_state.openai_client = OpenAI(api_key=openai_api_key)

open_weather_api = st.secrets["OPENWEATHER_KEY"]

# Defining Location by concatenating city and state. 
city = st.text_input(label = "Enter your city", placeholder =  "Ex. Syracuse")
state = st.text_input(label = "Enter your state", placeholder = "Ex. New York")
location = city + "," + state
# location = location.object()

if not city and not state:
    st.warning("Please add your location")

elif city and not state:
    st.warning("Please add your state")

elif city and state:
    # Creating a function to get weather based on location

    # Defining the function and saving it as a variable before adding it to the list of tools
    tools = [{
        "type" : "function",
        "function" : {
            "name" : "get_current_weather",
            "description" : "Get the current weather",
            "parameters": {
                "type" : "object",
                "properties" : {
                    "location" : {
                        "type" : "string",
                        "description" : "The city and state. E.g. Syracuse,New York"
                    },
                },
                "required" : ["location"]
            }
        }
    }]

    def get_current_weather(location, API_KEY):
        if "," in location:
            location = location.split(",")[0].strip()
        urlbase = "https://api.openweathermap.org/data/2.5/"
        urlweather = f"weather?q={location}&appid={API_KEY}"
        url = urlbase + urlweather
        response = requests.get(url)
        data = response.json()
    # Extract temperatures & Convert Kelvin to Celsius
        temp = data['main']['temp'] - 273.15
        feels_like = data['main']['feels_like'] - 273.15
        temp_min = data['main']['temp_min'] - 273.15 
        temp_max = data['main']['temp_max'] - 273.15
        humidity = data['main']['humidity']
        weather_data = {
            "location": location,
            "temperature": round(temp, 2),
            "feels_like": round(feels_like, 2),
            "temp_min": round(temp_min, 2), 
            "temp_max": round(temp_max, 2),
            "humidity": round(humidity, 2)
            }
        return weather_data
        # Creating an empty list and building a function to append defined functions to the list for the model to choose from.
        
    def chat_completion_requests(model, messages, tools = None, tool_choice = None):
            try:
                response = st.session_state.openai_client.chat.completions.create(
                    model = model,
                    messages = messages,
                    tools = tools,
                    tool_choice = tool_choice
                )
            except Exception as e:
                print()
                response = f"Unable to generate chat completion. \n Execution: {e}"
            return response 

    if location:
        #tools = []
        #def add_to_tools(function_definition):
            #tools.append(function_definition)# Building a function to create a response for the model to choose the tool. 

        # Adding weather function to the tools list    
        # add_to_tools(weather_function_definition)
        # st.write(tools)
        # Using the function from the tools list
        messages = []
        messages.append({"role" : "system", "content" : "Don't make assumptions about what values to plug into functions. Ask for clarification if user request is ambiguous."})
        messages.append({"role" : "user", "content" : f"What is the weather in {location}"})

        if language_model == "OpenAI" and not adv_model:
            # Accessing the fucntion request:
            response = st.session_state.openai_client.chat.completions.create(
                    model = "gpt-4o-mini",
                    messages = messages,
                    tools = tools,
                    tool_choice = "auto"
                )
        else:
            # Accessing the fucntion request:
            response = st.session_state.openai_client.chat.completions.create(
                    model = "gpt-4o",
                    messages = messages,
                    tools = tools,
                    tool_choice = "auto"
                )
        response_message = response.choices[0].message
        messages.append(response_message) 
        print(response_message)       
        tool_calls = response_message.tool_calls
        if tool_calls:
            tool_call_id = tool_calls[0].id
            tool_function_name = tool_calls[0].function.name
            tool_query_string = eval(tool_calls[0].function.arguments)['location']

            if tool_function_name == 'get_current_weather':
                results = get_current_weather(location, st.secrets['OPENWEATHER_KEY'])
                messages.append({
                    "role" : "tool", 
                    "tool_call_id" : tool_call_id,
                    "name" : tool_function_name, 
                    "content" : f" The temp in {results['location']} is {results['temperature']}"})

                model_response_with_function_call = st.session_state.openai_client.chat.completions.create(
                    model = "gpt-4o",
                    messages = messages
                )
                st.write(model_response_with_function_call.choices[0].message.content)
            else:
                st.write(f"Error: {tool_function_name} does not exist")
        else:
            st.write(f"Error: tool does not exist")






# Code from Lab 4

ignore = '''
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
        query_embeddings = [query_embedding]
    )
    docs_id = []
    for i in range(len(results['documents'][0])):
        doc = results['documents'][0][i]
        doc_id = results['ids'][0][i]
        docs_id.append(doc_id)
    #return docs_id
    extracted_texts = {}
    for doc_id in docs_id:
        file_path = os.path.join(folder_path, doc_id)
        with open(file_path, "rb") as pdf_file:
            reader = PdfReader(pdf_file)
            full_text = ""
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                full_text += page.extract_text()
            extracted_texts[doc_id] = full_text
    return extracted_texts

if topic == "Select your topic":
    st.warning("Select a topic from the sidebar to continue")

else:
    search = st.button(f"Click here to search for helpful documents related to {topic}")

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
'''
