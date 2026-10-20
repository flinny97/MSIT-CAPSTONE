"""
Start the training app on this computer.

    python app.py

Then open http://127.0.0.1:5000 in a browser. The researcher dashboard is at
http://127.0.0.1:5000/admin. Settings come from environment variables, see
.env.example.
"""

from webapp import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=app.config["PORT"], debug=app.config["DEBUG"])
