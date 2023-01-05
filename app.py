import os
import atexit
import dotenv
from dotenv import load_dotenv

from flask import Flask
from flask import render_template,  request, url_for, flash, redirect
from flask_bootstrap import Bootstrap5

from mexc_sdk import Spot
from agents import TradingAgent
from clients import MexcClient

def to_float(x):
    try:
        return  float(x)
    except:
        return None

load_dotenv('.env')

client = MexcClient(
        Spot(
            os.environ.get('a_k'), 
            os.environ.get('s_k')
        )
    )

app = Flask(__name__)
app.secret_key = os.environ.get('s_k')
bootstrap = Bootstrap5(app)

coins = {}


@app.route("/", methods=('GET', 'POST'))
def index():

    if request.method == 'POST':
        # validate ticker
        ticker = request.form['ticker']
        summa = to_float(request.form['summa'])
        mul_buy = to_float(request.form['mul_buy'])
        mul_sell = to_float(request.form['mul_sell'])

        if not ticker:
            flash('Заполни название пары')
        elif not client.is_valid_ticker(ticker):
            flash('Данной пары нет на бирже') 
        
        #validate trading volume
        
        elif not summa:
            flash('Введите сумму торговли')
        elif client.get_balance('USDT')['free'] - sum(c['summa'] for k, c in coins.items()) - summa < 0:
                flash('Недостаточно средств')

        #validate buy multiply coeff
        
        elif not mul_buy:
            flash('не задан коэффциент для цены покупки')

        #validate buy multiply coeff
        
        elif not mul_sell:
            flash('не задан коэффциент для цены покупки')
  

        else:
            if ticker not in coins:
                coins[ticker] = {
                    'summa': summa, 
                    'agent': TradingAgent(client, ticker, summa, mul_buy, mul_sell)
                    } 
                coins[ticker]['agent'].start()

            return render_template('index.html', coins=coins)

    return render_template('index.html', coins=coins)

@app.route("/remove/<string:id>", methods = ['POST'])
def remove(id):
    coins[id]['agent'].stop_event.set()
    coins.pop(id)
    return redirect(url_for('index'))

@app.route("/settings", methods=('GET', 'POST'))
def settings():
    if request.method == 'POST':
        dotenv.set_key('.env', "a_k", request.form['a_k'])
        dotenv.set_key('.env', "s_k", request.form['s_k'])

        return redirect(url_for('index'))

    return render_template('settings.html')



def close_running_threads():
    print('Остановлено пользователем')
    for v in coins.values():
        v['agent'].stop_event.set()

    

if __name__ == '__main__':
    atexit.register(close_running_threads)
    app.run(debug=True)


        