# from LangChain_ConversationalRetreivalChain import Chatbot
# from Pinecone_ConversationalRetreivalChain import Chatbot
from LangChain_Streaming import Chatbot
# from LangChain_Streaming_human_tool import Chatbot
from DataBase import database
import json
# from LangChain_load_qa_chain import Chatbot
# from LangChain_QAwS import Chatbot

db = database('ChatbotDB')
db.create_database()
user_id = 20
table_name = f'User_Chat_History_{user_id}'
db.create_user_Chat_History(table_name=table_name)
chat_history = db.get_data_by_column(column_name='chat_history', table_name=table_name)
chat_history = db.filter_data_for_chatbot(chat_history)
# print("chat_history: ",chat_history)
bot = Chatbot(data_file_path="./Axie-Infinity/data/data.csv", chat_history=chat_history)

print("\n\nHello, I'm your Axie Infinity chatbot. How can I help you today?")

while True:
    query = input("You: ")
    if query == "None":
        print("Goodbye!")
        break
    print("Bot:")
    result, default_ans = bot.ask_question(query=query, chat_history=chat_history if len(chat_history)>0 else [])
    # chat_history = [(query, result)]
    chat_history.append((query, default_ans))
    data = {'user_id': 1, 'chat_history': json.dumps(chat_history[-1])}
    db.insert_data(table_name=table_name, data=data)
    # print(f"\n{chat_history}")
    print("\ndefault ans: ", default_ans)
    # print("Bot: ", result)
    print("\n")