from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    fruits = ["Apple", "Mango", "Banana", "Orange"]
    user_logged_in = True

    return render_template(
        "index.html",
        fruits=fruits,
        logged_in=user_logged_in
    )

if __name__ == '__main__':
    app.run(debug=True)
