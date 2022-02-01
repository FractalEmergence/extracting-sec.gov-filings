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
    
### Running the Python file

    $ python filing_extractor.py
    
### Downlaod example database

Download links to a sample database that was generated using filing_extractor.py. 
Companies included in the database: Microsoft, Tesla and Amazon
Filing types: 10-K and 10-Q
Time range: 2015-01-26 to 2021-10-29

Download the normalized edgar_transposed.db database at https://drive.google.com/file/d/1eikVcM-LvDn7_lCgQtBaXVSttQ5flyUT/view?usp=sharing.

Download the non-processed edgar.db database at https://drive.google.com/file/d/15qNf6zR6XBr5-nXlqPTVjwGuF4tw7MLS/view?usp=sharing.
    
### Example queries

I recommend using DBeaver for data exploration in SQL, you can download DBeaver at https://dbeaver.io/.

  ```SQL
  ---------------------------------------------------------------------
  -- Compare two databases and find missing tables if there are any --
  ---------------------------------------------------------------------
  
ATTACH 'edgar.db' AS db1;
ATTACH 'edgar_transposed.db' AS db2;

SELECT name FROM db1.sqlite_schema
WHERE type = 'table'
EXCEPT
SELECT name FROM db2.sqlite_schema
WHERE type = 'table'

--------------------------------------------------------------------------------
-- Inspect tables properties, such as columns and their respective data types --
--------------------------------------------------------------------------------

pragma table_info('table_name');

-----------------------------------
-- Create a reference table view --
-----------------------------------

CREATE VIEW reference_table AS
SELECT b.short_name AS 'Table Name',  a.company_name AS  'Company Name' ,
a.filing_number AS  'Filing Number',  a.filing_date AS 'Filing Date',
a.cik  AS  'Company CIK' , a.filing_type AS  'Filing Type',
a.table_name AS 'Full Table Name',  b.report_url AS 'Link to Table'
FROM (
      SELECT a.filing_number, a.filing_date, a.company_name, a.cik, a.filing_type, b.table_name
      FROM filing_list AS a
      INNER JOIN (SELECT name AS table_name
                  FROM sqlite_master
                  WHERE type='table') AS b
      ON b.table_name LIKE '%' || a.filing_number || '%') AS a
LEFT OUTER JOIN individual_report_links AS b
ON (a.table_name LIKE '%' || REPLACE(b.short_name, ' ' , '_') || '_'||  b.filing_number|| '%')
AND a.filing_number = b.filing_number
GROUP BY a.table_name
ORDER BY 6

--------------------------------------------------------------------------------------------------------------------------------
-- This is an example of combining Microsoft's income statements for the past 9 years and converting data types (if necessary)--
--------------------------------------------------------------------------------------------------------------------------------

SELECT date AS 'Date',
       CAST(REPLACE(revenue, ',', '') AS integer) AS 'Revenue',
       CAST(REPLACE(net_income, ',', '') AS integer) AS 'Net Income',
       CAST(REPLACE(income_before_income_taxes, ',', '') AS integer) AS 'Income Before Income Taxes',
       CAST(REPLACE(operating_income, ',', '') AS integer) AS 'Operating Income',
       CAST(REPLACE(gross_margin, ',', '') AS integer) AS 'Gross Margin',
       CAST(REPLACE(research_and_development, ',', '') AS integer) AS 'Research and Development',
       CAST(REPLACE(sales_and_marketing, ',', '') AS integer) AS 'Sales and Marketing'
FROM
    (
     SELECT date, revenue , net_income, income_before_income_taxes, operating_income, gross_margin, 
            research_and_development, sales_and_marketing
     FROM '10_K2015_07_31_INCOME_STATEMENTS_14278151019135'
     UNION
     SELECT date, revenue , net_income, income_before_income_taxes, operating_income, gross_margin, 
            research_and_development, sales_and_marketing
     FROM '10_K2016_07_28_INCOME_STATEMENTS_137845161790278'
     UNION
     SELECT date, revenue , net_income, income_before_income_taxes, operating_income, gross_margin, 
            research_and_development, sales_and_marketing
     FROM '10_K2017_08_02_INCOME_STATEMENTS_137845171000067'
     UNION
     SELECT date, revenue , net_income, income_before_income_taxes, operating_income, gross_margin, 
            research_and_development, sales_and_marketing
     FROM '10_K2018_08_03_INCOME_STATEMENTS_13784518990758'
     UNION
     SELECT date, revenue , net_income, income_before_income_taxes, operating_income, gross_margin, 
            research_and_development, sales_and_marketing
     FROM '10_K2019_08_01_INCOME_STATEMENTS_13784519992755'L
     UNION
     SELECT date, revenue , net_income, income_before_income_taxes, operating_income, gross_margin, 
            research_and_development, sales_and_marketing
     FROM '10_K2020_07_30_INCOME_STATEMENTS_137845201063171'
     UNION
     SELECT date, revenue , net_income, income_before_income_taxes, operating_income, gross_margin,
            research_and_development, sales_and_marketing
     FROM '10_K2021_07_29_INCOME_STATEMENTS_137845211127769'
    )
WHERE (revenue || net_income || income_before_income_taxes || operating_income || gross_margin || research_and_development || sales_and_marketing ) IS NOT NULL
GROUP BY DATE

---------------------------------------------------------------------------------------------------------------
-- Example of calculating microsoft's EBITDA, EBITDA Margin, working capital, change in cash working capital --
---------------------------------------------------------------------------------------------------------------

SELECT c.date, 
       c.operating_income, 
       c.revenue AS 'revenue',
       d.property_and_equipment_net_of_accumulated_depreciation,
       c.depreciation_amortization_and_other,
       ROUND(CAST(c.provision_for_income_taxes AS float)/CAST(income_before_income_taxes AS float) * 100 ,2) AS 'annual_effective_tax_rate',
       c.operating_income + c.depreciation_amortization_and_other AS 'EBITDA',
       ROUND((CAST(c.operating_income AS float) + CAST(c.depreciation_amortization_and_other AS float))/CAST(c.revenue AS float),2) * 100 AS 'EBITDA_Margin ',
       c.additions_to_property_and_equipment*(-1) AS 'capital_expenditure',
       d.total_current_assets - d.total_current_liabilities AS 'working_capital',
       (d.total_current_assets - d.total_current_liabilities) - (d.total_current_assets_previous_year - d.total_current_liabilities_previous_year) AS 'change_in_working_capital',
       (d.total_current_assets-d.total_cash_cash_equivalents_and_short_term_investments) - (d.total_current_liabilities-current_portion_of_long_term_debt) AS 'non_cash_working_capital',
       ((d.total_current_assets-d.total_cash_cash_equivalents_and_short_term_investments) - (d.total_current_liabilities-current_portion_of_long_term_debt))-
       ((d.total_current_assets_previous_year -d.total_cash_cash_equivalents_and_short_term_investments_previous_year) - 
       (d.total_current_liabilities_previous_year - d.current_portion_of_long_term_debt_previous_year)) AS 'change_in_non_cash_working_capital'
FROM
(
       SELECT *,
              LEAD(depreciation_amortization_and_other) OVER(ORDER BY date DESC) AS 'depreciation_amortization_and_other_previous_year'
       FROM 
       (
           SELECT a.date, 
                  a.revenue,
                  a.operating_income, 
                  b.depreciation_amortization_and_other,
                  a.net_income, 
                  a.income_before_income_taxes,
                  a.provision_for_income_taxes,
                  b.additions_to_property_and_equipment
           FROM '10_K2021_07_29_INCOME_STATEMENTS_137845211127769' AS a
           INNER JOIN '10_K2021_07_29_CASH_FLOWS_STATEMENTS_137845211127769' AS b
           ON a.date = b.date
           WHERE (a.revenue || b.depreciation_amortization_and_other || a.operating_income) IS NOT NULL 
           UNION
           SELECT a.date, 
                  a.revenue,
                  a.operating_income, 
                  b.depreciation_amortization_and_other,
                  a.net_income,
                  a.income_before_income_taxes,
                  a.provision_for_income_taxes,
                  b.additions_to_property_and_equipment
           FROM '10_K2020_07_30_INCOME_STATEMENTS_137845201063171' AS a
           INNER JOIN '10_K2020_07_30_CASH_FLOWS_STATEMENTS_137845201063171' AS b
           ON a.date = b.date
           WHERE (a.revenue || b.depreciation_amortization_and_other || a.operating_income) IS NOT NULL
       ) GROUP BY date ) AS c
           LEFT JOIN (SELECT date,     
                             property_and_equipment_net_of_accumulated_depreciation,
                             LEAD(property_and_equipment_net_of_accumulated_depreciation) OVER(ORDER BY date DESC) AS 'property_and_equipment_net_of_accumulated_depreciation_previous_year',
                             total_current_assets, 
                             LEAD(total_current_assets) OVER(ORDER BY date DESC) AS 'total_current_assets_previous_year',
                             total_current_liabilities,
                             LEAD(total_current_liabilities) OVER(ORDER BY date DESC) AS 'total_current_liabilities_previous_year',
                             current_portion_of_long_term_debt, 
                             LEAD(current_portion_of_long_term_debt) OVER(ORDER BY date DESC) AS 'current_portion_of_long_term_debt_previous_year',
                             total_cash_cash_equivalents_and_short_term_investments,
                             LEAD(total_cash_cash_equivalents_and_short_term_investments) OVER(ORDER BY date DESC) AS 'total_cash_cash_equivalents_and_short_term_investments_previous_year'                
                      FROM (SELECT date, 
                                   property_and_equipment_net_of_accumulated_depreciation_of_51_351_and_43_197 AS 'property_and_equipment_net_of_accumulated_depreciation', 
                                   total_current_assets, total_current_liabilities, 
                                   total_cash_cash_equivalents_and_short_term_investments, 
                                   current_portion_of_long_term_debt
                            FROM '10_K2021_07_29_BALANCE_SHEETS_137845211127769' 
                            UNION
                            SELECT date, 
                                   property_and_equipment_net_of_accumulated_depreciation_of_43_197_and_35_330 AS 'property_and_equipment_net_of_accumulated_depreciation', 
                                   total_current_assets, total_current_liabilities, 
                                   total_cash_cash_equivalents_and_short_term_investments, 
                                   current_portion_of_long_term_debt
                            FROM '10_K2020_07_30_BALANCE_SHEETS_137845201063171'
                            UNION 
                            SELECT date, 
                                   property_and_equipment_net_of_accumulated_depreciation_of_35_330_and_29_223 AS 'property_and_equipment_net_of_accumulated_depreciation', 
                                   total_current_assets, total_current_liabilities, 
                                   total_cash_cash_equivalents_and_short_term_investments, 
                                   current_portion_of_long_term_debt
                            FROM '10_K2019_08_01_BALANCE_SHEETS_13784519992755' 
                            UNION 
                            SELECT date, 
                                   property_and_equipment_net_of_accumulated_depreciation_of_29_223_and_24_179 AS 'property_and_equipment_net_of_accumulated_depreciation',
                                   total_current_assets, 
                                   total_current_liabilities, 
                                   total_cash_cash_equivalents_and_short_term_investments, 
                                   current_portion_of_long_term_debt
                            FROM '10_K2018_08_03_BALANCE_SHEETS_13784518990758' )) AS d
           ON c.date = d.date
       ORDER BY d.date DESC
  ```
