import openai
import os

openai.api_key = "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"
# get API key from top-right dropdown on OpenAI website

print(openai.Engine.list())  # check we have authenticated

MODEL = "text-embedding-ada-002"

res = openai.Embedding.create(
    input=[
        "Sample document text goes here",
        "there will be several phrases in each batch"
    ], engine=MODEL
)

print(res)

embeds = [record['embedding'] for record in res['data']]

import pinecone

index_name = 'semantic-search-openai'

# initialize connection to pinecone (get API key at app.pinecone.io)
pinecone.init(
    api_key="bd20fae8-7de5-4ef0-858c-6a376362cace",
    environment="us-west1-gcp-free"  # find next to api key in console
)
# check if 'openai' index already exists (only create index if not)
if index_name not in pinecone.list_indexes():
    pinecone.create_index(index_name, dimension=1536)
# connect to index
index = pinecone.Index(index_name)