import datetime

from service.month_bill import Bill
from data.datasource import FolderBillDatasource

from flask import Flask, jsonify, render_template

server = Flask(__name__)

datasource = FolderBillDatasource(bills_dir='../bills')
bill = Bill(datasource)


@server.route('/bill')
def get_bills():
    data = bill.get_month_bill(year=2021, month=datetime.datetime.now().month, pure_bills=True)
    return jsonify(data)


@server.route('/', methods=['GET'])
def main():
    data = {'我': 10}
    return render_template('chart.html', data=data)


@server.route('/a')
def a():
    a = 'Hello World'
    return jsonify(a)


if __name__ == '__main__':
    server.run(port=8080)
