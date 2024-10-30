import streamlit as st
import os
from helpers import *

val_df = pd.read_csv("/Users/martinvlad/hackathon/rochexmsft_ai_hackothan_finance/data/validation_Team Isabel_Ana.csv")
val_df.columns = ['question','source','gt']
val_df_output = val_df.copy()

with st.sidebar:

    retrieval = st.selectbox("Retrieval option",['RAG','Metadata'],0)

    task = st.selectbox("Select model task",['Find insights','Generate charts'],1)

    if task == "Generate charts":
        filename = st.text_input("Enter name of output .png file","file")

if retrieval == "Metadata":
    table_choice = st.selectbox("Choose table to query from",val_df_output['source'].unique())

user_input = st.text_area("Enter input here","")

generate = st.button("Send to model")

if task == "Find insights":
    with st.sidebar.expander("Sample insights questions"):
        st.markdown("""
        - **Balance Sheet (in millions of CHF)**: Can you summarize Roche's non-current assets for 2022 and 2023? 

        - **DIA Division operating result**s: What was the cost of sales for DIA in 2023?

        - **Dia Division – Sales by customer area**: What are the sales for Point of Care in 2022?

        - **Income statement in millions of CHF**: What were Roche's administration expenses in 2023?
        """
        )
else:
    with st.sidebar.expander("Samples charts questions"):
        st.markdown("""
        - **Balance Sheet (in millions of CHF)**: Generate a stacked bar chart of Roche's total liabilities and shareholders' equity from 2019 to 2023.

        - **Balance Sheet (in millions of CHF)**: Create a pie chart depicting the percentage distribution of Roche's total assets between current and non-current assets for 2023.
        """)

def check_file_exists(file_name):
    return os.path.isfile(file_name) and file_name.endswith('.png')

if generate:
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            use_retriever = (retrieval == 'RAG')
            start = time.time()
            if use_retriever:
                response = autogen_response(user_input + f"Name the output PNG file as {filename}.png",table_choice=None, use_retrieval=True)
            else:
              
                response = autogen_response(user_input,table_choice, use_retrieval=False)
                # st.write_stream(response_stream(response))
            exec_time = time.time() - start
            
            st.sidebar.write(f"Response time: {exec_time:.2f} seconds")
    if task == 'Generate charts':
        if check_file_exists(f"/Users/martinvlad/hackathon/groupchat/{filename}.png"):
            print("we're checking filename")
            st.image(f"/Users/martinvlad/hackathon/groupchat/{filename}.png", caption=user_input)
