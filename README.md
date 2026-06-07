Files : 
-TF2P.ipynb : a notebook file containing the Python code for webscraping code and model training
-main.py : the script file used for deployment on FastAPI

Summary of the project : The goal was to create a model capable of predicting the result of a match in the online FPS Team Fortress 2, based on player skill.
In the game, Players compete in teams or individually based on several match types, including capture the flag, death-match...
This project only focused on competetive mode, in which players compete in a team deathmatch style. The model predicts a binary output based on which team will win : red or blue.
Player skills were first determined using the Trueskill algorithm, which in turn utilised the results of past matches.
A simple XGBost model was then deployed on the cumulative sum of the player skill scores in each team to predict the result. 

Source : the match results were scraped from the website logs.tf, which is regularly updated with competitive match results.

Results : the final accuracy score obtained is roughly 70% as random chance plays a huge role in online shooters. This is unsuitable for further application, 
but is nevertheless promising for further study.
