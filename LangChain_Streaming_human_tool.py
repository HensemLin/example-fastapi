from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import CharacterTextSplitter, RecursiveCharacterTextSplitter
from langchain.llms import OpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.document_loaders.csv_loader import CSVLoader
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain import PromptTemplate, LLMChain
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.agents import load_tools, initialize_agent
from langchain.agents import AgentType
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    AIMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage
)
import openai
import os
from dotenv import load_dotenv
import pinecone

class Chatbot():
    """
    A chatbot with memory that is capable of answering questions based on a set of provided documents.

    Attributes:
        OPENAI_API_KEY (str): The OpenAI API key.
        PINECONE_API_KEY (str): The Pinecone API key.
        PINECONE_ENVIRONMENT (str): The Pinecone environment.
        index_name (str): The name of the search index.
        data_file_path (str): The path to the data file.
        documents (list): A list of documents.
        text_splitter (CharacterTextSplitter): A text splitter instance.
        embeddings (OpenAIEmbeddings): An embeddings instance.
        vectorstore (Chroma): A vector store instance.
        index (Index): An index instance.
        memory (ConversationBufferMemory): A memory instance.
        qa (ConversationalRetrievalChain): A conversational retrieval chain instance.
        initialized (bool): Whether or not the chatbot has been initialized.
    """

    def __init__(self, data_file_path, openai_api_key="", pinecone_api_Key="", pinecone_environment=""):
        """
        Initializes a new instance of the Chatbot class.

        Args:
            data_file_path (str): The path to the data file.
            openai_api_key (str, optional): The OpenAI API key. Defaults to "".
            pinecone_api_key (str, optional): The Pinecone API key. Defaults to "".
            pinecone_environment (str, optional): The Pinecone environment. Defaults to "".
        """
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
        """
        Initializes the chatbot by loading documents, splitting them into chunks, and creating embeddings and an index.
        """
        print("Initializing Chatbot...")

        # Set the OpenAI API key.
        openai.api_key = self.OPENAI_API_KEY
        
        # Load the documents.
        self.loader = CSVLoader(file_path=self.data_file_path, csv_args={'delimiter':","})
        self.documents = self.loader.load()
        print(f"You have {len(self.documents)} document(s) in your data")

        # Split the documents into chunks.
        self.text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
        self.documents = self.text_splitter.split_documents(self.documents)
        print(f"Now you have {len(self.documents)} document(s)")

        # Create embeddings and a vector store.
        self.embeddings = OpenAIEmbeddings(openai_api_key=self.OPENAI_API_KEY)
        self.vectorstore = Chroma.from_documents(self.documents, self.embeddings)
        
        self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        self.qa = ConversationalRetrievalChain.from_llm(
            OpenAI(temperature=0), 
            retriever=self.vectorstore.as_retriever(), 
            memory=self.memory)

        self.initialized = True

    def filter_Chabot(self, question, existing_answer):
        """
        A function that filters the chatbot's response based on the existing answer and the question.

        Args:
        - question (str): The question that the user asked.
        - existing_answer (str): The answer that the chatbot generated for the previous question.

        Returns:
        - ans (str): The answer that the chatbot will give to the current question.
        """

        # Define a system template message that explains the chatbot's role and how it will handle different types of questions
        system_template = """
        You are a Axie Infinity chatbot, your role is to assist with answering questions. 

        The original_question is: {question}, and we have provided an existing_answer: {existing_answer}.
        
        You will treat the existing_answer as related to Axie Infinity. 

        If the existing_answer is not known such as "I don't know", you will respond with a message that acknowledges the original_question but explains that you are unable to answer it".
        If the existing_answer if not known such as "I don't know", you remind the user that you are a chatbot specific to Axie Infinity and suggest that they ask questions that are relevant to Axie Infinity. 
        
        When the original_question consists of greetings such as "hi" or "thanks", you will respond with corresponding greeting replies like "hi" or "you're welcome".

        If the existing_answer is known, you will provide a more detailed response and must based solely on the information provided in the existing answer but cannot mention the answer is from existing_answer in the answer. 

        You cannot state that the answer is based from the existing_answer in the answer. 
        
        You will only return the answer.

        You must never return where and how you get the answer.

        You must treat the answer as your own generated answer and avoid acknowledging that it was provided or based on or referred to any other sources. 
        
        You should make it clear that the answer was generated by you as a Axie Infinity chatbot. 
        
        You must treat the answer as your own generated answer and cannot acknowledge that the answer was provided by the existing_answer or any other sources in the answer.
        """

        # Create a ChatOpenAI instance with temperature=0
        chat = ChatOpenAI(streaming=True, callbacks=[StreamingStdOutCallbackHandler()], temperature=0)
        
        # Create a SystemMessagePromptTemplate from the system template
        system_message_prompt = SystemMessagePromptTemplate.from_template(system_template)
        
        # Create a ChatPromptTemplate from the system message prompt
        chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt])

        # Create an LLMChain from the ChatOpenAI instance and the ChatPromptTemplate
        chain = LLMChain(llm=chat, prompt=chat_prompt)
        
        # Call the LLMChain's run method with the current question and the existing answer, and store the result in ans
        ans = chain.run(question=question, existing_answer=existing_answer)
        
        return ans

    def ask_question(self, query, chat_history):
        """
        A function that uses the initialized chatbot to answer a user's question.

        Args:
        - query (str): The question that the user asked.

        Returns:
        - ans (str): The answer that the chatbot generated.
        """

        # If the chatbot has not been initialized yet, initialize it
        if not self.initialized:
            print("Chatbot not initialized. Initializing...")
            self.initialize()
        
        # Use the chatbot's ConversationalRetrievalChain to find a relevant answer to the user's question
        result = self.qa({"question": query, "chat_history": chat_history})
        
        # Filter the chatbot's response using the filter_Chabot function
        ans = self.filter_Chabot(question=query, existing_answer=result["answer"])
        return ans, result["answer"]

