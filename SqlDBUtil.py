# -*- coding: utf-8 -*-
"""
Created on Tue Jan 15 11:11:54 2019

@author: ptichkule
"""
import pyodbc
import pandas as pd
import re
import sqlalchemy
from copy import deepcopy
from argparse import ArgumentParser
from math import ceil
from WbtPyUtilities import ProgressBar as PB

if __name__ == "__main__":
    help_str = """  set conn_str = 'bat_conn' for connecting to BAT server
                    set conn_str = 'gremlin_conn' for connecting to NvBugs Gremlin server
                    set conn_str = 'devtest_conn' for connecting to Devtest server, Select only
                    set conn_str = 'wbt_vm1_conn1' for connecting to SQL hosted on HQNVWBTD01'
                    set conn_str = 'wbt_bg_vm1_conn1' for connecting to SQL hosted on HQNVWBTD01'
                """

    parser = ArgumentParser()
    parser.add_argument('-m','--mode', required=False, default='none',help="To select mode as from csv default is none")
    parser.add_argument('-f','--inputFile', required=False, default='data.csv',help="To pass csv/json file name")
    parser.add_argument('-cn','--conn_str', required=False, default='bat_conn',help="To pass SQL connection string \n\n" + help_str)
    pargs = parser.parse_args()


class SqlDBUtil:
    DevTestLink = 'Driver={ODBC Driver 13 for SQL Server};''Server=HQNVSQL171;''UID=DevTest_User;''PWD=Nvidia@2o1o;'
    GremlinLink = 'Driver={ODBC Driver 13 for SQL Server};''Server=NVSQL113\\SQLPROD113;Trusted_Connection=Yes'
    BatServerLink = 'Driver={ODBC Driver 13 for SQL Server};''Server=RNNVSQL174;''UID=wbt_user;''PWD=wbt_user@123;' # old GPUSWQA-PTIC-W7
    WBT_VM1_Conn1 = 'Driver={ODBC Driver 13 for SQL Server};''Server=RNNVSQL174;''UID=wbt_user;''PWD=wbt_user@123;' # old HQNVWBTD01
    IT_PROD_SQL174 = 'Driver={ODBC Driver 13 for SQL Server};''Server=RNNVSQL174;''UID=wbt_user;''PWD=wbt_user@123;'
    WBT_BG_VM1_Conn1 = 'Driver={ODBC Driver 13 for SQL Server};''Server=bgdvbatdevenv01;''UID=sa;''PWD=WBTR0cks!;'

    def __init__(self,data_frame):
        self.df = data_frame
    
    @staticmethod
    def execute_select_query(query,conn_str = 'bat_conn' ):
        """
        Input
        set conn_str = 'bat_conn' for connecting to BAT server
        set conn_str = 'gremlin_conn' for connecting to NvBugs Gremlin server
        set conn_str = 'devtest_conn' for connecting to Devtest server, Select only
        set conn_str = 'wbt_vm1_conn1' for connecting to SQL hosted on HQNVWBTD01'
        or pass your own conn_str = '<conn_string>'
        
        Return 
            Tuple of ( Bool , List of Tuples)
            e.g. (True,[ ('A', 1), ('B',2) ])
            e.g. (False, "Error string")
        """
        try:
            if conn_str == 'bat_conn':
                conn_str = SqlDBUtil.BatServerLink
            elif conn_str == 'gremlin_conn':
                conn_str = SqlDBUtil.GremlinLink
            elif conn_str == 'devtest_conn':
                conn_str = SqlDBUtil.DevTestLink
            elif conn_str == 'wbt_vm1_conn1':
                conn_str = SqlDBUtil.WBT_VM1_Conn1
            elif conn_str == 'wbt_bg_vm1_conn1':
                conn_str = SqlDBUtil.WBT_BG_VM1_Conn1
            
            connection = pyodbc.connect(conn_str)
            crs = connection.cursor()
            crs.execute(query)
            result = crs.fetchall()
            crs.commit()
            crs.close()
            del crs
            connection.close()
            return True, result
        except Exception as e:
            print(e)
            return False, str(e)

    
    @staticmethod
    def execute_select_query_get_df(query,columns,conn_str = 'bat_conn' ):
        """
        Input
        set conn_str = 'bat_conn' for connecting to BAT server
        set conn_str = 'gremlin_conn' for connecting to NvBugs Gremlin server
        set conn_str = 'devtest_conn' for connecting to Devtest server, Select only
        set conn_str = 'wbt_vm1_conn1' for connecting to SQL hosted on HQNVWBTD01'
        or pass your own conn_str = '<conn_string>'
        
        Return 
            Tuple of ( Bool , Data)
            e.g. (True,DataFrame)
            e.g. (False, "Error string")
        """
        try:
            status, data = SqlDBUtil.execute_select_query(query,conn_str=conn_str)
            if not status:
                return status, data
            data_list = [list(x) for x in data]
            print("Length of df",len(data_list))
            df = pd.DataFrame(data_list,columns=columns)
            return True, df
        except Exception as e:
            print(e)
            return False, str(e)

    @staticmethod
    def execute_select_query_get_df2(query, conn_str='bat_conn'):
        """
        Input
        set conn_str = 'bat_conn' for connecting to BAT server
        set conn_str = 'gremlin_conn' for connecting to NvBugs Gremlin server
        set conn_str = 'devtest_conn' for connecting to Devtest server, Select only
        set conn_str = 'wbt_vm1_conn1' for connecting to SQL hosted on HQNVWBTD01'
        or pass your own conn_str = '<conn_string>'
        
        Return 
            Tuple of ( Bool , Data)
            e.g. (True,DataFrame)
            e.g. (False, "Error string")
        """
        try:
            if conn_str == 'bat_conn':
                conn_str = SqlDBUtil.BatServerLink
            elif conn_str == 'gremlin_conn':
                conn_str = SqlDBUtil.GremlinLink
            elif conn_str == 'devtest_conn':
                conn_str = SqlDBUtil.DevTestLink
            elif conn_str == 'wbt_vm1_conn1':
                conn_str = SqlDBUtil.WBT_VM1_Conn1
            elif conn_str == 'wbt_bg_vm1_conn1':
                conn_str = SqlDBUtil.WBT_BG_VM1_Conn1

            sql_conn = pyodbc.connect(conn_str)
            df = pd.read_sql(query, sql_conn)
            return True, df
        except Exception as e:
            print(e)
            return False, str(e)

    @staticmethod
    def execute_queries(queries, conn_str='bat_conn', verbose=True):
        """
        Note: The method does not read and return data, Kindly use execute_select_query for the same
        Inputs:
        queries = <List of query strings>
        conn_str
        set conn_str = 'bat_conn' for connecting to BAT server
        set conn_str = 'gremlin_conn' for connecting to NvBugs Gremlin server
        set conn_str = 'devtest_conn' for connecting to Devtest server, Select only
        set conn_str = 'wbt_vm1_conn1' for connecting to SQL hosted on HQNVWBTD01'
        or pass your own conn_str = '<conn_string>'
        
        Return 
            On Success Tuple of True,"Success"
            On Failure Tuple of False, <Error_String>
        """
        try:
            if conn_str == 'bat_conn':
                conn_str = SqlDBUtil.BatServerLink
            elif conn_str == 'gremlin_conn':
                conn_str = SqlDBUtil.GremlinLink
            elif conn_str == 'devtest_conn':
                conn_str = SqlDBUtil.DevTestLink
            elif conn_str == 'wbt_vm1_conn1':
                conn_str = SqlDBUtil.WBT_VM1_Conn1
            elif conn_str == 'wbt_bg_vm1_conn1':
                conn_str = SqlDBUtil.WBT_BG_VM1_Conn1

            connection = pyodbc.connect(conn_str)
            crs = connection.cursor()
            crs.execute('BEGIN TRANSACTION')
            if verbose:
                print('Executing {} queries'.format(len(queries)))
            index = 0
            if verbose:
                PB.printProgressBar(index, len(queries), prefix = 'Progress:', suffix = 'Complete', length = 50, decimals = 3)
            for query in queries:
                crs.execute(query)
                index = index + 1
                if(index%100 == 0):
                    with open("Query{}.txt".format(index), "w") as text_file:
                        text_file.write(query)
                if verbose:
                    PB.printProgressBar(index, len(queries), prefix = 'Progress:', suffix = 'Complete', length = 50, decimals = 3)
            crs.execute('COMMIT')
            crs.commit()
            crs.close()
            del crs
            connection.close()
            return True, "Success"
        except Exception as e:
            try:
                with open("Query.txt", "w") as text_file:
                    text_file.write(queries[index])
            except Exception as e2:
                print(e2)
            print(e)
            return False, str(e)

    @staticmethod
    def execute_queries_read_output(queries, conn_str='bat_conn', verbose=True, column_to_read=[]):
        """
        Note: The method does not read and return data, Kindly use execute_select_query for the same
        Inputs:
        queries = <List of query strings>
        conn_str
        set conn_str = 'bat_conn' for connecting to BAT server
        set conn_str = 'gremlin_conn' for connecting to NvBugs Gremlin server
        set conn_str = 'devtest_conn' for connecting to Devtest server, Select only
        set conn_str = 'wbt_vm1_conn1' for connecting to SQL hosted on HQNVWBTD01'
        or pass your own conn_str = '<conn_string>'
        
        Return 
            On Success Tuple of True,"Success"
            On Failure Tuple of False, <Error_String>
        """
        try:
            if conn_str == 'bat_conn':
                conn_str = SqlDBUtil.BatServerLink
            elif conn_str == 'gremlin_conn':
                conn_str = SqlDBUtil.GremlinLink
            elif conn_str == 'devtest_conn':
                conn_str = SqlDBUtil.DevTestLink
            elif conn_str == 'wbt_vm1_conn1':
                conn_str = SqlDBUtil.WBT_VM1_Conn1
            elif conn_str == 'wbt_bg_vm1_conn1':
                conn_str = SqlDBUtil.WBT_BG_VM1_Conn1

            connection = pyodbc.connect(conn_str)
            crs = connection.cursor()
            crs.execute('BEGIN TRANSACTION')
            if verbose:
                print('Executing {} queries'.format(len(queries)))
            index = 0
            if verbose:
                PB.printProgressBar(index, len(queries), prefix = 'Progress:', suffix = 'Complete', length = 50, decimals = 3)
            all_result = []
            for query in queries:
                crs.execute(query)
                result = crs.fetchall()
                result = [list(x) for x in result]
                [all_result.append(x) for x in result]
                index = index + 1
                if(index%100 == 0):
                    with open("Query{}.txt".format(index), "w") as text_file:
                        text_file.write(query)
                if verbose:
                    PB.printProgressBar(index, len(queries), prefix = 'Progress:', suffix = 'Complete', length = 50, decimals = 3)
            df = pd.DataFrame(all_result,columns=column_to_read)
            crs.execute('COMMIT')
            crs.commit()
            crs.close()
            del crs
            connection.close()
            
            return True, df
        except Exception as e:
            try:
                with open("Query.txt", "w") as text_file:
                    text_file.write(queries[index])
            except Exception as e2:
                print(e2)
            print(e)
            return False, str(e)

    @staticmethod
    def generate_insert_queries_from_df(df,db_table,db_name,max_insert_per_query=900,columns='all',
                                        drop_duplicate = True, verbose=True,
                                        read_inserted_columns=[]):
        """
        On success Returns Tuple of True & List of string(queries)
        On Falure Returns Tuple of False & <Error_String>
        """
        try:
            if(max_insert_per_query > 1000):
                return False, "Can't insert more than 1000 record at once"
            if columns == 'all':
                columns = list(df.columns)
            elif type(columns) != list:
                print('columns data must be a list')        
            if drop_duplicate:
                df.drop_duplicates(inplace=True, keep='first')
            df_insert = df[columns]
            if verbose:
                print('Generating insert queries')
            encrypter = "#vft#-encrypter-#vft#"
            for clm in columns:
                df_insert[clm] = df_insert[clm].apply(lambda m: re.sub(r"'",encrypter,m) if type(m) == str else m )
            query = str(list(columns))
            query = query.replace('[','')
            query = query.replace(']','')
            query = query.replace("',",'],')
            query = query.replace("'","[")
            query = " ( " + query[:-1]  + "] ) "
            query = "INSERT INTO [{}].[dbo].[{}]".format(db_name,db_table) + query 
            if len(read_inserted_columns) > 0:
                query =  query + 'Output ' + ', '.join([ f'[Inserted].[{clm}]' for clm in read_inserted_columns])

            query = query + " VALUES "
            queries = []
            total_query_count = ceil(len(df_insert)/max_insert_per_query)
            if verbose:
                PB.printProgressBar(len(queries),total_query_count , prefix = 'Progress:', suffix = 'Complete', length = 50, decimals = 3)
            for i in range(0,len(df_insert),max_insert_per_query):
                tmp_df = df_insert[i:i+max_insert_per_query]
                tmp_df = tmp_df.reset_index(drop=True)
                if(len(columns) == 1):
                    value = [ "( {} )".format(tuple(tmp_df.loc[index])[0]) for index in range(0,len(tmp_df))]
                else:
                    #formating tuple use encoded string so '\' get converted to '\\', replace converts it back to '\'
                    value = [ str(tuple(tmp_df.loc[index])).replace('\\\\','\\') for index in range(0,len(tmp_df))]
                tmp_query = query + ", ".join(value)
                tmp_query = re.sub(encrypter,"''",tmp_query)
                queries.append(tmp_query)
                if verbose:
                    PB.printProgressBar(len(queries),total_query_count , prefix = 'Progress:', suffix = 'Complete', length = 50, decimals = 3)
            return True, queries
        except Exception as e:
            print(e)
            return False, str(e)

    @staticmethod
    def generate_where_clause_string(df, columns='all', max_per_query=900, verbose = True, include_column_braces=False):
        try:
            if columns == 'all':
                columns = list(df.columns)
            elif type(columns) != list:
                print('columns data must be a list')
                return False, 'columns data must be a list'
            if verbose:
                print('Generating where clause strings')
            df_where = df[columns]
            encrypter = "#vft#-encrypter-#vft#"
            for clm in columns:
                df_where[clm] = df_where[clm].apply(lambda m: re.sub(r'\'',encrypter,m) if type(m) == str else m )
            queries = []
            total_query_count = ceil(len(df)/max_per_query)
            if verbose:
                PB.printProgressBar(len(queries),total_query_count , prefix = 'Progress:', suffix = 'Complete', length = 50, decimals = 3)
            for i in range(0,len(df_where),max_per_query):
                tmp_df = df_where[i:i+max_per_query]
                tmp_df = tmp_df.reset_index(drop=True)
                if include_column_braces:
                    tmp_query = " OR ".join([ "(" + " AND ".join([ "[" + str(c) + "] = '" + str(row[c]) + "'" for c in columns ]) + ")" for _, row in tmp_df.iterrows() ])
                else:
                    tmp_query = " OR ".join([ "(" + " AND ".join([ str(c) + " = '" + str(row[c]) + "'" for c in columns ]) + ")" for _, row in tmp_df.iterrows() ])
                tmp_query = re.sub(encrypter,"''",tmp_query)
                queries.append(tmp_query)
                if verbose:
                    PB.printProgressBar(len(queries),total_query_count , prefix = 'Progress:', suffix = 'Complete', length = 50, decimals = 3)
            return True, queries
        except Exception as e:
            print(e)
            return False, str(e)
    
    @staticmethod
    def generate_delete_query(df,db_table,db_name,columns='all',max_per_query=900, verbose=True):
        """
        On success Returns Tuple of True & <Delete Query>
        On Falure Returns Tuple of False & <Error_String>
        """
        try:
            query = "DELETE FROM [{}].[dbo].[{}] WHERE ".format(db_name,db_table)
            status, query_clauses = SqlDBUtil.generate_where_clause_string(df,columns=columns,max_per_query=max_per_query,verbose=verbose)
            if not status:
                return status, query_clauses
            queries = [ query + w for w in query_clauses ]
            return True, queries
        except Exception as e:
            print('generate_delete_queries',e)
            return False, str(e)

    @staticmethod
    def generate_update_queries(df,db_table,db_name,update_columns,conditional_columns):
        """
        On success Returns Tuple of True & <Update Query List>
        On Falure Returns Tuple of False & <Error_String>
        """
        try:
            if len(df) < 1:
                return False, "Empty Dataframe"
            tmp_df = deepcopy(df)
            tmp_df = tmp_df.astype(str)
            if len(tmp_df) < 1:
                return False, "Empty Dataframe"
            tmp_df.reset_index(inplace=True,drop=True)
            tmp_column = "::update_query_tmp_column::"
            tmp_df[tmp_column] = "UPDATE [{}].[dbo].[{}] ".format(db_name,db_table)
            encrypter = "#vft#-encrypter-#vft#"
            for clm in tmp_df.columns:
                tmp_df[clm] = tmp_df[clm].apply(lambda m: re.sub(r'\'',encrypter,m) if type(m) == str else m )
            
            print("Generating Queries")
            for i, column in zip( range(len(update_columns)) ,update_columns):
                if type(column) == list or type(column) == tuple:
                    column0 = column[0]
                    column1 = column[-1]
                else:
                    column0 = column1 = column
                if i == 0:
                    tmp_df[tmp_column]  = tmp_df[tmp_column] + "SET [" + column1 + "] = '" + tmp_df[column0] + "' "
                else:
                    tmp_df[tmp_column]  =  tmp_df[tmp_column] + ", [" + column1 + "] = '" + tmp_df[column0] + "' "
            
            for i, column in zip(range(len(conditional_columns)),conditional_columns):
                if type(column) == list or type(column) == tuple:
                    column0 = column[0]
                    column1 = column[-1]
                else:
                    column0 = column1 = column
                if i == 0:
                    tmp_df[tmp_column]  = tmp_df[tmp_column] + " WHERE [" + column1 + "] = '" + tmp_df[column0] + "' "
                else:
                    tmp_df[tmp_column]  = tmp_df[tmp_column] +  " AND [" +  column1 + "] = '" + tmp_df[column0] + "' "
            queries =  list(tmp_df[tmp_column])
            queries = [re.sub(encrypter,"''",tmp_query) for tmp_query in queries]
            return True, queries     
        except Exception as e:
            print(e)
            return False, str(e)

    @staticmethod
    def insert_df_to_sqlDB(df,db_table,db_name,max_insert_per_query=900,columns='all',conn_str = 'bat_conn' ):
        """
        Note: The method does not read and return data, Kindly use execute_select_query for the same
        Input
        set conn_str = 'bat_conn' for connecting to BAT server
        set conn_str = 'gremlin_conn' for connecting to NvBugs Gremlin server
        set conn_str = 'devtest_conn' for connecting to Devtest server, Select only
        set conn_str = 'wbt_vm1_conn1' for connecting to SQL hosted on HQNVWBTD01'
        or pass your own conn_str = '<conn_string>'
        
        Return 
            On Success Tuple of True,"Success"
            On Failure Tuple of False, <Error_String>
        """
        try:
            status, queries = SqlDBUtil.generate_insert_queries_from_df(df,db_table,db_name,max_insert_per_query,columns)
            if not status:
                return status, queries
            status, message = SqlDBUtil.execute_queries(queries,conn_str=conn_str)
            return status, message
        except Exception as e:
            print(e)
            return False, str(e)

    @staticmethod
    def insert_json_to_sqlDB(data_json,db_table,db_name,max_insert_per_query=900,columns='all',conn_str = 'bat_conn' ):
        """
        Note: The method does not read and return data, Kindly use execute_select_query for the same
        Input
        set conn_str = 'bat_conn' for connecting to BAT server
        set conn_str = 'gremlin_conn' for connecting to NvBugs Gremlin server
        set conn_str = 'devtest_conn' for connecting to Devtest server, Select only
        set conn_str = 'wbt_vm1_conn1' for connecting to SQL hosted on HQNVWBTD01'
        or pass your own conn_str = '<conn_string>'
        
        Return 
            On Success Tuple of True,"Success"
            On Failure Tuple of False, <Error_String>
        """
        try:
            df = pd.DataFrame(data_json)
            return SqlDBUtil.insert_df_to_sqlDB(df,db_table,db_name,max_insert_per_query,columns,conn_str)
        except Exception as e:
            print(e)
            return False, str(e)
    
    @staticmethod
    def insert_csv_file_to_sqlDB(csvFile,db_table,db_name,max_insert_per_query=900,columns='all',conn_str = 'bat_conn' ):
        """
        Note: The method does not read and return data, Kindly use execute_select_query for the same
        Input
        set conn_str = 'bat_conn' for connecting to BAT server
        set conn_str = 'gremlin_conn' for connecting to NvBugs Gremlin server
        set conn_str = 'devtest_conn' for connecting to Devtest server, Select only
        set conn_str = 'wbt_vm1_conn1' for connecting to SQL hosted on HQNVWBTD01'
        or pass your own conn_str = '<conn_string>'
        
        Return 
            On Success Tuple of True,"Success"
            On Failure Tuple of False, <Error_String>
        """
        try:
            df = pd.read_csv(csvFile)
            return SqlDBUtil.insert_df_to_sqlDB(df,db_table,db_name,max_insert_per_query,columns,conn_str)
        except Exception as e:
            print(e)
            return False, str(e)


    @staticmethod
    def insert_json_file_to_sqlDB(jsonFile,db_table,db_name,max_insert_per_query=900,columns='all',conn_str = 'bat_conn' ):
        """
        Note: The method does not read and return data, Kindly use execute_select_query for the same
        Input
        set conn_str = 'bat_conn' for connecting to BAT server
        set conn_str = 'gremlin_conn' for connecting to NvBugs Gremlin server
        set conn_str = 'devtest_conn' for connecting to Devtest server, Select only
        set conn_str = 'wbt_vm1_conn1' for connecting to SQL hosted on HQNVWBTD01'
        or pass your own conn_str = '<conn_string>'
        
        Return 
            On Success Tuple of True,"Success"
            On Failure Tuple of False, <Error_String>
        """
        try:
            df = pd.read_json(jsonFile)
            return SqlDBUtil.insert_df_to_sqlDB(df,db_table,db_name,max_insert_per_query,columns,conn_str)
        except Exception as e:
            print(e)
            return False, str(e)
    
    @staticmethod
    def insert_excel_file_to_sqlDB(file,db_table,db_name,max_insert_per_query=900,columns='all',conn_str = 'bat_conn' ):
        """
        Note: The method does not read and return data, Kindly use execute_select_query for the same
        Input
        set conn_str = 'bat_conn' for connecting to BAT server
        set conn_str = 'gremlin_conn' for connecting to NvBugs Gremlin server
        set conn_str = 'devtest_conn' for connecting to Devtest server, Select only
        set conn_str = 'wbt_vm1_conn1' for connecting to SQL hosted on HQNVWBTD01'
        or pass your own conn_str = '<conn_string>'
        
        Return 
            On Success Tuple of True,"Success"
            On Failure Tuple of False, <Error_String>
        """
        try:
            df = pd.read_excel(file)
            return SqlDBUtil.insert_df_to_sqlDB(df,db_table,db_name,max_insert_per_query,columns,conn_str)
        except Exception as e:
            print(e)
            return False, str(e)

