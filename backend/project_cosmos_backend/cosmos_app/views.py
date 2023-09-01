from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.llms import HuggingFaceHub

# Initialize global variables to store vectorstore and conversation_chain
vectorstore = None
conversation_chain = None

# Initialize OpenAIEmbeddings
embeddings = OpenAIEmbeddings()

@csrf_exempt
@require_POST
def upload_text(request):
    global vectorstore, conversation_chain

    # Check if text data has been provided in the request
    request_data = json.loads(request.body.decode('utf-8'))
    pdf_text = request_data.get('pdf_text', '')

    if pdf_text:
        # Split text into chunks
        text_chunks = split_text_into_chunks(pdf_text)

        # Create or update the vectorstore
        vectorstore = create_or_update_vectorstore(text_chunks)

        # Create a new conversation chain
        conversation_chain = create_conversation_chain(vectorstore)

        return JsonResponse({'message': 'Text uploaded successfully'})
    else:
        return JsonResponse({'error': 'No text data found in the request'}, status=400)

@csrf_exempt
@require_POST
def semantic_search(request):
    global conversation_chain

    # Check if a user query is provided
    user_query = request.POST.get('user_query', '')
    if user_query:
        # Perform semantic search
        similar_chunks_indices = perform_semantic_search(user_query, conversation_chain)

        return JsonResponse({'similar_chunks_indices': similar_chunks_indices})
    else:
        return JsonResponse({'error': 'No user query provided'}, status=400)

# The rest of your code remains unchanged

def split_text_into_chunks(text):
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    return chunks

def create_or_update_vectorstore(text_chunks):
    # Create or update the vectorstore
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

def perform_semantic_search(user_query, conversation_chain):
    # Generate embedding for the user query
    query_embedding = embeddings.embed_text(user_query)
    
    # Perform semantic search and get similar text chunks
    similar_chunks = conversation_chain.retrieve_most_similar(
        query_embedding, k=5)  # Adjust 'k' as needed
    
    # Get the indices of similar text chunks
    similar_chunks_indices = [chunk.index for chunk in similar_chunks]
    
    return similar_chunks_indices
