import pandas as pd

class PandasManager:
    def __init__(self, file_path,file_type):
        self.file_path = file_path
        self.file_type = file_type
        if file_type == "csv":
            self.df = pd.read_csv(file_path)
        elif file_type == "excel":
            self.df = pd.read_excel(file_path)
        elif file_type == "json":
            self.df = pd.read_json(file_path)
        elif file_type == "parquet":
            self.df = pd.read_parquet(file_path)
        elif file_type == "pickle":
            self.df = pd.read_pickle(file_path)
        elif file_type == "sql":
            self.df = pd.read_sql(file_path)
    
    def get_df_info(self):
        data_types = self.df.dtypes
        columns = self.df.columns
        return data_types, columns
    
    def get_df_sample(self):
        return self.df.sample(5)
    
    def query_df(self, query):
        return self.df.query(query)
    
     
    
    