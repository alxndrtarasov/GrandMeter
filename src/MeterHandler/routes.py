from flask import request
from src import app
from src.MeterHandler.config import transaction_builder


@app.route('/meter/accounts', methods=['POST'])
def create_account():
    data = request.get_json()
    account = data["account"].lower()
    result, code = transaction_builder.create_client(account)
    return result, code
