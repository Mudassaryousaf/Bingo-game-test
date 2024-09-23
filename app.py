from flask import Flask, render_template, request, redirect, url_for, session
import random

app = Flask(__name__)
app.secret_key = 'your_secret_key'

called_numbers = []
players = {}
bingo_numbers = list(range(1, 31))  # Bingo numbers from 1 to 30
winner = None

ADMIN_CREDENTIALS = {'username': 'Admin', 'password': 'Admin12345'}

def generate_bingo_card():
    """Generates a random bingo card with 9 numbers."""
    return random.sample(bingo_numbers, 9)

def check_winner(marked_numbers):
    """Check if the player has a winning combination (row/column)."""
    win_combinations = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Rows
        [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Columns
    ]
    for combination in win_combinations:
        if all(num in marked_numbers for num in combination):
            return True
    return False

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Admin Login
        if 'username' in request.form and 'password' in request.form:
            username = request.form['username']
            password = request.form['password']
            if username == ADMIN_CREDENTIALS['username'] and password == ADMIN_CREDENTIALS['password']:
                session['admin'] = True
                return redirect(url_for('admin'))
            else:
                return "Invalid admin credentials!"

        # Player Login
        elif 'name' in request.form and 'email' in request.form:
            name = request.form['name']
            email = request.form['email']
            if name and email:
                session['name'] = name
                session['email'] = email
                players[email] = {
                    'card': generate_bingo_card(),
                    'marked_numbers': []
                }
                return redirect(url_for('bingo'))
            else:
                return "Please enter a valid name and email!"

    return render_template('login.html')

@app.route('/bingo', methods=['GET', 'POST'])
def bingo():
    global winner
    if 'name' in session:
        email = session['email']
        player_data = players.get(email, {})
        card = player_data['card']
        marked_numbers = player_data['marked_numbers']
        is_winner = check_winner(marked_numbers)

        # Check for a winner
        if is_winner and winner is None:
            winner = session['name']
            return render_template('bingo.html', name=session['name'], card=card, numbers=called_numbers,
                                   marked_numbers=marked_numbers, is_winner=is_winner,
                                   total_players=len(players), winner=winner, game_over=True)

        return render_template('bingo.html', name=session['name'], card=card, numbers=called_numbers,
                               marked_numbers=marked_numbers, is_winner=is_winner,
                               total_players=len(players), winner=winner, game_over=False)

    return redirect(url_for('login'))

@app.route('/mark', methods=['POST'])
def mark():
    global winner
    if 'name' in session and winner is None:
        email = session['email']
        marked_numbers = request.form.getlist('marked_numbers')

        # Filter out valid marked numbers
        valid_marked_numbers = [int(num) for num in marked_numbers if num.isdigit() and int(num) in called_numbers]

        if len(valid_marked_numbers) != len(marked_numbers):
            return "Error: You can only mark numbers that have been called. Please try again."

        players[email]['marked_numbers'] = valid_marked_numbers

        # Check if the player is a winner
        if check_winner(players[email]['marked_numbers']):
            winner = session['name']
            return redirect(url_for('bingo'))

    return redirect(url_for('bingo'))

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    global called_numbers, winner
    if not session.get('admin'):
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        if 'number' in request.form and winner is None:
            number = request.form['number']
            if number and int(number) not in called_numbers:
                called_numbers.append(int(number))
        elif 'newgame' in request.form:
            # Reset the game for a new round
            called_numbers = []
            winner = None
            for player in players:
                players[player]['card'] = generate_bingo_card()
                players[player]['marked_numbers'] = []
            return redirect(url_for('admin'))

    return render_template('admin.html', called_numbers=called_numbers, 
                           total_players=len(players), winner=winner)

if __name__ == '__main__':
    app.run(debug=True)
