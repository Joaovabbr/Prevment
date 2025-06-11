import sqlite3
import re
import hashlib
import unicodedata

class SQLiteHandler:
    def __init__(self, db_path):
        self.db_path = db_path
        self.connection = sqlite3.connect(self.db_path)
        self.cursor = self.connection.cursor()
    
    def close(self):
        self.connection.commit()
        self.connection.close()

    def setup_table(self, table_name: str, columns: dict):
        """
        Set up a table with the specified name and columns.
        :param table_name: Name of the table to create.
        :param columns: A dictionary where keys are column names and values are their data types.
        """
        columns_with_types = ', '.join([f"{col} {dtype}" for col, dtype in columns.items()])
        create_table_query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_with_types})"
        self.cursor.execute(create_table_query)
        self.connection.commit()

    
    def fetch_data(self, table_name, conditions=None):
        """
        Fetch data from the specified table.
        :param table_name: Name of the table to fetch data from.
        :param conditions: Optional conditions for the query (as a string).
        :return: List of tuples containing the fetched data.
        """
        query = f"SELECT * FROM {table_name}"
        if conditions:
            query += f" WHERE {conditions}"
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def delete_data(self, table_name, conditions):
        """
        Delete data from the specified table based on conditions.
        :param table_name: Name of the table to delete data from.
        :param conditions: Conditions for the deletion (as a string).
        """
        delete_query = f"DELETE FROM {table_name} WHERE {conditions}"
        self.cursor.execute(delete_query)
        self.connection.commit()

    def post_id(self, text, likes, coments, shares):
        # Normaliza unicode (NFKC ou NFC)
        normalized_text = unicodedata.normalize('NFKC', text)
        
        # Remove caracteres de controle e pontuações desnecessárias, mantendo letras de qualquer alfabeto e números
        # Aqui mantemos letras, números e espaços, removemos símbolos pontuação simples para limpar
        cleaned_text = re.sub(r'[^\w\s]', '', normalized_text, flags=re.UNICODE)
        
        # Opcional: converte para minúsculas para uniformizar (alguns alfabetos podem não ter case, mas ok)
        cleaned_text = cleaned_text.lower()
        
        # Usa os primeiros 50 caracteres para o ID
        base = cleaned_text[:50]
        
        # Cria string base combinando com os números
        string_base = f"{base}_{likes}_{coments}_{shares}"
        
        # Gera hash MD5 (tamanho fixo e praticamente único)
        hash_id = hashlib.md5(string_base.encode('utf-8')).hexdigest()
        
        return hash_id
    
    def news_id(self, title, url, source, time):
        """
        Generate a unique ID for news articles based on title, URL, source, and time.
        :param title: Title of the news article.
        :param url: URL of the news article.
        :param source: Source of the news article.
        :param time: Time of the news article.
        :return: A unique ID string.
        """
        base = f"{title}_{url}_{source}_{time}"
        return hashlib.md5(base.encode('utf-8')).hexdigest()

    def insert_data(self, table_name, data:dict):
        """
        Insert data into the specified table.
        :param table_name: Name of the table to insert data into.
        :param data: A dictionary where keys are column names and values are the data to insert.
        """
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        insert_query = f"INSERT OR REPLACE INTO {table_name} ({columns}) VALUES ({placeholders})"
        self.cursor.execute(insert_query, tuple(data.values()))
        self.connection.commit()