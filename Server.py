from flask import Flask, request, render_template

app = Flask(__name__)


@app.route('/booksmap', methods=['POST'])
def get_books_data(books_filters):
    pass

@app.route('/main', methods=['GET'])
def get_main_page():
    # will render main js page
    pass

def __main__():
    host = '0.0.0.0'
    port = 8080
    app.run(host=host, port=port)

if __name__ == "__main__":
    main()

