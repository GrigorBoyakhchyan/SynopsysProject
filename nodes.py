from langchain.prompts import PromptTemplate
from langchain_google_genai import GoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

llm = GoogleGenerativeAI(model= "gemini-2.0-flash")

def question(state):
    """Answering the question with LangChain"""

    prompt = PromptTemplate.from_template("""
        You are a helpful, friendly,and knowledgeable assistant. 
        Answer the user's question clearly and accurately,
        while maintaining a warm and approachable tone. If the question is complex,
        break it down into easy-to-understand parts. 
        Do not overcomplicate things — keep your response informative, 
        but make the user feel comfortable and understood.
                                        
        User's question: {question}""")
    chain = prompt | llm

    question_text = state.get("query", "") or state.get("answer", "")

    if not question_text:
        return {"error": "No question provided."}
    
    answer = chain.invoke({"question": question_text})
    return {"answer": answer, "query": question_text}

def generate_code(state):
    """Generating the code with LangChain"""

    prompt = PromptTemplate.from_template("""   
        You are a skilled programmer. Write a complete and working piece of code that solves the following request: "{request}"

        - If the user specified the programming language, use that.
        - If not, choose the language that is best suited for the task.
        - Keep the code clean, efficient, and readable.
        - Do not add explanations or comments unless asked.""")
    chain = prompt | llm

    user_request_code = state.get("query", "") or state.get("answer", "")

    if not user_request_code:
        return {"error": "No request to generating code provided."}

    generated_code = chain.invoke({"request": user_request_code})

    return {"generate_code": generated_code, "query": user_request_code}

def edit_code(state):
    """Editing the code with LangChain"""

    prompt = PromptTemplate.from_template("""   
        Edit a code that will satisfy the user's request: {request}.
        explain what the problem was and show the changes step by step using a comment in the new code.
        Like this:
        User_code -> prnit("Hello World!!!")
        AI_edited_code -> print("Hello World!!!) # You misspelled the word <print>""")

    chain = prompt | llm

    user_request_edit_code = state.get("query", "") or state.get("answer", "")

    if not user_request_edit_code:
        return {"error": "No request to editing code provided."}
    
    edited_code = chain.invoke({"request": user_request_edit_code})

    return {"edit_code": edited_code, "query": user_request_edit_code}

def generate_text(state):
    """Generating the text with LangChain"""

    prompt = PromptTemplate.from_template("""   
        Generate a text that will satisfy the user's request: {request}.
        The generated text must be in the language in which the user requests,
        otherwise if the user did not specify the language,
        then respond in the language in which the request was made.""")

    chain = prompt | llm

    user_request_text = state.get("query", "") or state.get("answer", "")

    if not user_request_text:
        return {"error": "No request to generating text provided."}

    generated_text = chain.invoke({"request": user_request_text})

    return {"generate_text": generated_text, "query": user_request_text}

def edit_text(state):
    """Editing the text with LangChain"""

    prompt = PromptTemplate.from_template("""   
        Edit a text that will satisfy the user's request: {request}.
        explain what the problem was and show the changes step by step using a comments in the text redactor.
        Like this:
        User_text -> Hi, my name are Maria.
        AI_edited_code -> Hi my name is Maria.(You've made a grammatical mistake.)
        Or like this:
        User_text -> Hi, my name is Maria, I'm fron London.
        AI_edited_code -> Hi my name is Maria, I'm from London.(You've made a orthographic mistake.)""")

    chain = prompt | llm

    user_request_edit_text = state.get("query", "") or state.get("answer", "")

    if not user_request_edit_text:
        return {"error": "No request to editing text provided."}
    
    edited_text = chain.invoke({"request": user_request_edit_text})

    return {"edit_text": edited_text, "query": user_request_edit_text}

def save_code(state):
    """Saving edited/generated code"""

    prompt = PromptTemplate.from_template("""
        Save the code that was generated/edited: {code}.
        The code must be saved in the appropriate file.
        Code in c++ => output.cpp
        Code in python => output.py
        Code in javascript => output.js
        Code in java => output.java
        Code in go => output.go
        Code in php => output.php
        Code in ruby => output.rb
        Code in c# => output.cs
        Code in rust => output.rs""")
    
    chain = prompt | llm

    user_request_code_s = state.get("query", "") or state.get("answer", "")

    if not user_request_code_s:
        return {"error": "No request to saving code provided."}

    saved_code = chain.invoke({"code": user_request_code_s})
    
    return {"save_code": saved_code, "query": user_request_code_s}

def save_text(state):
    """Saving edited/generated text"""

    prompt = PromptTemplate.from_template("""
        Save the text that was generated/edited: {text}.
        The text must be saved in file output.txt.""")
    
    chain = prompt | llm

    user_request_text_s = state.get("query", "") or state.get("answer", "")

    if not user_request_text_s:
        return {"error": "No request to saving text provided."}

    saved_text = chain.invoke({"text": user_request_text_s})
    
    return {"save_text": saved_text, "query": user_request_text_s}    

def router(state):
    """Routing the state based on the input"""

    prompt = PromptTemplate.from_template("""
        Route the state based on the input: {input}.
        If the input is a question, route to "question".
        If the input is code, route to "code".
        If the input is text, route to "text".
        Respond ONLY with one of: question, code, text.""")
    
    chain = prompt | llm
    routing = chain.invoke({"input": state["query"]})

    result = str(routing).strip().lower()

    return {"next": result if result in ["question", "code", "text"] else "text"}

def code_router(state):
    """Routing the state based on the input for code"""

    prompt = PromptTemplate.from_template("""
        You are an AI assistant that decides whether the user wants to generate new code or edit existing code.

        If the input asks to create, write, build, implement or generate something new — respond with: generate_code  
        If the input asks to fix, refactor, edit, correct, improve or modify existing code — respond with: edit_code  

        Respond ONLY with one of the following (no quotes, no explanations):  
        generate_code  
        edit_code

        Input: {input}""")
    
    chain = prompt | llm

    user_request = state.get("query", "") or state.get("answer", "")
    if not user_request:
        return {"next", "generate_code"}
    
    routing = chain.invoke({"input": user_request})

    result = str(routing).strip().lower()

    return {"next" : result if result in ["generate_code", "edit_code"] else "generate_code"}

def text_router(state):
    """Routing the state based on the input for text"""

    prompt = PromptTemplate.from_template("""
        You are an AI assistant that decides whether the user wants to generate new text or edit existing text.

        If the input asks to create, write, describe, build or generate something — respond with: generate_text  
        If the input asks to fix, edit, improve, rewrite, correct grammar or spelling — respond with: edit_text  

        Respond ONLY with one of the following (no quotes, no explanations):  
        generate_text  
        edit_text

        Input: {input}""")
    
    chain = prompt | llm

    user_request = state.get("query", "") or state.get("answer", "")
    if not user_request:
        return {"next": "generate_text"}
    
    routing = chain.invoke({"input": user_request})

    result = str(routing).strip().lower()

    return {"next": result if result in ["generate_text", "edit_text"] else "generate_text"}

def passtrough(state):
    """Pass through the state without any changes"""
    return state