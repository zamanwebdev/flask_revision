from flask import Flask

# Flask app তৈরি
app = Flask(__name__)

# Home Route
@app.route('/')
def home():
    return "<h1>Welcome Syed Zaman 🔥</h1>"
@app.route('/about')
def about():
    return "<h2>This is About Page</h2>"


# Run Server
if __name__ == '__main__':
    app.run(debug=True)
