# app_name/views.py

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import PyPDF2
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain

# Define variables to store chat history and PDF data
chat_history = []
pdf_data = []

@csrf_exempt  # Disable CSRF protection for this view during development
def process_pdfs(request):
    global pdf_data
    if request.method == 'POST':
        pdf_files = request.FILES.getlist('pdf_files')

        # Extract text from PDFs and concatenate it
        pdf_text = ""
        for pdf_file in pdf_files:
            pdf_reader = PyPDF2.PdfFileReader(pdf_file)
            for page in range(pdf_reader.getNumPages()):
                pdf_text += pdf_reader.getPage(page).extractText()

        # Split the text into chunks
        text_chunks = get_text_chunks(pdf_text)

        # Create a vector store
        vectorstore = get_vectorstore(text_chunks)

        # Create a conversation chain
        create_conversation_chain(vectorstore)

        pdf_data = {
            'text_chunks': text_chunks,
            'vectorstore': vectorstore
        }

        return JsonResponse({'message': 'PDFs processed successfully'})

    return JsonResponse({'error': 'Invalid request method'})

@csrf_exempt  # Disable CSRF protection for this view during development
def handle_user_input(request):
    global chat_history
    if request.method == 'POST':
        user_question = request.POST.get('question')

        # Handle user input and chat logic
        response = get_chat_response(user_question)

        # Update chat history
        chat_history.append({'user': user_question, 'bot': response})

        return JsonResponse({'response': response})

    return JsonResponse({'error': 'Invalid request method'})

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

def create_conversation_chain(vectorstore):
    llm = ChatOpenAI()
    memory = ConversationBufferMemory(
        memory_key='chat_history', return_messages=True)
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(),
        memory=memory
    )
    return conversation_chain

def get_chat_response(user_question):
    global chat_history
    response = chat_history[-1]['bot']  # Default response

    # If a conversation chain has been created, use it to get a response
    if 'conversation_chain' in globals() and conversation_chain:
        response = conversation_chain({'question': user_question})['chat_history'][-1].content

    return response
