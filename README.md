## Extract filings from Sec.Gov 

filing_extractor.py allows the user to extract tables in bulk from Sec.Gov filings and store the extracted tables in a SQLite database for quick and easy access, furthermore it creates a separate SQL normalized database which can be used to create time-series graphs and allows for further processing in SQL. 

Before running filing_extractor.py,  modify the list parameters. You can extract multiple filing types for multiple companies at the same time. 

- You must first find the company's CIK number which you can find at https://www.sec.gov/edgar/searchedgar/companysearch.html. Once you find the company’s CIK number, modify the filing_extractor.py file and place the CIK number in the company_CIKs list, for example company_CIKs = [‘789019’, '1018724'],  here the CIK numbers belong to Microsoft and Amazon respectively. 

- Secondly, enter the type of filings that you want to use, if you want to use annual reports  put  ‘10-K’ in filing_types, similarly if you want tables from the quarterly report use ‘10-Q’, for example filing_types = ['10-k','10-q'].

- Thirdly, select the date range for the filings by modifying start_date and end_date using the 'YYYY-MM-DD' format. For example start_date = '2021-06-01' and end_date = '2022-12-30'.
 
- Finally, enter the location for where you want to save the database. By default, the database will be saved in the following directory folder_path = r"C:\sqlite\db".

### Setup in Windows 

    $ pip install virtualenv
    $ cd C:\sqlite\db
    $ virtualenv venv
    $ source venv/bin/activate
    $ venv\Scripts\activate.bat
    $ pip install -r requirements.txt
