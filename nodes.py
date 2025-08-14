from langchain.prompts import PromptTemplate
from langchain_google_genai import GoogleGenerativeAI
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

llm = GoogleGenerativeAI(model= "gemini-2.0-flash")

def _take_incoming(state: dict, *keys: str)->str:
    for k in keys:
        v = state.get(k,"")
        if isinstance(v, str) and v.strip():
            return v
    return ""


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

    question_text = _take_incoming(state, "query", "answer")

    if not question_text:
        return {"error": "No question provided."}
    
    answer = chain.invoke({"question": question_text})
    return {"answer": str(answer), "query": question_text}

def generate_code(state):
    """Generating the code with LangChain"""

    prompt = PromptTemplate.from_template("""   
        You are a skilled programmer. Write a complete and working piece of code that solves the following request: "{request}"

        - If the user specified the programming language, use that.
        - If not, choose the language that is best suited for the task.
        - Keep the code clean, efficient, and readable.
        - Do not add explanations or comments unless asked.""")
    chain = prompt | llm

    user_request_code = _take_incoming(state, "query", "answer")

    if not user_request_code:
        return {"error": "No request to generating code provided."}

    generated_code = chain.invoke({"request": user_request_code})

    return {"generate_code": str(generated_code), "query": user_request_code}

def edit_code(state):
    """Editing the code with LangChain"""

    prompt = PromptTemplate.from_template("""   
        Edit a code that will satisfy the user's request: {request}.
        explain what the problem was and show the changes step by step using a comment in the new code.
        Like this:
        User_code -> prnit("Hello World!!!")
        AI_edited_code -> print("Hello World!!!) # You misspelled the word <print>""")

    chain = prompt | llm

    user_request_edit_code = _take_incoming(state, "query", "answer", "generate_code")

    if not user_request_edit_code:
        return {"error": "No request to editing code provided."}
    
    edited_code = chain.invoke({"request": user_request_edit_code})

    return {"edit_code": str(edited_code), "query": user_request_edit_code}

def generate_text(state):
    """Generating the text with LangChain"""

    prompt = PromptTemplate.from_template("""   
        Generate a text that will satisfy the user's request: {request}.
        The generated text must be in the language in which the user requests,
        otherwise if the user did not specify the language,
        then respond in the language in which the request was made.""")

    chain = prompt | llm

    user_request_text = _take_incoming(state, "query", "answer")

    if not user_request_text:
        return {"error": "No request to generating text provided."}

    generated_text = chain.invoke({"request": user_request_text})

    return {"generate_text": str(generated_text), "query": user_request_text}

def edit_text(state):
    """Editing the text with LangChain"""

    prompt = PromptTemplate.from_template("""   
        Edit a text that will satisfy the user's request: {request}.
        explain what the problem was and show the changes step by step using comments in the text redactor.
        Like this:
        User_text -> Hi, my name are Maria.
        AI_edited_code -> Hi my name is Maria.(You've made a grammatical mistake.)
        Or like this:
        User_text -> Hi, my name is Maria, I'm fron London.
        AI_edited_code -> Hi my name is Maria, I'm from London.(You've made a orthographic mistake.)""")

    chain = prompt | llm

    user_request_edit_text = _take_incoming(state, "query", "answer", "generate_text")

    if not user_request_edit_text:
        return {"error": "No request to editing text provided."}
    
    edited_text = chain.invoke({"request": user_request_edit_text})

    return {"edit_text": str(edited_text), "query": user_request_edit_text}

def save_code(state):
    """Saving edited/generated code"""

    prompt = PromptTemplate.from_template("""
        Decide the best filename from this fixed set:
        output.cpp, output.py, output.js, output.java, output.go,
        output.php, output.rb, output.cs, output.rs

        Return STRICTLY in this format (no extra text, no code fences):
        FILENAME: <chosen_name>
        <code content here>

        Code to save:
        {code}""")
    
    chain = prompt | llm

    user_request_code_s = _take_incoming(state, "edit_code", "generate_code", "answer", "query")
    if not user_request_code_s:
        return {"error": "No request to saving code provided."}

    llm_out = str(chain.invoke({"code": user_request_code_s})).strip()
    lines = llm_out.splitlines()

    if not lines:
        return {"error": "LLM returned empty content for saving code"}
    
    header = lines[0].strip()
    prefix = "FILENAME: "

    if not header.startswith(prefix):
        filename = "output.py"
        code_text = llm_out
    else:
        filename = header[len(prefix):].strip() or "output.py"
        code_text = "\n".join(lines[1:])

    path = Path(filename)
    path.write_text(code_text, encoding="utf-8")

    return {"save_code": f"Saved to {path.resolve()}"}

def save_text(state):
    """Persist generated/edited text to output.txt"""
    
    user_request_text_s = _take_incoming(state, "edit_text", "generate_text", "answer", "query")

    if not user_request_text_s:
        return {"error": "No text to save"}
    
    path = Path("output.txt")
    path.write_text(str(user_request_text_s), encoding="utf-8")

    return {"save_text": f"Saved to {path.resolve()}"}

def router(state):
    """Routing the state based on the input"""

    prompt = PromptTemplate.from_template("""
        Route the state based on the input: {input}.
        If the input is a question, route to "question".
        If the input is code, route to "code".
        If the input is text, route to "text".
        Respond ONLY with one of: question, code, text.""")
    
    chain = prompt | llm
    incoming = _take_incoming(state, "query")
    if not incoming:
        return "text"

    routing = chain.invoke({"input": incoming})
    result = str(routing).strip().lower()

    return result if result in ("question", "code", "text") else "text"

def code_router(state):
    """Routing the state based on the input for code: generate_code vs edit_code"""

    prompt = PromptTemplate.from_template("""
        Decide what the user wants:
        - new code → respond: generate_code
        - fix/refactor existing → respond: edit_code

        Input: {input}
        ONLY one of: generate_code, edit_code""")
    
    chain = prompt | llm

    incoming = _take_incoming(state, "query", "answer", "generate_code", "edit_code")
    if not incoming:
        return "generate_code"
    
    routing = chain.invoke({"input": incoming})
    result = str(routing).strip().lower()

    return result if result in ("generate_code", "edit_code") else "generate_code"

def text_router(state):
    """Routing the state based on the input for text: generate_text vs edit_text"""

    prompt = PromptTemplate.from_template("""
        Decide what the user wants:
        - generate new text → respond: generate_text
        - edit/improve existing → respond: edit_text

        Input: {input}
        ONLY one of: generate_text, edit_text""")
    
    chain = prompt | llm

    incoming = _take_incoming(state, "query", "answer", "generate_text", "edit_text")
    
    if not incoming:
        return "generate_text"
    
    routing = chain.invoke({"input": incoming})
    result = str(routing).strip().lower()

    return result if result in ("generate_text", "edit_text") else "generate_text"