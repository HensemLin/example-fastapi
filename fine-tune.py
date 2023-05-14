import openai
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")

openai.api_key = API_KEY
# os.environ['OPENAI_API_KEY'] = API_KEY
# print(API_KEY)
# file_id = file-GscON40CdgwKHAdV9GIQIAF5
# file_id = file-1VL7AdWA2d5MJJICBbx4M9OG
# fine_tune_id = ft-BXwRjtX7TTlPCrToIgXdxkqq
# fine-tune-id = ft-rpDFdkNVyJurM6R51F7OftKg

"""---------------------------- prepare data --------------------------"""
# export OPENAI_API_KEY="<OPENAI_API_KEY>"
# export OPENAI_API_KEY="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"
# openai tools fine_tunes.prepare_data -f <LOCAL_FILE>
# openai tools fine_tunes.prepare_data -f /Users/anshin-lin/Desktop/VS_Code/Axie-Infinity/data/prepared_data.jsonl
# openai tools fine_tunes.prepare_data -f /Users/anshin-lin/Desktop/VS_Code/Axie-Infinity/data/prompt.jsonl

"""---------------------------- upload file to OpenAI acc --------------------------"""
# file_name = "/Users/anshin-lin/Desktop/VS_Code/Axie-Infinity/data/prepared_data.jsonl"
# upload_response = openai.File.create(
#   file=open(file_name, "rb"),
#   purpose='fine-tune'
#   )
# print(upload_response)

"""---------------------------- fine tune model --------------------------"""
# openai api fine_tunes.create -t <TRAIN_FILE_ID_OR_PATH> -m <BASE_MODEL>
# openai api fine_tunes.create -t /Users/anshin-lin/Desktop/VS_Code/Axie-Infinity/data/prepared_data_prepared.jsonl -m davinci
# openai api fine_tunes.create -t /Users/anshin-lin/Desktop/VS_Code/Axie-Infinity/data/prompt_prepared.jsonl -m davinci

# file_id = upload_response.id
# file_id = 'file-GscON40CdgwKHAdV9GIQIAF5'
# training_file_path = "/Users/anshin-lin/Desktop/VS_Code/OpenAI-API/data_prepared.jsonl"
# fine_tune_response = openai.FineTune.create(
#     training_file=file_id,
#     model='davinci'
#     )
# print(fine_tune_response)

"""---------------------------- check fine tune progress --------------------------"""
# If the event stream is interrupted for any reason, you can resume it by running:
# openai api fine_tunes.follow -i <YOUR_FINE_TUNE_JOB_ID>
# openai api fine_tunes.follow -i ft-rpDFdkNVyJurM6R51F7OftKg

# List all created fine-tunes
# openai api fine_tunes.list

# id = 'ft-BXwRjtX7TTlPCrToIgXdxkqq'
# id = fine_tune_response.id
# fine_tune_events = openai.FineTune.list(
#     id=id
#     )
# print(fine_tune_events)

# Retrieve the state of a fine-tune. The resulting object includes
# job status (which can be one of pending, running, succeeded, or failed)
# and other information
# openai api fine_tunes.get -i <YOUR_FINE_TUNE_JOB_ID>
# openai api fine_tunes.get -i 'ft-BXwRjtX7TTlPCrToIgXdxkqq'

# id = 'ft-BXwRjtX7TTlPCrToIgXdxkqq'
# id = fine_tune_response.id
# retrieve_response = openai.FineTune.retrieve(
#     id=id
#     )
# print(retrieve_response)

# Cancel a job
# openai api fine_tunes.cancel -i <YOUR_FINE_TUNE_JOB_ID>
# openai api fine_tunes.cancel -i 'ft-BXwRjtX7TTlPCrToIgXdxkqq'

# openai.FineTune.cancel(id=fine_tune_response.id)

"""---------------------------- run the fine tune model --------------------------"""
#FINE_TUNED_MODEL = "davinci:ft-personal-2023-04-17-14-52-17"
# FINE_TUNED_MODEL = "davinci:ft-personal-2023-04-17-15-26-35"
FINE_TUNED_MODEL = "davinci:ft-personal-2023-04-19-05-44-39"
# result_file = "file-SP7TmhamfCSmolRbG4aoXb1x"
prompt = "tell me about Ecosystem Fund of Axie Infinity\n\n###\n\n"

response = openai.Completion.create(
    model=FINE_TUNED_MODEL,
    prompt=prompt,
    max_tokens = 50,
    stop=["END"]
    )

print(response['choices'][0]['text'])





