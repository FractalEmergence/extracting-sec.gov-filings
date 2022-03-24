import requests
import requests_random_user_agent # pip install requests-random-user-agent
import pandas as pd
from bs4 import BeautifulSoup # pip install beautifulsoup4
import re
import sqlite3
from sqlite3 import Error
import os
import sys
from contextlib import closing # pip install contextlib2
import time
from dateutil import parser # pip install python-dateutil
from datetime import datetime

# You can find company's CIK number at https://www.sec.gov/edgar/searchedgar/companysearch.html
company_CIKs = ['1018724', '1318605', '789019']
# Enter what forms(s) you want to extract using the '10-K', '10-Q', '8-K' format.
filing_types = ['10-k']
# Enter the database name that you want to use and populate.
#The database will be automatically created if it does not exist.
db_name = 'edgar.db'
# Specify the folder path for DB file. For example "C:\sqlite\db"
folder_path = r"C:\sqlite\db"
db_path = f"{folder_path}\{db_name}"
# Enter the date range for the filings in the 'YYYY-MM-DD' format
start_date = '2020-01-01'
end_date = '2022-01-01'

# Create a class to handle connection(s) to SQLite database(s).
class DB_Connection:
    # Create a directory for the DB file if the directory does not exist.
    def create_folder(self):
        if not os.path.exists(UserParameters.folder_path):
            os.makedirs(UserParameters.folder_path)
            print(f'Successfully created a new folder path {UserParameters.folder_path}.')
        else:
            print(f'Folder path {UserParameters.folder_path} already exists.')


    # Open connection to the database, if connection fails abort the program.
    # If the DB file does not already exist, it will be automatically created.
    @classmethod
    def open_conn(cls, db_path):
        try:
            cls.conn = sqlite3.connect(db_path)
            print(f'Successfully connected to the {db_path} database.')
            return cls.conn
        except sqlite3.Error as e:
            print(f'Error occurred, unable to connect to the {db_path} database.')
            print(e)
            UserParameters.error_messages.append(e)
            return None
    # Close connection to the database.
    @classmethod
    def close_conn(cls):
        try:
            cls.conn.commit()
            print('Commited transactions.')
            cls.conn.close()
            print('Closing all database connections.')
        except Exception as e:
            print(f'Unable to close database connection.\n{e}')


class Filing_Links:

    def __init__(self):
            # Capitalize the letters of form type, since by default SQLite is case sensitive.
            UserParameters.filing_types = [item.upper() for item in UserParameters.filing_types]
    # Get available filings types for a specific company and their respective links.
    def Get_Filing_Links(self):
        try:
            for Company_CIK_Number in UserParameters.company_CIKs:
                for Filing_Type in UserParameters.filing_types:
                    # define our parameters dictionary
                    filing_parameters = {'action':'getcompany',
                                  'CIK':Company_CIK_Number,
                                  'type':Filing_Type,
                                  'dateb':'',
                                  'owner':'exclude',
                                  'start':'',
                                  'output':'',
                                  'count':'100'}

                    # request the url, and then parse the response.
                    response = requests.get(url = r"https://www.sec.gov/cgi-bin/browse-edgar",
                                            params = filing_parameters)
                    # Add 0.1 second time delay to comply with SEC.gov's 10 requests per second limit.
                    time.sleep(0.1)
                    soup = BeautifulSoup(response.content, 'html.parser')
                    # Find the document table that contains filing information.
                    main_table = soup.find_all('table', class_='tableFile2')
                    # The base URL will be used to construct document links URLs.
                    sec_base_url = r"https://www.sec.gov"
                    Company_Name_path=str(soup.find('span',{'class':'companyName'}))
                    if Company_Name_path != None:
                        try:
                            Company_Name = re.search('<span class="companyName">(.*)<acronym title',
                                                     Company_Name_path).group(1)
                        except AttributeError:
                            print("Could not find company name, \
                                   assigning NULL value to company name.")
                            Company_Name = None
                    # loop through each row of table and extract filing numbers, links, etc.
                    for row in main_table[0].find_all('tr'):
                        # find all the rows under the 'td' element.
                        cols = row.find_all('td')
                        # If no information was detected, move on to the next row.
                        if len(cols) != 0:
                            # Get the text from the table.
                            Filing_Type = cols[0].text.strip()
                            Filing_Date = cols[3].text.strip()
                            Filing_Number = cols[4].text.strip()
                            Filing_Number = ''.join(e for e in Filing_Number if e.isalnum())


                            # Get the URL path to the filing number.
                            filing_number_path = cols[4].find('a')
                            if filing_number_path != None:
                                Filing_Number_Link = sec_base_url + filing_number_path['href']
                            else:
                               break

                            # Get the URL path to the document.
                            document_link_path = cols[1].find('a',
                                                              {'href':True, 'id':'documentsbutton'})
                            if document_link_path != None:
                                Document_Link = sec_base_url + document_link_path['href']
                            else:
                                Document_Link = None

                            # Get the account number.
                            try:
                                Account_Number= cols[2].text.strip()
                                Account_Number = re.search('Acc-no:(.*)(34 Act)',
                                                            Account_Number).group(1)
                                Account_Number = ''.join(e for e in Account_Number if e.isalnum())

                            except Exception as e:
                                """
                                Add break if you don't want empty account number rows.
                                If account number is not present, the interactive document
                                link will not be available. If the interactive link is not
                                present, we will not be able to extract the individual
                                tables containing financial statements..
                                """
                                Account_Number = None
                                print(f'Could not retrieve the account number, \
                                        assigning NULL value.\n{e}')

                            # Get the URL path to the interactive document.
                            interactive_data_path = cols[1].find('a',
                                                                 {'href':True, 'id':'interactiveDataBtn'})
                            if interactive_data_path != None:
                                Interactive_Data_Link = sec_base_url + interactive_data_path['href']
                                # If the interactive data link exists, then so does the FilingSummary.xml link.
                                Summary_Link_Xml = Document_Link.replace(f"/{Account_Number}",'')\
                                                                .replace('-','')\
                                                                .replace('index.htm' ,'/FilingSummary.xml')

                            else:
                                # break
                                Interactive_Data_Link = None
                                Summary_Link_Xml = None

                            self.info_to_sql(Company_Name, Company_CIK_Number, Account_Number,
                                             Filing_Type, Filing_Number, Filing_Date, Document_Link,
                                             Interactive_Data_Link, Filing_Number_Link, Summary_Link_Xml)
        except Exception as e:
            print(f"Could not retrieve the table containing the necessary information.\
                    \nAbording the program.\nIf index list is out of range, make sure \
                    \nthat you entered the correct CIK number(s).")
            print(e)
            UserParameters.error_messages.append(e)
            return None

    # Migrate the DataFrame containing, filing and document links information to a local SQLite database.
    def info_to_sql(self, Company_Name, Company_CIK_Number, Account_Number,
                    Filing_Type, Filing_Number, Filing_Date, Document_Link,
                    Interactive_Data_Link, Filing_Number_Link, Summary_Link_Xml):

        with DB_Connection.open_conn(UserParameters.db_path) as conn:
            try:
                with closing(conn.cursor()) as cursor:
                    cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS filing_list (
                    filing_number integer PRIMARY KEY,
                    account_number integer,
                    company_name text NOT NULL,
                    cik integer NOT NULL,
                    filing_type text NOT NULL,
                    filing_date text NOT NULL,
                    document_link_html TEXT NOT NULL,
                    filing_number_link TEXT NOT NULL,
                    interactive_dash_link TEXT,
                    summary_link_xml TEXT
                    )
                    ;""")
            except ValueError as e:
                print(f"Error occurred while attempting to create filing_list table.\
                        \nAbording the program.")
                print(e)
                UserParameters.error_messages.append(e)
                return None
            else:
                print("Successfully created the table.")
                print(f"Migrating information for filing number {Filing_Number} to the SQL table.......")
                try:
                    # INSERT or IGNORE will insert a record if it does NOT duplicate an existing record.
                    with closing(conn.cursor()) as cursor:
                        cursor.execute(
                        """
                        INSERT or IGNORE INTO filing_list (
                        filing_number,
                        account_number,
                        company_name,
                        cik,
                        filing_type,
                        filing_date,
                        document_link_html,
                        filing_number_link,
                        interactive_dash_link,
                        summary_link_xml
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?) """
                        ,(
                        Filing_Number,
                        Account_Number,
                        Company_Name,
                        Company_CIK_Number,
                        Filing_Type,
                        Filing_Date,
                        Document_Link,
                        Filing_Number_Link,
                        Interactive_Data_Link,
                        Summary_Link_Xml
                         ))
                except ValueError as e:
                    print(f"Error occurred while attempting to insert values into the filing_list table.\n{e}")

        DB_Connection.close_conn()

    # Extract individual table links to financial statements, supplementary data tables, etc
    def get_table_links(self):
        dfs = []
        with DB_Connection.open_conn(UserParameters.db_path) as conn:
            try:
                for Company_CIK_Number in UserParameters.company_CIKs:
                    for Filing_Type in UserParameters.filing_types:
                        df = pd.read_sql_query(
                             """
                             SELECT filing_number, summary_link_xml
                             FROM filing_list
                             WHERE summary_link_xml IS NOT NULL
                             AND filing_type = ?
                             AND cik = ?
                             AND filing_date BETWEEN ? AND ?
                             """, con = conn , params=(Filing_Type,
                                                       Company_CIK_Number,
                                                       UserParameters.start_date,
                                                       UserParameters.end_date))
                        dfs.append(df)
                df_query2 = pd.concat(dfs)

            except ValueError as e:
                print(f"Error occurred while attempting to retrieve data from the filing_list table.")
                print(e)
                UserParameters.error_messages.append(e)
                return None

            # If the DataFrame is empty, terminate the program.
            if len(df_query2) == 0:
                error_msg ='DataFrame is empty. (Error in the get_table_links method) '
                print(error_msg)
                UserParameters.error_messages.append(error_msg)
                return None
            try:
                with closing(conn.cursor()) as cursor:
                    cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS individual_report_links (
                    filing_number integer,
                    short_name text,
                    report_url text,
                    FOREIGN KEY(filing_number) REFERENCES filing_list(filing_number),
                    UNIQUE(report_url)
                    )
                    ;""")
            except ValueError as e:
                print(f"Error occurred while attempting to create individual_report_links table.\
                        \nAbording the program.")
                print(e)
                UserParameters.error_messages.append(e)
                return None

            # Extract the tables name and its respective URL
            # Currently, I do not have a function/method to extract data from a .XML file extension.
            for filing_number, summary_link_xml in df_query2.itertuples(index = False):
                response_2 = requests.get(summary_link_xml).content
                time.sleep(0.1)
                soup_2 = BeautifulSoup(response_2, 'lxml')
                for item in soup_2.find_all('report')[:-1]:
                    if item.shortname:
                        Short_Name = item.shortname.text
                         # Remove special characters
                        Short_Name = re.sub(r"[^a-zA-Z0-9]+", ' ', Short_Name)
                        # Remove white wite space at the end of the string.
                        Short_Name = Short_Name.rstrip()
                    else:
                        print('Short name could not be retrieved.')
                        Short_Name  = None
                    # Some tables come only in the xml form.
                    if item.htmlfilename:
                        Report_Url = summary_link_xml.replace('FilingSummary.xml',
                                                              item.htmlfilename.text)
                    elif item.xmlfilename:
                        Report_Url = summary_link_xml.replace('FilingSummary.xml',
                                                              item.xmlfilename.text)
                    else:
                        print('URL to the individual report could not be retrieved.')
                        Report_Url = None
                    print(Short_Name)
                    print(Report_Url)
                    print(filing_number)
                    print('*'*50 + ' Inserting values into the table .... ' + '*'*50)
                    try:
                        with closing(conn.cursor()) as cursor:
                            cursor.execute(
                            """
                            CREATE TABLE IF NOT EXISTS individual_report_links (
                            filing_number integer,
                            short_name text,
                            report_url text,
                            FOREIGN KEY(filing_number) REFERENCES filing_list(filing_number)
                            )
                            ;""")
                            cursor.execute(
                            """
                            INSERT OR IGNORE INTO individual_report_links (
                            filing_number,
                            short_name,
                            report_url
                            ) VALUES (?, ?, ?) """,(
                            filing_number,
                            Short_Name,
                            Report_Url
                             ))
                    except ValueError as e:
                        print(f"Error occurred while attempting to insert values into \
                                the individual_report_links table.\nAbording the program.")
                        print(e)
                        UserParameters.error_messages.append(e)
                        return None

        DB_Connection.close_conn()


class Extract_Data:

    def __init__(self):
        self.df_xml = None
    # Extract table data from a .XMK
    def htm_table_extractor(self,report_url):
        # Note to self, .text is in Unicode, .content is in bytes.
        response_xml = requests.get(report_url).content
        time.sleep(0.1)
        soup_xml = BeautifulSoup(response_xml, "lxml")
        table = soup_xml.find_all('table')
        if table:
            try:
                print("Inserting table data into the DataFrame.")
                self.df_xml = pd.read_html(str(table))[0]
                self.df_xml = self.df_xml.replace({'\$':''}, regex = True)\
                                         .replace({'\)':''}, regex = True)\
                                         .replace({'\(':''}, regex = True)\
                                         .replace({'\%':''}, regex = True)\
                                         .replace({' ','', 1}, regex = True)

            except Exception as e:
                print(f'Error occurred while attempting to insert \
                        table data into the DataFrame.\n{e}')
        else:
            print(f'No table detected for {report_url}.')

    # Retreive the necessary information information to extract data from the table's URL.
    def get_tables(self):

        dfs =[]
        with DB_Connection.open_conn(UserParameters.db_path) as conn:
            for company_CIK in UserParameters.company_CIKs:
                for filing_type in UserParameters.filing_types:
                    try:
                        df = pd.read_sql_query(
                            """
                            SELECT a.filing_number,
                                   a.company_name,
                                   a.filing_type,
                                   a.filing_date,
                                   b.short_name ,
                                   b.report_url
                            FROM filing_list a
                            INNER JOIN individual_report_links b
                            ON a.filing_number = b.filing_number
                            WHERE b.report_url LIKE '%.htm%'
                            AND a.cik = ?
                            AND a.filing_type = ?
                            AND a.filing_date BETWEEN ? AND ?
                            ORDER by filing_date DESC
                            LIMIT ?
                            """, con = conn , params=(company_CIK, filing_type,
                                                      UserParameters.start_date,
                                                      UserParameters.end_date , 10))
                        dfs.append(df)
                    except ValueError as e:
                        print(f"Error occurred while attempting to retreive data \
                                from the SQL database.\nAbording the program.")
                        print(e)
                        UserParameters.error_messages.append(e)
                        return None
            if dfs:
                df_query1 = pd.concat(dfs)
            else:
                empty_df_msg = 'DataFrame is Empty. (Error in the get_tables method)'
                print(empty_df_msg)
                UserParameters.error_messages.append(empty_df_msg)
                return None

            # If the DataFrame is empty, terminate the program.
            # if len(df_query1) == 0:
            #     main.error_box('DataFrame is Empty')
            #     return None
            # else:
            #     # If maximum recursion error occurs, increase recursion limit. sys.setrecursionlimit(25000)
            #     pass

            for filing_number,\
                company_name,\
                filing_type,\
                filing_date,\
                short_name,\
                report_url in df_query1.itertuples(index = False):
                print(f'Processing {short_name} table at {report_url}.')

                if report_url.endswith('.htm'):
                    try:
                        self.htm_table_extractor(report_url)
                    except ValueError as e:
                        print(f"Could not retreive the table for filing number \
                                {filing_number} at {report_url}\n{e}")
                        break
                    else:
                        try:
                            # We want to name the table with a unique table name for easy reference.
                            table_name = filing_type + filing_date + '_' + \
                                         short_name.replace(' ','_') + '_' + str(filing_number)
                            # Remove all special characters except for '_'
                            table_name = re.sub(r"[^a-zA-Z0-9]+", '_', table_name)
                            print(f'Inserting data from the DataFrame into SQL table {table_name}')
                            # Check to see if table already exists in the database to avoid duplicate records.
                            with closing(conn.cursor()) as cursor:
                                cursor.execute(f""" SELECT count(name)
                                              FROM sqlite_master
                                              WHERE type='table' AND name= '{table_name}' """) # SQL injection vulnerability.
                                # If count is 1, then table exists
                                if cursor.fetchone()[0]==1:
                                    print(f'Table {table_name} already exists.')
                                else:
                                    # Write records that are stored in the DataFrame into a SQL server database.
                                    self.df_xml.to_sql(con = conn,
                                              name=table_name,
                                              schema='SCHEMA',
                                              index=False,
                                              if_exists='fail')

                        except ValueError as e:
                            print(f"Could not migrate the {short_name} table to the SQL database.\n{e}")
                elif report_url.endswith('.xml'):
                    print('.xml extension link detected. Unable to to process the table.\
                           \n.xml extension link support is expected to be developed in the future.')
                else:
                    print(f'Table for filing number {filing_number} could not be detected.')

        DB_Connection.close_conn()


    # Normalize the data.
    def transpose(self):
        db2_path = UserParameters.db_path.replace('.db','_transposed.db')
        with DB_Connection.open_conn(UserParameters.db_path) as conn:
            try:
                df_table_list = pd.read_sql_query(
                """
                SELECT name AS table_name
                FROM sqlite_master
                WHERE type='table'
                """, conn)
            except ValueError as e:
                print(f"Could not retrieve table list.\n{e}")
            for row in df_table_list.itertuples(index = False):
                try:
                    df_table = pd.read_sql_query(
                    """ SELECT * FROM "{}" """.format(row.table_name), con=conn)
                except ValueError as e:
                    print(f"Could not read table {table_name}.\n{e}")
                else:
                    try:
                        while row.table_name not in ['filing_list', 'individual_report_links']:
                            # Remove duplicate rows that have the same values.
                            df_table = df_table.drop_duplicates()
                            # Transpose the pandas DataFrame.
                            df_table = df_table.T
                            # Transform first rows into the header.
                            df_table.columns = df_table.iloc[0]
                            df_table = df_table[1:]
                            # Remove special characters, replace empty spaces with _
                            df_table = df_table.rename(columns=lambda x: re.sub('\W+','_',str(x)))
                            df_table.columns = df_table.columns.str.strip('_')
                            df_table.columns = df_table.columns.str.lower()
                            # Convert index of the DataFrame into a column.
                            df_table.reset_index(level=0, inplace=True)
                            # Format the date column.
                            try:
                                date_list = []
                                for item in df_table.iloc[:,0]:
                                    match = re.search('\D{3}. \d{2}, \d{4}', item)
                                    if match is not None:
                                        # .strftime removes the time stamp.
                                        date= parser.parse(match.group()).strftime("%Y-%m-%d")
                                        date_list.append(date)
                                    else:
                                        date_list.append(item)
                                df_table.rename(columns={ df_table.columns[0]: "date" }, inplace = True)
                                df_table['date'] = date_list
                                print('Successfully formatted the date.')
                            except Exception as e:
                                df_table.rename(columns={ df_table.columns[0]: "name" }, inplace = True)
                                print(e)

                            # Convert rows to numeric data types such as integers and floats.
                            df_table.replace(',','', regex=True, inplace=True)
                            df_table = df_table.apply(pd.to_numeric, errors = 'ignore')
                            # Dynamically rename duplicate rows that have the same name.
                            if any(df_table.columns.duplicated()):
                                print('Duplicate column name detected.\nRenaming the duplicate column name.  ')
                                columns_series = pd.Series(df_table.columns)
                                for dup in columns_series[columns_series.duplicated()].unique():
                                    columns_series[columns_series[columns_series == dup].index.values.tolist()] = \
                                    [dup + '.' + str(i) if i != 0 else dup for i in range(sum(columns_series == dup))]
                                df_table.columns = columns_series
                            break
                    except Exception as e:
                        print(f"Could not transpose the table.\n{e}")
                    else:
                        with DB_Connection.open_conn(db2_path) as conn2:
                            # Check to see if table already exists in the database.
                            with closing(conn2.cursor()) as cursor:
                                cursor.execute(f""" SELECT count(name)
                                              FROM sqlite_master
                                              WHERE type='table' AND name= '{row.table_name}' """) # SQL injection vulnerability.
                                # If count is 1, then table exists
                                if cursor.fetchone()[0]==1:
                                    print(f'Table {row.table_name} already exists.')
                                else:
                                    try:
                                        print(f'Connected to the {db2_path} database.')
                                        print(f'Inserting data from the DataFrame into SQL table {row.table_name}')
                                        # Write records that are stored in the DataFrame into a SQL server database.
                                        df_table.to_sql(con = conn2,
                                                        name = row.table_name,
                                                        schema ='SCHEMA',
                                                        if_exists = 'append',
                                                        index = False
                                                        )

                                    except Exception as e:
                                        print(f"Could not migrate the {row.table_name} table to the normalized SQL database.\n{e}")

        DB_Connection.close_conn()

connection1 = DB_Connection(db_name, folder_path, db_path)
connection1.create_folder()
filings1 = Filing_Links(company_CIKs, filing_types, start_date, end_date)
filings1.Get_Filing_Links()
filings1.get_table_links()
data1 = Extract_Data()
data1.get_tables()
data1.transpose()
