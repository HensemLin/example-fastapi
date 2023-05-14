from langchain.llms import OpenAI
from langchain.agents import initialize_agent
from langchain.agents.agent_toolkits import ZapierToolkit
from langchain.agents import AgentType
from langchain.utilities.zapier import ZapierNLAWrapper
import os
from dotenv import load_dotenv

load_dotenv()

# get from https://platform.openai.com/
os.environ["OPENAI_API_KEY"] = os.environ.get("OPENAI_API_KEY", "")

# get from https://nla.zapier.com/demo/provider/debug (under User Information, after logging in): 
os.environ["ZAPIER_NLA_API_KEY"] = os.environ.get("ZAPIER_NLA_API_KEY", "")

llm = OpenAI(temperature=0)
zapier = ZapierNLAWrapper()
toolkit = ZapierToolkit.from_zapier_nla_wrapper(zapier)
agent = initialize_agent(toolkit.get_tools(), llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True)

prompt = "Send an message to Jshyne from slack account of jiayuan.lin@anhsin.io via slack that is a pitch for why you should visit https://starmorph.com to help you small business integrate GPT-3 services today. Provide a hyperlink to the website and make the message likely to convert to website visitors."
agent.run(prompt)