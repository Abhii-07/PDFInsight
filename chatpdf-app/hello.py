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



# Define a function for the home page
def home_page():
    st.title("PDF Chat App 🤖")
    st.write("Welcome to the PDF Chat App!")

    st.header("Chat with Your PDFs 📚")
    st.write("The PDF Chat App allows you to have a conversation with your PDF documents. "
             "You can ask questions, seek information, and get instant responses from your PDFs "
             "using plain language queries. 💬")

    st.header("How It Works 🧠")
    st.write("Our application utilizes state-of-the-art language models to understand your queries "
             "and retrieve relevant information from your PDF files. It's like having a smart assistant "
             "for your documents! 📄🤖")

    st.header("Key Features 🚀")
    st.markdown("- **Natural Language Queries:** Ask questions in plain English, and the app will understand. 🗣️"
                "\n- **Multi-Document Support:** Chat with multiple PDFs at the same time. 📚📚"
                "\n- **Real-time Responses:** Get answers instantly as you chat with your documents. ⏱️")

    st.header("Benefits 🌟")
    st.markdown("- **Efficiency:** Save time by quickly finding information in your PDFs. ⏳"
                "\n- **Accessibility:** Make your PDF content more accessible and user-friendly. ♿")

    st.header("Language Models (LLMs) 🤯")
    st.write("Our app harnesses the power of advanced language models, including ChatGPT, "
             "to enhance your document interaction experience. 💪")

    st.header("Security 🔒")
    st.write("We prioritize the security of your data and documents. Rest assured that your information is safe with us. 🛡️")

    st.header("Getting Started 🚀")
    st.write("1. Sign in or register to access the app."
             "\n2. Upload your PDFs to start chatting with them."
             "\n3. Ask questions and enjoy instant responses! 📥🗨️")

    st.header("FAQs ❓")
    # FAQ accordion
    with st.expander("How do I sign in or register?"):
        st.write("To sign in, click on the 'Sign In' page and enter your username and password. "
                 "If you don't have an account, you can register on the 'Sign Up' page. 📝🔐")

    with st.expander("What types of PDFs are supported?"):
        st.write("The app supports a wide range of PDF documents, including text-based PDFs and those with images. "
                 "It can extract text and provide responses based on the content of your PDFs. 📄🖼️")

    with st.expander("How accurate are the responses?"):
        st.write("The accuracy of responses depends on the content and quality of your PDFs. "
                 "The app uses advanced language models to provide the best possible answers. 📈🧐")

    with st.expander("Is my data stored securely?"):
        st.write("Yes, we take data security seriously. Your data and documents are stored securely, "
                 "and we follow best practices to protect your information. 🔒🏢")

    st.header("Contact Us 📧")
    st.write("If you have any questions or feedback, please feel free to [contact our support team](mailto:support@example.com). 📩🙋‍♂️")

# Define a function for the Sign In tab
# Initialize the MySQL connection
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "root",
    "database": "pdfchat"
}

# cursor = mydb.cursor()

# Create the users table if it doesn't exist
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


# Define a function for the Sign In page
# Define a function for the Sign In page
def sign_in_page():
    st.title("Sign In")

    # Initialize the MySQL connection
    db_config = {
        "host": "localhost",
        "user": "root",
        "password": "root",
        "database": "pdfinsights"
    }

    # Create a cursor for database operations
    cursor = None

    # Sign In form
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    try:
        # Connect to the MySQL database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        if st.button("Sign In"):
            # Verify user credentials with MySQL
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()
            if user and bcrypt.checkpw(password.encode('utf-8'), user[2].encode('utf-8')):
                st.success("Successfully logged in!")
                st.session_state.is_authenticated = True
            else:
                st.error("Invalid credentials!")

        # Sign Up button that opens the Sign Up form
        if st.button("Sign Up"):
            st.session_state.show_sign_up = True

        # Show Sign Up form if the button is clicked
        if st.session_state.get("show_sign_up"):
            st.title("Sign Up")
            new_username = st.text_input("New Username")
            new_password = st.text_input("New Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            if new_password == confirm_password and st.button("Register"):
                # Hash the new password
                hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

                # Store the new user in MySQL
                cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (new_username, hashed_password))
                conn.commit()

                st.success("Successfully registered and logged in!")
                st.session_state.is_authenticated = True
            elif new_password != confirm_password:
                st.error("Passwords do not match!")

    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


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
# Define a function for the chat page
# Define a function for the chat page
def chat_page():
    if "conversation" not in st.session_state:
        st.session_state.conversation = None

    st.header("Chat with multiple PDFs :books:")

    # Initialize chat history as an empty list if it doesn't exist
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Main content
    if st.session_state.is_authenticated:
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
                if "conversation" not in st.session_state:
                    st.session_state.conversation = None

                if st.session_state.conversation is None:
                    st.session_state.conversation = get_conversation_chain(vectorstore)
        # Chatbot interaction
        user_question = st.text_input("Ask a question about your documents:")
        if user_question:
            response = st.session_state.conversation({'question': user_question})
            # Assign the response chat history to the chat_history variable
            chat_history = response['chat_history']

            st.write('<div style="display: flex; flex-direction: column;">', unsafe_allow_html=True)
            for i, message in enumerate(chat_history):
                if i % 2 == 0:
                    st.write(user_template.replace("{{MSG}}", message.content), unsafe_allow_html=True)
                else:
                    st.write(bot_template.replace("{{MSG}}", message.content), unsafe_allow_html=True)
            st.write('</div>', unsafe_allow_html=True)
    else:
        st.warning("Please sign in to access the Chat App.")



# Define a function for the navigation bar
def navigation_bar():
    st.sidebar.title("Navigation")
    if hasattr(st.session_state, "is_authenticated") and st.session_state.is_authenticated:
        page = st.sidebar.radio("Select a Page", ["Home", "Chat"])
    else:
        page = st.sidebar.radio("Select a Page", ["Home", "Sign In"])
    return page

# Load your other functions and constants here

load_dotenv()

# Main function
def main():
    page = navigation_bar()
    create_user_table()

    if page == "Home":
        home_page()
    elif page == "Sign In":
        sign_in_page()
    elif page == "Chat":
        chat_page()

if __name__ == '__main__':
    main()
