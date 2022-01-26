
-- Compare two databases and find missing tables if there are any.
ATTACH 'edgar.db' AS db1;
ATTACH 'edgar_transposed.db' AS db2;

SELECT name FROM db1.sqlite_schema
WHERE type = 'table'
EXCEPT
SELECT name FROM db2.sqlite_schema
WHERE type = 'table'

-- Inspect tables properties, such as columns and their respective data types.
pragma table_info('table_name');

-- Create a reference table view
CREATE VIEW reference_table AS
SELECT b.short_name AS 'Table Name',  a.company_name AS  'Company Name' , a.filing_number AS  'Filing Number',  a.filing_date AS 'Filing Date',  a.cik  AS  'Company CIK' , a.filing_type AS  'Filing Type',  a.table_name AS 'Full Table Name',  b.report_url AS 'Link to Table'
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

-- This is an example of combining Microsoft's income statement for the past 9 years and converting data types (if necessary). 

SELECT 
date AS 'Date',
CAST(REPLACE(revenue, ',', '') AS integer) AS 'Revenue',
CAST(REPLACE(net_income, ',', '') AS integer) AS 'Net Income',
CAST(REPLACE(income_before_income_taxes, ',', '') AS integer) AS 'Income Before Income Taxes',
CAST(REPLACE(operating_income, ',', '') AS integer) AS 'Operating Income',
CAST(REPLACE(gross_margin, ',', '') AS integer) AS 'Gross Margin',
CAST(REPLACE(research_and_development, ',', '') AS integer) AS 'Research and Development',
CAST(REPLACE(sales_and_marketing, ',', '') AS integer) AS 'Sales and Marketing'
FROM
(
SELECT date, revenue , net_income, income_before_income_taxes, operating_income, gross_margin, research_and_development, sales_and_marketing 
FROM '10_K2015_07_31_INCOME_STATEMENTS_14278151019135'
WHERE revenue IS NOT NULL
UNION
SELECT date, revenue , net_income, income_before_income_taxes, operating_income, gross_margin, research_and_development, sales_and_marketing 
FROM '10_K2016_07_28_INCOME_STATEMENTS_137845161790278'
WHERE revenue IS NOT NULL
UNION
SELECT date, revenue , net_income, income_before_income_taxes, operating_income, gross_margin, research_and_development, sales_and_marketing 
FROM '10_K2017_08_02_INCOME_STATEMENTS_137845171000067'
WHERE revenue IS NOT NULL
UNION
SELECT date, revenue , net_income, income_before_income_taxes, operating_income, gross_margin, research_and_development, sales_and_marketing 
FROM '10_K2018_08_03_INCOME_STATEMENTS_13784518990758'
WHERE revenue IS NOT NULL
UNION
SELECT date, revenue , net_income, income_before_income_taxes, operating_income, gross_margin, research_and_development, sales_and_marketing 
FROM '10_K2019_08_01_INCOME_STATEMENTS_13784519992755'
WHERE revenue IS NOT NULL
UNION
SELECT date, revenue , net_income, income_before_income_taxes, operating_income, gross_margin, research_and_development, sales_and_marketing 
FROM '10_K2020_07_30_INCOME_STATEMENTS_137845201063171'
WHERE revenue IS NOT NULL
UNION
SELECT date, revenue , net_income, income_before_income_taxes, operating_income, gross_margin, research_and_development, sales_and_marketing 
FROM '10_K2021_07_29_INCOME_STATEMENTS_137845211127769'
WHERE revenue IS NOT NULL
)
GROUP BY DATE

-- 
