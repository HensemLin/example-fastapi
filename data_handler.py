from WebScrape import WebScrap
import os
import json
import csv
from dotenv import load_dotenv
import openai

class DataHandler:
    # Class variable for storing jsonl data in a list
    prompt_completion_data = []

    def __init__(self, folder_name):
        """
        Constructor for the WebScrap class.

        Args:
            folder_name (str): The name of the folder where scraped data will be stored.
        """
        # Set the folder name
        self.folder_name = folder_name
        
        # Call the WebScrap and web_scrap method to scrape data from the web and convert it to json
        p = WebScrap(folder_name=folder_name)
        p.web_scrap()
    
    def generate_prompt_completion(self, data):
        """Converts the input data into a JSONL formatted string.

        Args:
            data (List[Dict[str, Any]]): A list of dictionaries representing the data to be converted.

        Returns:
            self.prompt_completion_data: A list of string representation of the JSONL formatted data.
        """
        
        prompt = False
        prompt_completion_data = []
        
        # Extract the title and topic of the document
        title = data["title"]
        topic = data["topic"]

        # Check if data contain main-info or main-links
        # main-info is a list of lists containing information about the document
        # main-links is a list of lists containing links to external resources
        main_info_bool = bool([elem for sublist in data["info"] for elem in sublist])
        main_links_bool = bool([elem for sublist in data["links"] for elem in sublist])

        # Generate prompts for table
        for table in data["table"]:
            for table_datas in table["table_data"]:
                # Replace empty lists with "None" in the table data and table header
                table_datas = [elem if elem != [] else "None" for elem in table_datas]
                table_header = [elem if elem != [] else "Details" for elem in table['table_header']]
                # Create the prompt dictionary with the topic, title, and table information
                if title:
                    prompt = {"prompt": f"Topic: {topic}\nTitle: {title}\n"}
                else:
                    prompt = {"prompt": f"Topic: {topic}\n"}

                if table['table_topic']:
                    prompt_dict = f"Table: {table['table_topic']}\n" + "\n".join([f"{header}: {data}" for header, data in zip(table_header, table_datas)])
                else:
                    prompt_dict = f"Table: Overview\n" + "\n".join([f"{header}: {data}" for header, data in zip(table_header, table_datas)])
                
                prompt["prompt"]+= prompt_dict
                
                # Create the completion dictionary with table information
                completion_dict = {"completion" : f"It has a " + ", ".join([f"{header} of {data}" for header, data in zip(table_header, table_datas)])}
                prompt.update(completion_dict)
                
                # Convert dictionary to JSON string
                obj_str = json.dumps(prompt, ensure_ascii=False)
                # Remove unnecessary characters from JSON string
                obj_str = obj_str.replace('\u200b', '').replace('   ', ' ').replace('  ', ' ')
                obj = json.loads(obj_str)
                
                # Add the prompt to the jsonl_data list
                prompt_completion_data.append(obj)
        
        # Generate prompt for topics and title
        # If the document has main-info or main-links, create a prompt for it
        if main_info_bool or main_links_bool:
            if not title:  
                if main_info_bool and main_links_bool and topic:
                    prompt = {"prompt": f"Topic: {topic}", "completion": {"info": data["info"], "links": data["links"]}}
                elif main_links_bool and not main_info_bool and title:
                    prompt = {"prompt": f"Topic: {topic}", "completion": {"links": data["links"]}}
                elif main_info_bool and not main_links_bool and title:
                    prompt = {"prompt": f"Topic: {topic}", "completion": {"info": data["info"]}}
            elif title:
                if main_info_bool and main_links_bool:
                    prompt = {"prompt": f"Topic: {topic}\nTitle: {title}", "completion": {"info": data["info"], "links": data["links"]}}
                elif main_links_bool and not main_info_bool:
                    prompt = {"prompt": f"Topic: {topic}\nTitle: {title}", "completion": {"links": data["links"]}}
                elif main_info_bool and not main_links_bool:
                    prompt = {"prompt": f"Topic: {topic}\nTitle: {title}", "completion": {"info": data["info"]}}
            if prompt:
                obj_str = json.dumps(prompt, ensure_ascii=False)
                obj_str = obj_str.replace('\u200b', '').replace('   ', ' ').replace('  ', ' ')
                obj = json.loads(obj_str)
                prompt_completion_data.append(obj)
        
        prompt = False
        # Generate prompts for contents
        for content in data["contents"]:
            # Extract the sub_title of the document
            sub_title = content["sub_title"]
            
            # Check if data contain sub-info or sub-links
            # sub_info_bool is a list of lists containing information about the document
            # sub_links_bool is a list of lists containing links to external resources
            sub_info_bool = bool([elem for sublist in content["sub_info"] for elem in sublist])
            sub_links_bool = bool([elem for sublist in content["sub_links"] for elem in sublist])

            # Generate prompts for table
            for table in content["sub_table"]:
                for table_datas in table["sub_table_data"]:
                    # Replace empty lists with "None" in the table header
                    table_header = [elem if elem != [] else "Details" for elem in table['sub_table_header']]
                    if title:
                        prompt = {"prompt": f"Topic: {topic}\nTitle: {title}\nSub-Title: {sub_title}\n"}
                    else:
                        prompt = {"prompt": f"Topic: {topic}\nSub-Title: {sub_title}\n"}
                    
                    if table['sub_table_topic']:
                        prompt_dict = f"Table: {table['sub_table_topic']}\n" + "\n".join([f"{header}: {data}" for header, data in zip(table_header, table_datas)])
                    else:
                        prompt_dict = f"Table: Overview\n" + "\n".join([f"{header}: {data}" for header, data in zip(table_header, table_datas)])
                
                prompt["prompt"]+= prompt_dict
                completion_dict = {"completion" : f"It has a " + ", ".join([f"{header} of {data}" for header, data in zip(table_header, table_datas)])}
                prompt.update(completion_dict)
                obj_str = json.dumps(prompt, ensure_ascii=False)
                obj_str = obj_str.replace('\u200b', '').replace('   ', ' ').replace('  ', ' ')
                obj = json.loads(obj_str)
                prompt_completion_data.append(obj)

            # Generate prompts for topic, title, and sub-title
            if sub_info_bool or sub_links_bool:
                if title:
                    if sub_info_bool and sub_links_bool:
                        prompt = {"prompt": f"Topic: {topic}\nTitle: {title}\nSub-Title: {sub_title}", "completion": {"info": content["sub_info"], "links": content["sub_links"]}}
                    elif sub_info_bool and not sub_links_bool:
                        prompt = {"prompt": f"Topic: {topic}\nTitle: {title}\nSub-Title: {sub_title}", "completion": {"info": content["sub_info"]}}
                    elif not sub_info_bool and sub_links_bool:
                        prompt = {"prompt": f"Topic: {topic}\nTitle: {title}\nSub-Title: {sub_title}", "completion": {"links": content["sub_links"]}}
                else:
                    if sub_info_bool and sub_links_bool:
                        prompt = {"prompt": f"Topic: {topic}\nSub-Title: {sub_title}", "completion": {"info": content["sub_info"], "links": content["sub_links"]}}
                    elif sub_info_bool and not sub_links_bool:
                        prompt = {"prompt": f"Topic: {topic}\nSub-Title: {sub_title}", "completion": {"info": content["sub_info"]}}
                    elif not sub_info_bool and sub_links_bool:
                        prompt = {"prompt": f"Topic: {topic}\nSub-Title: {sub_title}", "completion": {"links": content["sub_links"]}}
                if prompt:    
                    obj_str = json.dumps(prompt, ensure_ascii=False)
                    obj_str = obj_str.replace('\u200b', '').replace('   ', ' ').replace('  ', ' ')
                    obj = json.loads(obj_str)
                    prompt_completion_data.append(obj)
        return prompt_completion_data

    def restructure_prompt_completion(self, data):
        """
        This function restructures the JSONL data to a more readable and user-friendly format by extracting the prompt and completion data and combining it based on certain conditions.

        Inputs:
            data: A dictionary containing the prompt and completion data for a single prompt-completion pair.

        Output:
            A dictionary containing the restructured prompt and completion data for the given prompt-completion pair.
        """

        # Extract prompt and completion data from the input dictionary
        prompt_text = data["prompt"]
        completion_data = data["completion"]
        
        # Condition 1: If "info" is present in completion_data and "links" is not present
        if "info" in completion_data and "links" not in completion_data:
            prompts = (prompt_text)
            completions = (completion_data["info"])
        
        # Condition 2: If "links" is present in completion_data and "info" is not present
        elif "links" in completion_data and "info" not in completion_data:
            prompts = (prompt_text)
            links = completion_data["links"]
            completions = (f"Here are some links related to the topic: {', '.join(links)}")

        # Condition 3: If both "info" and "links" are present in completion_data
        elif "info" in completion_data and "links" in completion_data:
            prompts = (prompt_text)
            info = completion_data["info"]
            links = completion_data["links"]
            completions = (f"{info}\nHere are some links related to the topic: {', '.join(links)}")
        
        # Condition 4: If prompt or completion is empty
        elif not prompt_text or not completion_data:
            return

        # Condition 5: If none of the above conditions are met
        else:
            prompts = (prompt_text)
            completions = (completion_data)

        # Return the restructured prompt and completion data in the form of a dictionary
        return {"prompt": prompts, "completion": completions} 
    
    def generate_prompt_completion_davinci(self, data):
        """
        This function generates diverse and specific questions along with their detailed answers using OpenAI's GPT-3 API.

        Args:
            data (list): a list of dictionaries, each dictionary containing the prompt and completion text for which the questions
                        are to be generated

        Returns:
            A list of dictionaries containing the generated questions and their answers in json format.
        """

        # Initialize an empty list to store the generated questions and their answers
        davinci_data = []

        # Load the API key from the .env file and set it as the global API key for the OpenAI module
        load_dotenv()
        OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        openai.api_key = OPENAI_API_KEY

        for records in data:

            # Construct the prompt for generating questions
            record = records['prompt']+"\n"+"Content: "+records['completion']

            # if "Sub-Title: Axie Infinity Universe" in records["prompt"]:
            #     record = records['prompt']+"\n"+"Content: "+records['completion']
            #     break
            
            # Set the number of questions to be generated based on the presence of 'Table' in the prompt
            if "Table" in records['prompt']:
                Qnum = 20
            else:
                Qnum = 30

            # Construct the prompt for generating questions
            prompt = f"""As a prompt engineer, you must generate at least {Qnum} diverse, detailed and specific questions with their answers in detail only based on the "Content" in following information below. Also, if the information consist of "Table", please ensure that each question include at least 2 subjects, and first generate questions according to the format of: "What is the {{subject}} when {{subject}} is {{value}}?" or "What is the {{subject}} when {{subject}} and {{subject}} is {{value}} and {{value}}?". Please make it in the jsonl format of: {{'prompt': 'questions', 'completion': 'answer'}}\n\n"""
            
            # Print the prompt and the record
            print(prompt+record)        
            
            # Call the GPT-3 API to generate prompt and completion
            response = openai.Completion.create(
                model="text-davinci-003",
                prompt=prompt+record,
                max_tokens=2000,
                stop=None,
                temperature=0.7
            )

            # Print the generated questions
            print("Generated Questions:")
            for choice in response.choices:
                    data = choice.text.strip()
                    print(data)
            
            # Parse the generated questions and answers from the GPT-3 API response and store them in a list
            start_word = "{"
            end_word = "}"
            start_indices = []
            end_indices = []
            start_index = data.find(start_word)
            end_index = data.find(end_word)
            while start_index != -1 and end_index != -1:
                start_indices.append(start_index)
                end_indices.append(end_index)
                start_index = data.find(start_word, start_index + 1)
                end_index = data.find(end_word, end_index + 1)

            end_idx = data.find(end_word)
            result_dict = {}
            Q_counter = 0

            for start_idx, end_idx in zip(start_indices, end_indices):
                if start_indices != -1 and end_idx != -1:
                    result = data[start_idx:end_idx+len(end_word)].replace("{'", '{"').replace("'}", '"}').replace("': '", '": "').replace("', '", '", "')
                result_dict = json.loads(result)
                davinci_data.append(result_dict)
                Q_counter += 1
            
            print(f"Generated {Q_counter} questions from davinci")
            return davinci_data

    def generate_final_prompt_completion(self):
        """
        This function generates a list of dictionaries, each representing a prompt and its corresponding completion. 

        Input:
            None.

        Output:
            A list of dictionaries, each containing the prompt and completion for a given example.
        """

        # Set the name of the input file to be converted to JSONL
        input_file = "data.json"
        
        # Initialize the lists and dictionaries for storing the data
        prompt_completion_data = []
        restructure_prompt_completion_data = []
        davinci_data = []

        # Open the input file and load the data into a dictionary
        with open(os.path.join(self.folder_name, input_file), "r") as f:
            json_data = json.load(f)

        # Generate prompt and completion from each item in the JSON data
        for item in json_data:
            print(item)
            prompt_completion_data+=(self.generate_prompt_completion(item))

        # Restructure all the prompt and completion
        for item in prompt_completion_data:
            restructure_prompt_completion_data.append(self.restructure_prompt_completion(item))

        # generate more prompt and copmletion using davinci
        # davinci_data += self.generate_prompt_completion_davinci(restructure_prompt_completion_data)

        return restructure_prompt_completion_data+davinci_data

    def json_to_jsonl(self, output_file):
        """
        This function converts a JSON data to a JSONL file.

        Args:
            output_file (str): The name of the output JSONL file.

        Returns:
            None, but a JSONL file will be created at the location specified by output_file.
        """

        obj_counter = 0
        data = self.generate_final_prompt_completion()
        file_path = os.path.join(self.folder_name, output_file) 

        # Open the output file and write the prompt and completion in JSONL format
        with open(file_path, "w") as f:
            for obj in data:
                f.write(json.dumps(obj)+"\n")
                obj_counter += 1
        
        print(f"Generated {obj_counter} objects in {output_file}.")


    def json_to_CSV(self, output_file):
        """
        This function converts a JSON file to a CSV file.

        Args:
            output_file (str): The name of the output CSV file.

        Returns:
            None, but a CSV file will be created at the location specified by output_file.
        """

        row_counter = 0
        data = self.generate_final_prompt_completion()
        file_path = os.path.join(self.folder_name, output_file) 

        # Open the output file and write the prompt and completion in CSV format
        with open(file_path, "w", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(data[0].keys())
            for obj in data:
                row = []
                for key in obj:
                    row.append(obj[key])
                writer.writerow(row)
                row_counter += 1
        
        print(f"CSV file {output_file} has been generated with {row_counter} rows of data.")
            

    def data_handler(self):
        """
        converts the JSON files to a single JSONL file, and generates a proper JSONL file for fine-tuning.

        Args:
            self: An instance of the class.

        Returns:
            None.
        """
        # Set file names
        jsonl_file = "data.jsonl"
        csv_file = "data.csv"
        
        # Convert JSON files to JSONL file
        print(f"\n\nconverting json to jsonl file and saved in {jsonl_file}")
        self.json_to_jsonl(jsonl_file)

        # Convert JSON files to CSV file
        print(f"\n\nconverting json to CSV file and saved in {csv_file}")
        self.json_to_CSV(csv_file)
        
        #Finish
        print("Done !!!")





if __name__ == "__main__":
    folder_name = "./Axie-Infinity/data"
    p = DataHandler(folder_name=folder_name)
    # p.data_handler()
    p.generate_final_prompt_completion()