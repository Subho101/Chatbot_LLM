import streamlit as st
import os
from dotenv import load_dotenv
from pandasai.llm.openai import OpenAI
from pandasai import PandasAI, SmartDatalake
import pandas as pd

load_dotenv()

st.set_page_config(page_title="Trading ChatBot")

#os.environ["OPENAI_API_KEY"] = "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"
openai_api_key = os.getenv("OPENAI_API_KEY")

llm = OpenAI(api_token=openai_api_key)


if "messages" not in st.session_state.keys():
    st.session_state.messages = [
        {"role": "assistant", "content": "How may I help you?"}]

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])


# Sidebar for uploading csv
with st.sidebar:
    input_csvs = st.file_uploader("Upload your CSV files", type=[
        'csv'], accept_multiple_files=True)
    
    if input_csvs:
        st.info("CSV uploaded successfully")
        
        for uploaded_file in input_csvs:
            uploaded_file.seek(0)

        input_dataframes = [pd.read_csv(file) for file in input_csvs]
        
        smartdata_lake = SmartDatalake(input_dataframes, config={"llm": llm})
        st.session_state['datalake'] = smartdata_lake


# Function for generating LLM response
def generate_response(prompt_input):
    if len(input_csvs) == 0:
        return "Please upload some csv files!!"

    if 'datalake' in st.session_state:
        print(st.session_state)
        smartdata_lake = st.session_state['datalake']
        result = smartdata_lake.chat(prompt_input)
        return result
    else:
        return "Please upload some csv files!!"


# User-provided prompt
if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = generate_response(prompt)
            st.write(response)
    message = {"role": "assistant", "content": response}
    st.session_state.messages.append(message)
