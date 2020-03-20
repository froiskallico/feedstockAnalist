from flask import Flask
from app import App
app = Flask(__name__)

@app.route('/')
def hello():
    return App(lista_ops=(114562)).analist()

if __name__ == "__main__":
    app.run()

