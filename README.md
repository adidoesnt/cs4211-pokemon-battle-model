# Repository for CS4211 project, modelling a simplified version of a Pokemon battle.

## Usage of the automated pcsp file generator

- The python notebook is hosted on Google Colab [here] (A gmail account is required to access it)
- Proceed to the link and follow the steps below

### Steps
- Import all the CSV files from the repository and upload them to Google Colab notebook directory
   - Importing can be done by downloading the repository as a zip file
   - It should be the current working directory
   - There should be a sample data folder present as well (if you are in the correct directory)
   - The input CSVs should be named 'trainer1.csv' or 'trainer2.csv' explicitly
- Proceed to the 'Runtime' tab and click 'Run all' or press  'CTRL + F9'
- Download the generated 'battle_simulator_multiple_pokemon_real_data.pcsp' file
- Open and run it in PAT
- NOTE:
   - We assume that the CSV file contains the exact number of rows, as there are pokemons. The program will fail if there are empty rows i.e. rows that exist but only contain null values. If this happens, delete all rowsafter the last non empty row.
   
### Additional Information
- The source code for the python code is available in the above link, as a python script, or as a python notebook. The script and notebook are for reference purposes only, please run the generator through the Google Colab link

[//]: # (These are reference links used in the body of this note and get stripped out when the markdown processor does its job. There is no need to format nicely because it shouldn't be seen. Thanks SO - http://stackoverflow.com/questions/4823468/store-comments-in-markdown-syntax)

   [here]: <https://colab.research.google.com/drive/1Pktvyl3bAeBlCwgT_OMrOHXKRHbWTama?usp=sharing>
