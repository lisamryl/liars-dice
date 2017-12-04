# Liar's Dice

## Description

A web-app of the bidding dice game, Liar’s Dice, where a player is matched against up to 5 opponents with bidding AI. A user can chose to create a new game or return to a game in progress (games can always be accessed at the stage in which they were left). Their opponents have 3 varying attributes, calculated using the NumPy library, that impact their bidding strategy. The opponent AI is based off of a bidding algorithm built with Python and the SciPy library, that combines their attributes with the probabilities of their move options to generate a bid selection. If the player is having trouble deciding what bid to make, she can refer to a table of bidding probabilities, calculated using the SciPy library.

## Technologies Used

* Python
* Flask
* SQLAlchemy
* PostgreSQL
* Jinja
* AJAX
* JavaScript
* jQuery
* Bootstrap
* HTML 
* CSS 
* Chart.js
* NumPy
* SciPy

## How to Locally Run Liar's Dice
Liar's Dice has not yet been deployed, so here is how to run the app locally:

* Git clone into a new folder
* Run a virtual environment
* Install all dependencies (pip install -r requirement.txt)
* Make sure you have PostgreSQL running. Create a new database in psql named liarsdice.
* Create the tables by running the model.py file in Python.
* If you want sample data, populate some data by dumping the liarsdice.sql data into psql (psql liarsdice < liarsdice.sql). However, this is not necessary, as you can sign up and create a new game without populating sample data first.
* Start the server by running server.py in Python.
* Go to localhost:5000 to see the web app.

## How to Play Liar's Dice
* To play, you need to sign up. On the upper right hand side, click the Sign Up link and enter in an email and password.
* If you have never played Liar's Dice before, you should read the instructions (click the "Instructions" button on this page).
* Once you sign up, you'll be automatically logged in. To play, click the "Create New Liar's Dice Game" button. Note: if you have signed in before, you can load a saved game by clicking "Load a Saved Game".
* Select a difficulty and a number of players.
* Click the "Create New Game" button.
* The game will appear on the upper lefthand side of the screen. The human player will be in the lower lefthand side, and the current die roll will apper below the player, with red dice representing the die roll. The total number of dice among all players will be in the middle of the table.
* You will be prompted by either a user form, when it's the player's turn, or a button when action is required.
* If the game starts with the computer's turn, press the "Start Player Bidding" button when you are ready. All opponents will bid until it's your turn.
* Once it's your turn, there will be a form for bidding. You can choose a die to bid on, and select how many of that die you want to bid (only valid options will show).
* When someone challenges (or exacts) a bid, messages will pop up below the table informing the user what happened. Once the user has read the messages and is ready to start the next round, they can click the "Start Next Turn" button.
* The game ends when either the human player is out of the game, or the human player wins.

## Features on the Game Page
* If you are unsure of what to bid, you can click on the purple "Show Bidding Probabilities" button to see how likely the bids you make are to be valid bids.
* The AI opponent betting styles are based on a bidding algorithm that combines their 3 factors (bluffing, aggression, and intelligence) with the actual probabilities of their bidding options. I generated the factors using the normal distribution with the NumPy library, and calculated the probabilities of each move with the SciPy library.
* Some detail about the 3 factors:
** Players with a higher bluffing factor are more likely to bid on a die that they don't have.
** Players with high aggression are more likely to skip (or jump) a bid for a die that they do have.
** Players with high intelligence are more likely to make higher probability moves (moves that have a higher chance of being correct if challenged).
* If you want a hint about how the opponent's betting style will impact their bidding, check the "View Factors" button next to an opponent. The higher the factor shown, the more likely the player is to make bids reflecting that factor.
