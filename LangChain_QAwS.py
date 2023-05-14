from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.embeddings.cohere import CohereEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores.elastic_vector_search import ElasticVectorSearch
from langchain.vectorstores import Chroma
from langchain.docstore.document import Document
from langchain.document_loaders.csv_loader import CSVLoader
from langchain.prompts import PromptTemplate
from langchain.chains.qa_with_sources import load_qa_with_sources_chain
from langchain.llms import OpenAI
import openai
import os
from dotenv import load_dotenv
import pinecone


class Chatbot():
    """
    - Chatbot without memory
    - Does not have any knowledge other than the document
    - Will return "I don't know" if asked with irrelevant question
    - Will return weird answer 
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
        self.vectorstore = None
        self.index = None
        self.memory = None
        self.qa = None
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
        self.docsearch = Chroma.from_documents(self.documents, self.embeddings, metadatas=[{"source": str(i)} for i in range(len(self.documents))])

        # initialize connection to pinecone (get API key at app.pinecone.io)
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

        refine_prompt, question_prompt = self.custom_prompts()
        # self.chain = load_qa_with_sources_chain(OpenAI(temperature=0.7), chain_type="map_reduce", return_intermediate_steps=True, question_prompt=QUESTION_PROMPT, combine_prompt=COMBINE_PROMPT)
        self.chain = load_qa_with_sources_chain(OpenAI(temperature=0.7), chain_type="refine", question_prompt=question_prompt, refine_prompt=refine_prompt)
        
        self.initialized = True

    def custom_prompts(self):
        refine_template = (
            "The original question is as follows: {question}\n"
            "We have provided an existing answer, including sources: {existing_answer}\n"
            "We have the opportunity to refine the existing answer"
            "(only if needed) with some more context below.\n"
            "------------\n"
            "{context_str}\n"
            "------------\n"
            "Given the new context, refine the original answer to better "
            "answer the question (in English)"
            "If the context isn't useful, return the original answer."
        )
        refine_prompt = PromptTemplate(
            input_variables=["question", "existing_answer", "context_str"],
            template=refine_template,
        )
        
        question_template = (
            "Context information is below. \n"
            "---------------------\n"
            "{context_str}"
            "\n---------------------\n"
            "Given the context information and not prior knowledge, "
            "answer the question in English: {question}\n"
        )
        question_prompt = PromptTemplate(
            input_variables=["context_str", "question"], template=question_template
        )

        return refine_prompt, question_prompt

    def ask_question(self, query):
        if not self.initialized:
            print("Chatbot not initialized. Initializing...")
            self.initialize()
        docs = self.docsearch.similarity_search(query)
        return self.chain({"input_documents": docs, "question": query}, return_only_outputs=True)
         