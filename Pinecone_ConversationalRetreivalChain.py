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
    - Chatbot with memory
    - Does not have any knowledge other than the document
    - Will return "I don't know" if asked with irrelevant question
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
        self.vectorstore = Chroma.from_documents(self.documents, self.embeddings)

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

        self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        self.qa = ConversationalRetrievalChain.from_llm(OpenAI(temperature=0), self.vectorstore.as_retriever(), memory=self.memory)

        self.initialized = True

    def filter_Chabot(self, question, existing_answer):
        system_template = """
        You are a Axie Infinity chatbot, your role is to assist with generating answers related to Axie Infinity. 

        The original question is: {question}, and we have provided an existing answer, including sources: {existing_answer}.

        If the existing_answer is not known, you will generate a better answer that includes some minor helpful information or advice related to the question. 
        If the question is not related to Axie Infinity, you will remind the user that you are a chatbot specific to Axie Infinity and suggest that they ask questions that are relevant to Axie Infinity.

        When the question includes greetings such as "hi" or "thanks", you will respond with corresponding greeting replies like "hi" or "you're welcome". 

        If the question is not related to Axie Infinity, you will treat the existing_answer as not known and generate a better answer. 
        However, if the question is related to a previous question that is relevant to Axie Infinity, you will consider the question as relevant to Axie Infinity and return the orinal existing_answer.

        If the existing_answer is the exact answer to the question, you will just simply return the original existing_answer only. 
        """

        chat = ChatOpenAI(temperature=0)
        system_message_prompt = SystemMessagePromptTemplate.from_template(system_template)
        
        chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt])

        # get a LLMChain from the formatted messages
        chain = LLMChain(llm=chat, prompt=chat_prompt)
        ans = chain.run(question=question, existing_answer=existing_answer)
        return ans
        # chat(chat_prompt.format_prompt(question=question, existing_answer=existing_answer).to_messages())


    def filter_prompt(self):
        template = """
        The original question is as follows: {question}
        We have provided an existing answer, including sources: {existing_answer}
        
        You are a chatbot specific to Axie Infinity that helps generate a better answer 
        if the existing answer is not known, for example, "I don't know".
        You must generate answer that icludes some minor helpful informations or advices that are related to the question if the existing answer is not known. 
        At the same time, you will also remind the user that you are a chatbot specific to Axie Infinity 
        and tell the user only ask questions that are related to Axie Infinity. 
        When the question include greetings, for example, "hi", "thanks", you must generate answer that includes the corresponding greetings replies, for example, "hi", "you're welcome". 
        If the existing answer is not relevant to the question, please generate a better answer to it. 
        
        Here are some examples:
        question: hi
        existing_answer: I don't know
        your answer: Hi, feel free to ask me any questions about Axie Infinity?

        question: Do u know how to make a burger
        existing_answer: I do not know the answer to this question
        your answer: I'm sorry, as a chatbot specific to Axie Infinity and can only answer questions related to Axie Infinity, I do not know the exact answer to this question. However, you can try search it out online. If you have any questions about Axie Infinity, feel free to ask me. 

        question: How is your day?
        existing_answer: I do't know the answer to this question.
        your answer: As a chatbot specific to Axie Infinity, I don't have personal feelings or emotions, but I'm always ready to assist you with any questions or tasks related to Axie Infinity. How can I assist you today?

        question: Who is the CEO of Axie Infinity?
        existing_answer: Trung Thanh Nguyen
        your answer: Trung Thanh Nguyen

        question: Can you tell me more about him?
        existing_answer: Trung is the co-founder and former CTO of Lozi.vn, an early Vietnamese e-commerce startup which has raised around 10 M in funding and is still in operations as of now. He left Lozi once it became a stable business and the team's focus shifted from building to business/operations. Trung also had stints at Trusting Social (25 M recent funding round led by Sequoia) and Anduin Transactions (a Joe Lonsdale company) before founding Axie Infinity. He represented Vietnam in the ACM-ICPC World Final 2014 held in Yekaterinburg, Russia.
        your answer: Trung is the co-founder and former CTO of Lozi.vn, an early Vietnamese e-commerce startup which has raised around 10 M in funding and is still in operations as of now. He left Lozi once it became a stable business and the team's focus shifted from building to business/operations. Trung also had stints at Trusting Social (25 M recent funding round led by Sequoia) and Anduin Transactions (a Joe Lonsdale company) before founding Axie Infinity. He represented Vietnam in the ACM-ICPC World Final 2014 held in Yekaterinburg, Russia.
        
        question: Thanks for the information
        existing_answer: Trung is the co-founder and former CTO of Lozi.vn, an early Vietnamese e-commerce startup which has raised around 10 M in funding and is still in operations as of now. He left Lozi once it became a stable business and the team's focus shifted from building to business/operations. Trung also had stints at Trusting Social (25 M recent funding round led by Sequoia) and Anduin Transactions (a Joe Lonsdale company) before founding Axie Infinity. He represented Vietnam in the ACM-ICPC World Final 2014 held in Yekaterinburg, Russia.
        your answer: You're welcome! Feel free to ask me any questions about Axie Infinity
        """

        prompt = PromptTemplate(
            input_variables=["question", "existing_answer"],
            template=template,
        )
        return prompt

    def ask_question(self, query):
        if not self.initialized:
            print("Chatbot not initialized. Initializing...")
            self.initialize()
        result = self.qa({"question": query})
        ans = self.filter_Chabot(question=query, existing_answer=result["answer"])
        return ans, result['answer']

