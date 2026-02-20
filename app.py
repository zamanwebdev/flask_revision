from flask import Flask

app = Flask(__name__)

# Home Route
@app.route('/')
def home():
    return "<h1>Welcome to Flask Revision 🔥</h1>"

# About Route
@app.route('/about')
def about():
    return "<h2>This is About Page</h2>"

# Dynamic String Route
@app.route('/user/<name>')
def user(name):
    return f"<h3>Hello {name}, Welcome to Flask!</h3>"

# Dynamic Integer Route
@app.route('/number/<int:num>')
def number(num):
    return f"<h3>You entered number: {num}</h3>"

if __name__ == '__main__':
    app.run(debug=True)
