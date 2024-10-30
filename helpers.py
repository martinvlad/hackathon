import autogen
import pandas as pd
import chromadb
from datetime import datetime
import time
import os
import streamlit as st
from autogen import AssistantAgent
from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent
from dotenv import load_dotenv
load_dotenv()

def response_stream(res):
    for word in res.split():
        yield word + " "
        time.sleep(0.05)
def getsheet():
    return {
    'Balance Sheet (in millions of CHF)':'Roche_Multi_Year_Overview.csv',
    'Dia Division – Net operating assets':'Dia_Division.csv',
    'Dia Division – Operating free cash flow':'Dia_Division.csv',
    'DIA Division operating results':'Dia_Division.csv',
    'Dia Division – Sales by customer area':'Dia_Division.csv',
    'Dia Division Sales by Region':'Dia_Division.csv',
    'Income statement in millions of CHF':'Division_Financial_Statements.csv',
    'Pharmaceuticals Division – Net operating assets':'Pharma_Division.csv',
    'Pharmaceuticals Division – Operating free cash flow':'Pharma_Division.csv',
    'Pharmaceuticals Division – Product Sales':'Pharma_Division.csv',
    'Pharmaceuticals Division – Sales by therapeutic area':'Pharma_Division.csv',
    'Roche Division Multi Year Overview of Financial Statements':'Roche_Multi_Year_Overview.csv',
    'Sales by Division in Millions CHF':'Roche_Multi_Year_Overview.csv',
    'Sales by geographical area in millions of CHF':'Roche_Multi_Year_Overview.csv'
    }

def autogen_response(input,sheet_header=None,table_choice=None, use_retrieval=False):
    print(use_retrieval)
    llm_config = {"config_list": [{'model': os.getenv('AZURE_MODEL'),
                                    'api_key': os.getenv('AZURE_API_KEY'),
                                    'api_type': os.getenv('AZURE_API_TYPE'),
                                    'base_url': os.getenv('AZURE_BASE_URL'),
                                    'api_version': os.getenv('AZURE_API_VERSION')}], 
                  "seed": 42}
    if use_retrieval:
        # Setup for retrieval-augmented generation
        user_proxy = autogen.UserProxyAgent(
            name="User_proxy",
            system_message="A human admin.",
            code_execution_config={"last_n_messages": 3, "work_dir": "groupchat", "use_docker": False},
            human_input_mode="NEVER",
             
        )

        ragproxyagent = RetrieveUserProxyAgent(
            name="ragproxyagent",
            human_input_mode="NEVER",
            retrieve_config={
                "task": "qa",
                "docs_path": "/testDATA.md",
                "overwrite": True,
                "use_docker": False
            },
        )
        assistantTwo = AssistantAgent(
            name="assistant",
            system_message="You are a helpful assistant.",
            llm_config=llm_config,
        )
        assistantVisual = AssistantAgent(
            name="assistant",
            system_message="You are a visualization expert.",
            llm_config=llm_config,
        )
        groupchat = autogen.GroupChat(agents=[user_proxy,ragproxyagent, assistantVisual, assistantTwo], messages=[], max_round=20)
        manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=llm_config)
        prompt = f"""Please use python to generate the charts based on \n {input} Save the plot to a .png file."""
        response = user_proxy.initiate_chat(manager, message=prompt)
    else:
        # Default user proxy setup
        
        user_proxy = autogen.UserProxyAgent(
            name="User_proxy",
            system_message="A human admin.",
            code_execution_config={"last_n_messages": 3, "work_dir": "groupchat", "use_docker": False},
            human_input_mode="NEVER",
        )
        coder = autogen.AssistantAgent(
            name="Coder",
            llm_config=llm_config,
        )
        groupchat = autogen.GroupChat(agents=[user_proxy, coder], messages=[], max_round=20)

        manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=llm_config)

    # prompt = f"""Using Python and the following file:  {sheet_header}  and path to dataset: '/Users/tonc/Documents/rochexmsft_ai_hackothan_finance/data/{sheet_source.get(sheet_header)}' \n Answer the following question: \n {input} """
        prompt = f"""Download data from my local file '/Users/tonc/Documents/rochexmsft_ai_hackothan_finance/data/{getsheet().get(sheet_header)}' and {input} Save the plot to a file. Print the fields in a dataset before visualizing it. Save the response of the plot in a png"""
        response = user_proxy.initiate_chat(manager, message=prompt)
        parsed_output = [i for i in [i['content'] for i in response.chat_history if i['name'] == 'Coder'] if 'TERMINATE' in i and i != 'TERMINATE'][0].replace('TERMINATE','')

        return parsed_output