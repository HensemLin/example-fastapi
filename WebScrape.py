from bs4 import BeautifulSoup
import requests
import os
import json
import re
from dotenv import load_dotenv
import logging

class WebScrap:
    # Class variable for storing content urls as a set
    content_urls = set()
    json_dict = []
    jsonl_data = []
    main_url = 'https://whitepaper.axieinfinity.com'

    def __init__(self, folder_name, url=""):
        """
        Constructor for the WebScrap class.

        Args:
            main_url (str): The main URL to start searching for content URLs from.
            folder_name (str): The name of the folder where scraped data will be stored.
            url (str): Optional parameter to specify a specific URL to scrape.
        """
        self.combined_url = self.main_url+url
        self.folder_name = folder_name
    
    def get_html(self):
        """
        Sends a GET request to the class's URL and returns the response as text.

        Returns:
            str: The HTML content of the webpage as text.
            None: If the GET request fails or the response status code is not 200.
        """
        try:
            response = requests.get(self.combined_url)
            if response.status_code == 200:
                # Retrieve HTML content and return it
                html_text = requests.get(self.combined_url).text
                return html_text
            else:
                # Raise an exception if the response status code is not 200
                raise requests.exceptions.RequestException(f"Invalid response status code {response.status_code} for {self.combined_url}")
        
        except requests.exceptions.RequestException as e:
            # Raise an exception if the GET request fails
            raise requests.exceptions.RequestException(f"Error retrieving HTML from {self.combined_url}: {e}")


    def parse_html(self):
        """
        Parses the HTML content of the webpage using BeautifulSoup and returns a soup object.

        Returns:
            bs4.BeautifulSoup: The soup object containing the parsed HTML content of the webpage.
            None: If the HTML content cannot be retrieved or parsed.
        """
        html_text = self.get_html()
        if html_text:
            # Parse HTML content and return soup object
            soup = BeautifulSoup(html_text, 'lxml')
            return soup
        else:
            # Return None if the HTML content cannot be retrieved or parsed
            return None

    def check_url(self):
        """
        Check if the current page exists by searching for a specific div element in its HTML.

        Returns:
            bool: True if the page exists, False otherwise.
        """
        # Check if the page exists by searching for a specific div element in its HTML
        soup = self.parse_html()
        if soup.find('div', class_='css-1rynq56 r-gg6oyi r-ubezar r-1kfrs79 r-135wba7 r-1nf4jbm'):
            print(f"The page {self.combined_url} does not exist")
        else: 
            return True

    def get_TOC_urls(self):
        """
        Recursively searches for all content URLs on the webpage for Table of Content (TOC) and stores them in a set.

        Returns:
            set: A set of all unique content URLs found on the webpage for TOC.
            None: If the HTML content cannot be retrieved or parsed.
        """
        soup = self.parse_html() 
        if soup:
        # Get all links in the table of contents
            toc = soup.find_all('a')
            for content in toc:
                url = content.get('href', '')
                # Skip URLs that do not start with a '/'
                # or have already been visited and stored in content_urls
                if not url.startswith('/') or url in self.content_urls:
                    continue
                # If new URL exists, add it to content_urls and recursively search for more URLs
                if WebScrap(folder_name=self.folder_name, url=url).check_url(): 
                    self.content_urls.add(url)
                    # Recursively search for more URLs
                    if url != "/" : 
                        WebScrap(folder_name=self.folder_name, url=url).get_TOC_urls()
            return self.content_urls
        else:
            return None
    
    def get_links(self, ignore_link=['https://www.gitbook.com/?utm_source=content&utm_medium=trademark&utm_campaign=-LocuLeNcXinpTOZxNu0']):
        """
        Extracts all external links from the webpage (only starting with http).

        Args:
        ignore_link (list): A list of URLs to ignore when searching for links.
    
        Returns:
            list: A list of all external links found on the webpage.
            None: If the HTML content cannot be retrieved or parsed.
        """
        # Parse the HTML content and extract links
        soup = self.parse_html()
        if soup:
            titles, sub_titles, _, _ = self.get_text_info()
            main_links = []
            sub_links = []
            
            # Check any links that come after the title (if any)
            if all(elem for elem in titles):
                for title in titles:
                    value = []
                    for link in soup.find_all('a'):
                        href = link.get('href', '')
                        if href and href.startswith('http') and href not in ignore_link and link.find_previous("h1") and not link.find_previous("h2") and not link.find_previous("h3"): 
                            if link.find_previous("h1").text == title:
                                value.append(href)
                    if not value:
                        value.append(None)
                    main_links.append(value)

            # Check any links that come after the sub_titles (if any)
            if all(elem for elem in sub_titles):
                for sub_title in sub_titles:
                    value = []
                    for link in soup.find_all('a'):
                        href = link.get('href', '')
                        if href and href.startswith('http') and href not in ignore_link and (link.find_previous("h2") or link.find_previous("h3")): 
                            if (link.find_previous("h2").text == sub_title if link.find_previous("h2") else False) or (link.find_previous("h3").text == sub_title if link.find_previous("h3") else False):
                                value.append(href)
                    if not value:
                        value.append(None)
                    sub_links.append(value)
            return main_links, sub_links
        else:
            return None, None

    def get_table_info(self):
        """
        Extracts the data from tables in the HTML content.

        Returns:
            list: A list of dictionaries, where each dictionary represents a table and contains
                the title of the table and its data. Each title and data consist of tokens [CLS] and [SEP].
                Tokens is for fine-tune GPT-3 model.
            None: If the HTML content cannot be retrieved or parsed.
        """
        # Parse the HTML content and extract tables
        soup = self.parse_html()
        if not soup:
            return None
        
        # Check if any table 
        tables = soup.find_all('table')
        if not tables:
            main_tables_data = [{"topic":'null', "title":'null', "data":'null'}]
            sub_tables_data = [{"topic":'null', "title":'null', "data":'null'}]
            return main_tables_data, sub_tables_data
        
        # Get tables topic
        div_tag = soup.find("div", {"contenteditable": "false"})
        if not div_tag:
                tables_topic = [None]*len(tables) 
        else:
            inner_div_tags = div_tag.find_all("div", {"tabindex": "0"})
            if not inner_div_tags:
                tables_topic = [None]*len(tables) 
            else:
                tables_topic = [tag.text for tag in inner_div_tags]

        main_tables_data = []
        sub_tables_data = []
        # Loop through the tables
        for i, table in enumerate(tables):
            title = None
            table_data = []
            # Create a table object for table that come after main title (if any)
            if table.find_previous('h1') and not table.find_previous('h2') and not table.find_previous('h3'):
                for index, row in enumerate(table.find_all('tr')):
                    cells = row.find_all('td')
                    if cells and index == 0:
                        title = [cell.text for cell in cells]
                        title = [re.sub(r'\u200b', '', row) for row in title]
                    if cells and index !=0:
                        table_data.append(cell.text for cell in cells)
                        table_data = [[re.sub(r'\u200b', '', item) for item in row] for row in table_data]
                main_tables_data.append({"topic":tables_topic[i], "title":title, "data":table_data})
            # Create a table object for table that comes after sub title (if any) 
            if table.find_previous('h2') or table.find_previous('h3'):
                for index, row in enumerate(table.find_all('tr')):
                    cells = row.find_all('td')
                    if cells and index == 0:
                        title = [cell.text for cell in cells]
                        title = [re.sub(r'\u200b', '', row) for row in title]
                    if cells and index !=0:
                        table_data.append(cell.text for cell in cells)
                        table_data = [[re.sub(r'\u200b', '', item) for item in row] for row in table_data]
                sub_tables_data.append({"topic":tables_topic[i], "title":title, "data":table_data})
        
        if not main_tables_data:
            main_tables_data = [{"topic":'null', "title":'null', "data":'null'}]
        if not sub_tables_data:
            sub_tables_data = [{"topic":'null', "title":'null', "data":'null'}]
        return main_tables_data, sub_tables_data
                
    def get_text_info(self):
        """
        Extracts the titles, sub-titles and corresponding information from the HTML content.

        Returns:
            tuple: A tuple containing three lists: titles, sub-titles, and their corresponding information.
            None: If the HTML content cannot be retrieved or parsed.
        """
        # Parse the HTML content and extract the relevant text elements
        soup = self.parse_html()
        if soup:
            # Create a list of titles (header 1)
            titles = [tag.text for tag in soup.find_all('h1')]
            if not titles:
                titles=[None]

            # Create a list of sub_titles (header 2)
            sub_titles = [tag.text for tag in soup.find_all(['h2', 'h3'])]
            if not sub_titles:
                sub_titles = [None]

            # Create a list of information sections that comes after a title (if any)
            div_tag = soup.find_all("div", {"data-block-content": True})
            inner_div_tags = [tag.find_all(True, {"data-offset-key": True}) for tag in div_tag]
            main_texts = []
            if all(elem for elem in titles):
                for title in titles:
                    value = []
                    for tags in inner_div_tags:
                        for tag in tags:
                            if tag.find_previous("h1") and tag.find_previous("h1").text == title and not tag.find_previous("h2") and not tag.find_previous("h3"):
                                if not tag.find_parent("h1") and not tag.find_parent("table"):
                                    value.append(tag.text)
                    main_texts.append(value)
            
            main_infos = [[' '.join(text)] for text in main_texts]
            # main_infos = [re.sub(r'[\u200b\u200c✔️]', '', string[0]) for string in main_infos]
            main_infos = [text[0].replace('\n', '') for text in main_infos]
            main_infos = [re.sub(r' {2,}', ' ', string) for string in main_infos]
            if all(not sublist for sublist in main_infos):
                main_infos=[None]

            # Create a list of information sections that comes after sub_titles (if any)
            sub_texts = []
            if all(elem for elem in sub_titles):
                for sub_title in sub_titles:
                    value = []
                    for tags in inner_div_tags:
                        for tag in tags:
                            if (tag.find_previous("h2") and tag.find_previous("h2").text == sub_title) or (tag.find_previous("h3") and tag.find_previous("h3").text == sub_title):
                                if not tag.find_parent("h2") and not tag.find_parent("h3") and not tag.find_parent("table"):
                                    value.append(tag.text)
                    sub_texts.append(value)
            
            sub_infos = [[' '.join(text)] for text in sub_texts]
            # sub_infos = [re.sub(r'[\u200b\u200c✔️]', '', string[0]) for string in sub_infos]
            sub_infos = [text[0].replace('\n', '') for text in sub_infos]
            sub_infos = [re.sub(r' {2,}', ' ', string) for string in sub_infos]
            if all(not sublist for sublist in sub_infos):
                sub_infos=[None]

            # Add tokens in the data
            main_infos = [item if item else None for item in main_infos]
            sub_infos = [item if item else None for item in sub_infos ]
            titles = [item if item else None for item in titles]
            sub_titles = [item if item else None for item in sub_titles]

            return titles, sub_titles, main_infos, sub_infos
        else:
            return None
    
    def filter_NULL(self, data):
        """
        Filters null values from the given data.

        Args:
            data: The data to filter null values from.

        Returns:
            If data is null or empty, returns an empty list.
            If data is a list, returns a new list with null values filtered out recursively.
            If data is not null or a list, returns data itself.
        """
        if not data or data == 'null':
            return []
        elif isinstance(data, list):
            return [self.filter_NULL(d) for d in data]
        else:
            return data

    def create_json_dict(self):
        """
        This function creates a JSON dict containing the information from the web page.
        It returns a dictionary with the information arranged in a structured way.

        Returns:
            my_dict (dict): A dictionary containing the web page information in a structured format.
        """
        titles, sub_titles, main_infos, sub_infos = map(lambda x: self.filter_NULL(x), self.get_text_info())
        main_links, sub_links = map(lambda x: self.filter_NULL(x), self.get_links())
        main_tables_data, sub_tables_data = self.get_table_info()

        # Loop through the titles and sub-titles to structure the information in the dictionary
        for i in range(len(titles)):
            topic_dict = {"topic": "Axie Infinity",
                          "title": titles[i],
                          "info": main_infos[i],
                          "links": [],
                          "table": [],
                          "contents": []
                          }
            # Add main links to the topic dictionary if there are any
            if main_links:
                for z in range(len(main_links[i])):
                    topic_dict["links"].append(main_links[i][z])
            else:
                topic_dict["links"] = []

            # Add table information to the topic dictionary if there is any
            if any(d.get('topic') != 'null' or d.get('title') != 'null' or d.get('data') != 'null' for d in main_tables_data):
                for q in range(len(main_tables_data)):
                    main_table_dict = {"table_topic": self.filter_NULL(main_tables_data[q]["topic"]),
                                "table_header": self.filter_NULL(main_tables_data[q]["title"]),
                                "table_data": self.filter_NULL(main_tables_data[q]["data"])
                                }
                    topic_dict["table"].append(main_table_dict)
            else:
                topic_dict["table"] = []

            for j in range(len(sub_titles)):
                contents_dict = {"sub_title": sub_titles[j],
                                "sub_info": sub_infos[j],
                                "sub_links": [],
                                "sub_table": []
                                }
                 # Add links to the subtitle dictionary if there are any
                if sub_links:
                    for x in range(len(sub_links[j])):
                        contents_dict["sub_links"].append(sub_links[j][x])
                else:
                    contents_dict["sub_links"] = []
                # Add table information to the subtitle dictionary if there is any
                if any(d.get('topic') != 'null' or d.get('title') != 'null' or d.get('data') != 'null' for d in sub_tables_data):
                    for y in range(len(sub_tables_data)):
                        sub_table_dict = {"sub_table_topic": self.filter_NULL(sub_tables_data[y]["topic"]),
                                    "sub_table_header": self.filter_NULL(sub_tables_data[y]["title"]),
                                    "sub_table_data": self.filter_NULL(sub_tables_data[y]["data"])
                                    }
                        contents_dict["sub_table"].append(sub_table_dict)
                else:
                    contents_dict["sub_table"] = []
                # Append the subtitle dictionary to the topic dictionary
                topic_dict["contents"].append(contents_dict)
        return topic_dict
    
    def gen_data_text_file(self):
        """
        Generate a text file containing the titles and information of each section of the page.
        The file is saved in a newly created 'data' folder, with each section on a separate line.

        Returns:
            None, but a txt and JSON file will be created at the location specified by folder name.
        """
        # Only crete file if there is information to write
        if self.get_text_info():
            
            # Create the JSON dictionary
            json_dict = self.create_json_dict()

            # Create rhe JSON dictionary
            self.json_dict.append(json_dict)

            # Create the folder if it doesn't exist
            if not os.path.exists(self.folder_name):
                os.makedirs(self.folder_name)

            ## Uncomment the below parts if u want to name the txt file with incremental numbers
            # Find the latest numbered .txt file in the folder
            # existing_files = [f for f in os.listdir(self.folder_name) if f.endswith('.txt')]
            # if existing_files:
            #     latest_file = max(existing_files, key=lambda x: int(os.path.splitext(x)[0]))
            #     file_number = int(os.path.splitext(latest_file)[0])
            # else:
            #     file_number = 0
            
            # filename = file_number+1
            filename = "introduction" if "/".join(self.combined_url.split("/")[3:])=="" else "/".join(self.combined_url.split("/")[3:])
            filename = filename.replace("/", "\\")

            # Write the information to the new text file
            with open(os.path.join(self.folder_name, f"{filename}.txt"), 'w', encoding="utf-8") as f:
                json.dump(json_dict, f, indent=4, ensure_ascii=False)
            
            # Write the information to the json file
            with open(os.path.join(self.folder_name, "data.json"), 'w', encoding="utf-8") as f:
                json.dump(self.json_dict, f, indent=4, ensure_ascii=False)

            # Check if the file was successfully created
            if os.path.exists(os.path.join(self.folder_name, f"{filename}.txt")) and os.path.exists(os.path.join(self.folder_name, "data.json")):
                print(f"File {filename}.txt has been created.")
                print(f"File data.json has been created.")
                print("Data has been written to file")
            else:
                logging.warning("File not created")
                return None    
        else:
            logging.warning("File not created")
            return None
    
    def web_scrap(self):
        """
        Scrapes the table of contents URLs from a website, generates JSON data files for each URL

        Args:
            self: An instance of the class.

        Returns:
            None.
        """
        
        # Retrieve URLs from the website
        print("Retrieving links (URLs) from the website...")
        urls = self.get_TOC_urls()
        print(f"There are {len(urls)} contents in the Table of Contents")
        print("The links for the respective Table of Contents are:")
        for url in urls:
            print(f"{self.main_url+url}")

        # Generate JSON data files for each URL
        for index, url in enumerate(urls):
            print(f"\n\nGenerating data in json and txt format: ({index+1}/{len(urls)})")
            WebScrap(folder_name=self.folder_name, url=url).gen_data_text_file()
        print("Done !!!")





if __name__ == "__main__":
    folder_name = "./Axie-Infinity/data"
    p = WebScrap(folder_name=folder_name)
    p.web_scrap()























