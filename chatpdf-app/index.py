import streamlit as st
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings, HuggingFaceInstructEmbeddings
from langchain.vectorstores import FAISS
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from htmlTemplates import css, bot_template, user_template
from langchain.llms import HuggingFaceHub
import mysql.connector
import bcrypt

db_config = {
    "host": "localhost",
    "user": "root",
    "password": "root",
    "database": "pdfchat"
}

def create_user_table():
    try:
        # Connect to the MySQL database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(255) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL
            )
        ''')
        conn.commit()
        conn.close()
    except mysql.connector.Error as err:
        print(f"Error: {err}")

def register_user(username, password):
    try:
        # Connect to the MySQL database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Check if the username is already registered
        cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            return "Username already taken. Please choose another."

        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Insert the new user into the database
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
        conn.commit()
        conn.close()
        return "Registration successful. You can now log in."
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return "An error occurred during registration."

def login_user(username, password):
    try:
        # Connect to the MySQL database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Check if the username exists in the database
        cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
        user = cursor.fetchone()

        if user:
            # Verify the password
            if bcrypt.checkpw(password.encode('utf-8'), user[2].encode('utf-8')):
                st.session_state.authenticated = True
                return "Login successful."
            else:
                return "Invalid password."
        else:
            return "Username not found. Please register."
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return "An error occurred during login."
        

def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

def get_text_chunks(text):
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    return chunks

def get_vectorstore(text_chunks):
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
    return vectorstore

def get_conversation_chain(vectorstore):
    llm = ChatOpenAI()
    memory = ConversationBufferMemory(memory_key='chat_history', return_messages=True)
    conversation_chain = ConversationalRetrievalChain.from_llm(llm=llm, retriever=vectorstore.as_retriever(), memory=memory)
    return conversation_chain

def handle_userinput(user_question):
    response = st.session_state.conversation({'question': user_question})
    st.session_state.chat_history = response['chat_history']

    for i, message in enumerate(st.session_state.chat_history):
        if i % 2 == 0:
            st.write(user_template.replace("{{MSG}}", message.content), unsafe_allow_html=True)
        else:
            st.write(bot_template.replace("{{MSG}}", message.content), unsafe_allow_html=True)

chat_history = []

def main():
    load_dotenv()
    st.set_page_config(page_title="Chat with multiple PDFs", page_icon=":books:")
    st.write(css, unsafe_allow_html=True)

    if "conversation" not in st.session_state:
        st.session_state.conversation = None

    create_user_table()  # Create user table in the database if it doesn't exist

    st.header("Chat with multiple PDFs :books:")

    # Initialize authenticated attribute
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    # Initialize chat history if it doesn't exist in session state
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Sidebar navigation
    selected_option = st.sidebar.radio("Navigation", ["Sign In", "Sign Up"])
    
    if selected_option == "Sign In":
        # Show sign-in form
        st.subheader("Sign-In")
        username_login = st.text_input("Username:", key="login_username")  # Unique key for login username input
        password_login = st.text_input("Password:", type="password", key="login_password")  # Unique key for login password input
        if st.button("Login"):
            login_result = login_user(username_login, password_login)  # Use username for login
            st.write(login_result)

    elif selected_option == "Sign Up":
        # Show sign-up form
        st.subheader("Sign-Up")
        username_signup = st.text_input("Username:", key="signup_username")  # Unique key for signup username input
        password_signup = st.text_input("Password:", type="password", key="signup_password")  # Unique key for signup password input
        if st.button("Register"):
            registration_result = register_user(username_signup, password_signup)  # Use username for registration
            st.write(registration_result)

     # Main content
    if st.session_state.authenticated:
        # PDF upload option on the main page
        pdf_docs = st.file_uploader("Upload your PDFs here and click on 'Process'", accept_multiple_files=True)
        if pdf_docs:
            with st.spinner("Processing"):
                # get pdf text
                raw_text = get_pdf_text(pdf_docs)

                # get the text chunks
                text_chunks = get_text_chunks(raw_text)

                # create vector store
                vectorstore = get_vectorstore(text_chunks)

                # create conversation chain
                # Create a conversation chain
                if "conversation" not in st.session_state:
                    st.session_state.conversation = None
                if "chat_history" not in st.session_state:
                    st.session_state.chat_history = None

                if st.session_state.conversation is None:
                    st.session_state.conversation = get_conversation_chain(vectorstore)
        # Chatbot interaction
        user_question = st.text_input("Ask a question about your documents:")
        if user_question:
            response = st.session_state.conversation({'question': user_question})
            st.session_state.chat_history.append(response['chat_history'])

            st.write('<div style="display: flex; flex-direction: column;">', unsafe_allow_html=True)
            for i, message in enumerate(response['chat_history']):
                if i % 2 == 0:
                    st.write(user_template.replace("{{MSG}}", message.content), unsafe_allow_html=True)
                else:
                    st.write(bot_template.replace("{{MSG}}", message.content), unsafe_allow_html=True)
            st.write('</div>', unsafe_allow_html=True)

if __name__ == '__main__':
    main()