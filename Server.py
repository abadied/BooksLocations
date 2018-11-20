from flask import Flask, request

app = Flask(__name__)


@app.route('/booksmap', methods=['POST'])
def get_books_data(books_filters):
    pass

def __main__():
    host = '0.0.0.0'
    port = 8080
    app.run(host=host, port=port)

if __name__ == "__main__":
    main()

