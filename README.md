<h1 align="center"> Jetrics :pineapple:</h1>

### Config 
The [config](Jetrics/config.py) file is used to: 
1. Set the date to bound queries.
1. Determine what projects to look at. 

### Setup
You will need to set the following environmental variables:

    SPREADSHEET_ID :: Google Sheets spreadsheet ID
    JIRA_URL :: The JIRA URL to use 
    JIRA_PW :: The JIRA password to use 
    JIRA_USER :: The JIRA username to use
   
Further you need to setup the Google Sheets API. You will need to place a credentials.json file in the root directory. 

### Running 
You can run the program by installing it first: 

    > python setup.py install

Then run the program by typing:

    > jentrics