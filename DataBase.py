import mysql.connector
import json

class database():
    def __init__(self, database_name, host="localhost", user="root", passwd="Anhsin1234"):
        """Initialize a database object with the specified parameters.

        Args:
        database_name (str): the name of the database to connect to
        host (str): the hostname of the database server
        user (str): the username to use for authentication
        passwd (str): the password to use for authentication
        """
        self.host = host
        self.user = user
        self.passwd = passwd
        self.database_name = database_name
        self.connection(database=False)
        self.printOnce = False

    def connection(self, database: bool):
        """Connect to the database with the specified parameters.

        Args:
        database (bool): if True, connect to the specified database; if False, do not connect to a database
        
        Returns:
            None

        Raises:
            mysql.connector.Error: If there is an error connecting to the database.
        """
        if not database:
            config = {
                'host':self.host,
                'user':self.user,
                'passwd':self.passwd,
                'connection_timeout':180,
                'auth_plugin':"mysql_native_password"
            }
        else:
            config = {
                'host':self.host,
                'user':self.user,
                'passwd':self.passwd,
                'database': self.database_name,
                'connection_timeout':180,
                'auth_plugin':"mysql_native_password"
            }
        try:
            self.db = mysql.connector.connect(**config)

            if self.db.is_connected():
                db_Info = self.db.get_server_info()
                print(f"Connected to MySQL database... MySQL Server version on {db_Info}")

                self.cursor = self.db.cursor()
                
                # set global connection timeout arguments
                global_connect_timeout = "SET GLOBAL connect_timeout=180"
                global_wait_timeout = "SET GLOBAL wait_timeout=180"
                global_interactive_timeout = "SET GLOBAL interactive_timeout=180"
                
                # execute the query to set the connection timeout
                self.cursor.execute(global_connect_timeout)
                self.cursor.execute(global_wait_timeout)
                self.cursor.execute(global_interactive_timeout)

                # commit the changes to the database
                self.db.commit()
            else:
                raise mysql.connector.Error(f"Error while connecting to database")

        except mysql.connector.Error as e:
            print("Error while connecting to MySQL", e)

    def create_database(self):
        """
        Creates a new MySQL database.

        Returns:
            None

        Raises:
            mysql.connector.Error: If there is an error creating the database.
        """
        if not self.db.is_connected(): 
            raise mysql.connector.Error(f"Error while connecting to MySQL")
        
        try:
            # check if the database already exists
            query = "SHOW DATABASES"
            self.cursor.execute(query)
            databases = self.cursor.fetchall()

            if (self.database_name,) in databases:
                self.connection(database=True)

                print(f"Database '{self.database_name}' already exists!")
                print(f"Connected to '{self.database_name}")
            else:
                # define the SQL query to create a database
                create_database_query = f"CREATE DATABASE IF NOT EXISTS {self.database_name}"
                
                # execute the query to create a database
                self.cursor.execute(create_database_query)

                self.db.commit()

                self.connection(database=True)

                print(f"Database '{self.database_name} created successfully!")
                print(f"Connected to '{self.database_name}")

        except mysql.connector.Error as e:
            print(f"Error creating database: {e}")

    def createTable(self, table_name: str, columns: list[str]):
        """
        Creates a new table in the MySQL database.

        Args:
            table_name (str): The name of the table to be created.
            columns (list[str]): A list of column names and their data types.

        Returns:
            None

        Raises:
            mysql.connector.Error: If there is an error creating the table.
        """
        if not self.db.is_connected(): 
            raise mysql.connector.Error(f"Error while connecting to MySQL")
        
        try:
            if not self.db.is_connected() or self.db.database != self.database_name:
                self.connection(database=True)

            # check if the database already exists
            query = "SHOW TABLES"
            self.cursor.execute(query)
            tables = self.cursor.fetchall()

            if (table_name,) in tables:
                print(f"Database '{table_name}' already exists!")
            else:
                # define the SQL query to create a database
                create_database_query = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(columns)})"
                
                # execute the query to create a database
                self.cursor.execute(create_database_query)

                self.db.commit()

                print(f"Table '{table_name} created successfully!")
        
        except mysql.connector.Error as e:
            print(f"Error creating database: {e}")
    
    def deleteTable(self, table_name: str):
        """
        Deletes a table from the MySQL database.

        Args:
            table_name (str): The name of the table to be deleted.

        Returns:
            None

        Raises:
            mysql.connector.Error: If there is an error deleting the table.
        """
        if not self.db.is_connected(): 
            raise mysql.connector.Error(f"Error while connecting to MySQL")
        
        try:
            if not self.db.is_connected() or self.db.database != self.database_name:
                self.connection(database=True)

            # check if the database already exists
            query = "SHOW TABLES"
            self.cursor.execute(query)
            tables = self.cursor.fetchall()

            if (table_name,) in tables:
                query = f"DROP TABLE {table_name}"
                self.cursor.execute(query)
                
                self.db.commit()

                print(f"Table '{table_name}' already dropped!")
            else:
                print(f"Table '{table_name} does not exists!")
        
        except mysql.connector.Error as e:
            print(f"Error creating database: {e}")

    def create_users_table(self, table_name: str):
        """
        Create a users table in MySQL database.

        Args:
            table_name (str): The name of the table to be deleted.

        Returns:
            None
        """
        # define the table columns
        columns = [
            'id INT AUTO_INCREMENT PRIMARY KEY',
            'name VARCHAR(255) NOT NULL',
            'email VARCHAR(255)'
        ]

        # create the table
        self.createTable(table_name=table_name, columns=columns)

    def create_user_Chat_History(self, table_name: str):
        """
        Create a users table in MySQL database.

        Args:
            table_name (str): The name of the table to be deleted.

        Returns:
            None
        """
        # define the table columns
        columns = [
            'chat_id INT AUTO_INCREMENT PRIMARY KEY',
            'user_id INT NOT NULL',
            'chat_history TEXT',
            'date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP'
        ]

        # create the table
        self.createTable(table_name=table_name, columns=columns)

    def getTableColumns(self, table_name: str):
        """Returns a list of column names for a given table in the connected MySQL database.
    
        Args:
            table_name (str): The name of the table for which to retrieve column names.
        
        Returns:
            columns (list): A list of column names for the specified table.

        Raises:
            mysql.connector.Error: If there is an error getting the table columns.
        """

        # Check if the database is connected; if not, raise an error
        if not self.db.is_connected(): 
            raise mysql.connector.Error(f"Error while connecting to MySQL")
        
        try:
            # If the database is not connected or is not the correct database, connect to the database
            if not self.db.is_connected() or self.db.database != self.database_name:
                self.connection(database=True)
            
            # Use the DESCRIBE statement to get the column names for the specified table
            query = f"DESCRIBE {table_name}"
            self.cursor.execute(query)

            # Extract the column names from the result and store them in a list
            columns = [column[0] for column in self.cursor.fetchall()]
            
            if not columns:
                print(f"No column(s) found for the given table: '{table_name}'")
                return None
            
            return columns
        
        except mysql.connector.Error as e:
            # If an error occurs, print an error message
            print(f"Error creating database: {e}")

    def getKeyColumn(self, table_name: str):
        """
        Returns the primary key column of the specified table.
        
        Args:
            table_name (str): Name of the table for which the primary key column is to be fetched.

        Returns:
            str: Name of the primary key column, if present.
                 If no primary key is defined, it returns the first column of the table.

        Raises:
            mysql.connector.Error: If there is an error connecting to the MySQL database.

        """

         # Check if the database connection is established
        if not self.db.is_connected(): 
            raise mysql.connector.Error(f"Error while connecting to MySQL")
        
        try:
            # Connect to the database if not connected or if the current database is not the target database
            if not self.db.is_connected() or self.db.database != self.database_name:
                self.connection(database=True)
            
            # Get the column names of the table
            columns = self.getTableColumns(table_name)

            # Check if the table has a primary key constraint
            query = f"SHOW KEYS FROM {table_name} WHERE Key_name = 'PRIMARY'"
            self.cursor.execute(query)
            result = self.cursor.fetchone()

            if result is not None:
                # return the name of the primary key column
                return result[4]
            
            if not columns[0]:
                print(f"No key(s) found from the given table: '{table_name}'")
                return None
            
            #if table does not have a primary key constraint,
            #return the first column name as the key column
            return columns[0]
        
        except mysql.connector.Error as e:
            print(f"Error creating database: {e}")

    def insert_data(self, table_name: str, data: dict):
        """
        This function inserts a row of data into a table in the MySQL database specified by table_name.

        Args:
            table_name (str): The name of the table in the database to insert data into.
            data (dict): A dictionary containing the values to be inserted into the table. The keys should correspond to the column names in the table.
        
        Returns:
            None

        Raises:
            mysql.connector.Error: If there is an error while connecting to the MySQL database.
        """
        if not self.db.is_connected(): 
            raise mysql.connector.Error(f"Error while connecting to MySQL")
        
        try:
            if not self.db.is_connected() or self.db.database != self.database_name:
                self.connection(database=True)
            
            # construct the query to insert a row of data
            insert_query = f"INSERT INTO {table_name} ({','.join(data.keys())}) VALUES ({','.join(['%s']*len(data.values()))})"

            # execute the query to insert the row of data
            self.cursor.execute(insert_query, tuple(data.values()))

            # commit the changes to the database
            self.db.commit()

            # get the primary key value that was auto-generated by MySQL
            key_value = self.cursor.lastrowid

            inserted_data = self.get_data_by_id_as_JSON(table_name=table_name, id=key_value)

            print(f"Data inserted successfully into {table_name} with key {key_value}")

            return inserted_data

        except mysql.connector.Error as e:
            print(f"Error creating database: {e}")

    def get_all_data(self, table_name: str):
        """
        Retrieve all data from the given table.

        Args:
            table_name (str): Name of the table.

        Return:
            list of value from the table

        Raises:
            mysql.connector.Error: If there's an error while connecting to MySQL.

        """
        if not self.db.is_connected(): 
            raise mysql.connector.Error(f"Error while connecting to MySQL")
        
        try:
            if not self.db.is_connected() or self.db.database != self.database_name:
                self.connection(database=True)

            # construct the query to select all data from the table
            query = f"SELECT * FROM {table_name}"

            # execute the query
            self.cursor.execute(query)

            # fetch all the results
            results = self.cursor.fetchall()
            
            if not results:
                print(f"No result(s) found for the given table: '{table_name}'")
                return None
            
            for result in results:
                print(result)

            return results
        
        except mysql.connector.Error as e:
            print(f"Error creating database: {e}")

    def get_all_data_as_JSON(self, table_name: str):
            """
            Retrieve all data from the given table.

            Args:
                table_name (str): Name of the table.

            Return:
                list of JSON pairs key and value in 

            Raises:
                mysql.connector.Error: If there's an error while connecting to MySQL.

            """
            if not self.db.is_connected(): 
                raise mysql.connector.Error(f"Error while connecting to MySQL")
            
            try:
                if not self.db.is_connected() or self.db.database != self.database_name:
                    self.connection(database=True)

                column_names = self.getTableColumns(table_name=table_name)
                
                # Build the SELECT query
                column_pairs = ", ".join([f'"{column}", {column}' for column in column_names])
                
                # construct the query to select all data from the table
                query = f"SELECT JSON_ARRAYAGG(JSON_OBJECT({column_pairs})) FROM {table_name}"

                # execute the query
                self.cursor.execute(query)
                # Fetch the result
                result = self.cursor.fetchone()
                json_array_agg = result[0]

                if not json_array_agg:
                    print(f"No data(s) found for the given table: '{table_name}'")
                    return None
                
                return json.loads(json_array_agg)
            
            except mysql.connector.Error as e:
                print(f"Error creating database: {e}")
    
    def get_data_by_id_as_JSON(self, table_name: str, id: int):
        """
        Retrieve all data from the given table.

        Args:
            table_name (str): Name of the table.

        Return:
            list of JSON pairs key and value in 

        Raises:
            mysql.connector.Error: If there's an error while connecting to MySQL.

        """
        if not self.db.is_connected(): 
            raise mysql.connector.Error(f"Error while connecting to MySQL")
        
        try:
            if not self.db.is_connected() or self.db.database != self.database_name:
                self.connection(database=True)
            
            column_names = self.getTableColumns(table_name=table_name)
            
            # Build the SELECT query
            column_pairs = ", ".join([f'"{column}", {column}' for column in column_names])

            # construct the query to select all data from the table
            query = query = f"SELECT JSON_ARRAYAGG(JSON_OBJECT({column_pairs})) FROM {table_name} WHERE id = %s"

            self.cursor.execute(query, (str(id),))
            # Fetch the result
            result = self.cursor.fetchone()
            if not result[0]:
                print(f"No data(s) found for id: '{id}' in table: '{table_name}'")
                return None
            
            return json.loads(result[0])
        
        except mysql.connector.Error as e:
            print(f"Error creating database: {e}")
    
    def get_data_by_column(self, column_name: str, table_name: str):
        if not self.db.is_connected(): 
            raise mysql.connector.Error(f"Error while connecting to MySQL")
        
        try:
            if not self.db.is_connected() or self.db.database != self.database_name:
                self.connection(database=True)

            # construct the query to select all data from the table
            query = f"SELECT {column_name} FROM {table_name}"

            # execute the query
            self.cursor.execute(query)
            
            data = []
            # fetch the results
            results = self.cursor.fetchall()

            if not results:
                print(f"No data found for column: '{column_name}' in table: '{table_name}'")
                return None
            
            return results
        
        except mysql.connector.Error as e:
            print(f"Error creating database: {e}")

    def get_data_by_column_as_JSON(self, column_name: str, table_name: str):
        if not self.db.is_connected(): 
            raise mysql.connector.Error(f"Error while connecting to MySQL")
        
        try:
            if not self.db.is_connected() or self.db.database != self.database_name:
                self.connection(database=True)
                
            # Build the SELECT query
            column_pairs = f'"{column_name}", {column_name}'
            
            # construct the query to select all data from the table
            query = f"SELECT JSON_ARRAYAGG(JSON_OBJECT({column_pairs})) FROM {table_name}"

            # execute the query
            self.cursor.execute(query)
            # Fetch the result
            result = self.cursor.fetchone()
            json_array_agg = result[0]

            if not json_array_agg:
                print(f"No data(s) found for the given table: '{table_name}'")
                return None
            
            return json.loads(json_array_agg)
        
        except mysql.connector.Error as e:
            print(f"Error creating database: {e}")

    def filter_data_for_chatbot(self, results):
        data = []
        for result in results:
            if isinstance(result[0], str):
                datas = json.loads(result[0])
                data.append(tuple(datas))
            elif isinstance(result[0], int):
                data.append(result[0])

        if not data:
            print(f"No history found for chat bot")
            return None
        
        return data
    
    def delete_data_by_id(self, table_name: str, id: int):
        """
        Deletes a data from the MySQL database base on given id.

        Args:
            table_name (str): The name of the data to be deleted.
            id (int): The id of the data to be deleted

        Returns:
            None

        Raises:
            mysql.connector.Error: If there is an error deleting the table.
        """
        if not self.db.is_connected(): 
            raise mysql.connector.Error(f"Error while connecting to MySQL")
        
        try:
            if not self.db.is_connected() or self.db.database != self.database_name:
                self.connection(database=True)

            # check if the table and id exists
            query = "SHOW TABLES"
            self.cursor.execute(query)
            tables = self.cursor.fetchall()
            ids = self.get_data_by_column(table_name=table_name, column_name="id")

            if (table_name,) in tables and id in ids:
                # Get the columns name of the table
                column_names = self.getTableColumns(table_name=table_name)
            
                # Build the SELECT query
                column_pairs = ", ".join([f'"{column}", {column}' for column in column_names])

                # construct the query to select all data from the table
                query = f"SELECT JSON_ARRAYAGG(JSON_OBJECT({column_pairs})) FROM {table_name} WHERE id = %s"

                # execute the query
                self.cursor.execute(query, id)
                # Fetch the result
                result = self.cursor.fetchone()
                json_array_agg = result[0]
                deleted_data = json.loads(json_array_agg)

                query = f"DELETE FROM {table_name} WHERE id = %s"
                self.cursor.execute(query, id)
                self.db.commit()

                print(f"Data '{deleted_data}' already dropped!")
                return deleted_data
            else:
                print(f"Data with id: '{id}' does not exists in table: '{table_name}'!")
                return None
        
        except mysql.connector.Error as e:
            print(f"Error creating database: {e}")

    def update_value(self, table_name: str, new_values: dict, id: int):
        """
        Update a value in the specified table.

        Args:
            table_name (str): Name of the table.
            new_value (dict): Dictionary containing the new values for each column.
            id (int): ID of the row to update.

        Returns:
            bool: True if the update was successful, False otherwise.

        Raises:
            mysql.connector.Error: If there's an error while connecting to MySQL.

        """
        if not self.db.is_connected(): 
            raise mysql.connector.Error(f"Error while connecting to MySQL")
        
        try:
            if not self.db.is_connected() or self.db.database != self.database_name:
                self.connection(database=True)

            table_columns = self.getTableColumns(table_name=table_name)

            # Check if any of the specified columns are missing in the table
            missing_columns = [column for column in new_values.keys() if column not in table_columns]
            if missing_columns:
                print(f"The given columns does not exist in the table")
                return None
            
            # construct the query to update all values
            query = f"UPDATE {table_name} SET "

            # add the new values to the query
            set_values = ", ".join([f"{column} = %s" for column in new_values.keys()])
            query += set_values

            # add the condition to the query
            query += f" WHERE id = %s"

            # execute the query with the new values
            self.cursor.execute(query, tuple(list(new_values.values())+[id]))
            
            # commit the changes to the database
            self.db.commit()

            column_names = self.getTableColumns(table_name=table_name)
            
            # Build the SELECT query
            column_pairs = ", ".join([f'"{column}", {column}' for column in column_names])

            # construct the query to select all data from the table
            query = f"SELECT JSON_ARRAYAGG(JSON_OBJECT({column_pairs})) FROM {table_name} WHERE id = %s"
            self.cursor.execute(query, (str(id),))
            # Fetch the result
            result = self.cursor.fetchone()
            if not result[0]:
                print(f"No data(s) found for id: '{id}' in table: '{table_name}'")
                return None
            
            return json.loads(result[0])

        except mysql.connector.Error as e:
            print(f"Error updating values: {e}")
        

if __name__ == "__main__":
    db = database('ChatbotDB')
    db.create_database()
    user_id = 1
    table_name = f'User_Chat_History_{user_id}'
    # db.create_user_Chat_History(table_name=table_name)
    # data = {'user_id': 1, 'chat_history': 'Hello, how can I help you?'}
    # db.insert_data(table_name=table_name, data=data)
    # db.get_all_data(table_name=table_name)
    data=db.get_data_by_column(column_name='chat_history', table_name=table_name)
    # print(len(results), "\n\n")
    # print(data)
    # db.deleteTable(table_name=table_name)
