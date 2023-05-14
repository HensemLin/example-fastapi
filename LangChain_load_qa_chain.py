import openai
import os
from dotenv import load_dotenv
import pinecone
from langchain.document_loaders.csv_loader import CSVLoader
from langchain.text_splitter import CharacterTextSplitter, RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma, Pinecone
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.llms import OpenAI
from langchain.chains.question_answering import load_qa_chain


class Chatbot():
    """
    - Chatbot without memory
    - Got extra knowledge other than the document
    - Will give weird answer
    """
    def __init__(self, data_file_path, openai_api_key="", pinecone_api_Key="", pinecone_environment=""):
        load_dotenv()
        self.OPENAI_API_KEY = openai_api_key or os.getenv("OPENAI_API_KEY")
        self.PINECONE_API_KEY = pinecone_api_Key or os.getenv("PINECONE_API_KEY")
        self.PINECONE_ENVIRONEMENT = pinecone_environment or os.getenv("PINECONE_ENVIRONEMENT")
        
        self.index_name = 'semantic-search-openai'
        self.data_file_path = data_file_path
        self.documents = None
        self.text_splitter = None
        self.embeddings = None
        self.index = None
        self.initialized = False
        self.initialize()

    def initialize(self):
        print("Initializing Chatbot...")
        openai.api_key = self.OPENAI_API_KEY

        self.loader = CSVLoader(file_path=self.data_file_path, csv_args={'delimiter':","})
        self.documents = self.loader.load()
        print(f"You have {len(self.documents)} document(s) in your data")

        self.text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
        self.documents = self.text_splitter.split_documents(self.documents)
        print(f"Now you have {len(self.documents)} document(s)")

        self.embeddings = OpenAIEmbeddings(openai_api_key=self.OPENAI_API_KEY)

        # Initialize connection to Pinecone and create or connect to an index.
        pinecone.init(
            api_key=self.PINECONE_API_KEY,
            environment=self.PINECONE_ENVIRONEMENT 
        )

        # check if 'openai' index already exists (only create index if not)
        if self.index_name not in pinecone.list_indexes():
            pinecone.create_index(self.index_name, dimension=1536)
            print(f"New index: '{self.index_name}' created")
        # connect to index
        self.index = pinecone.Index(self.index_name)

        self.text_search = Pinecone.from_documents(self.documents, self.embeddings, index_name=self.index_name)
        self.llm = OpenAI(temperature=0.7, openai_api_key=self.OPENAI_API_KEY)
        self.chain = load_qa_chain(self.llm, chain_type="stuff")
        self.initialized = True

    def ask_question(self, query):
        if not self.initialized:
            print("Chatbot not initialized. Initializing...")
            self.initialize()
        texts = self.text_search.similarity_search(query=query, include_metadata=True)
        ans = self.chain.run(input_documents=texts, question=query)
        return ans









