from flask import Flask
from multiprocessing import Value

app = Flask(__name__)
counter = Value('1',0)

@app.route('/')
def hello():
    with counter.get_lock():
        counter.value += 1
        out = counter.value
    return '<h1> Hello World </h2>' + str(out)
if __name__=="__main__":
    app.run(debug=True)
