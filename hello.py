from flask import Flask, request, render_template, redirect
import arky.rest
import pymongo
import stripe
import random
import os
import binascii

stripe.api_key = "<stripe_api_key>"
url = "<mongodb_url>"

client = pymongo.MongoClient(url);
db = client.pipedb
col = db.users

arky.rest.use("pipe")
app = Flask(__name__)

MASTER_SECRET = "<wallet_secret_master_key>"


def gen_address(secret_key):
    secret = secret_key
    keyRing = arky.core.crypto.getKeys(secret)
    address = arky.core.crypto.getAddress(keyRing["publicKey"])
    return address
    #arky.rest.GET.api.accounts(address=address)

    #res = arky.core.sendToken(amount=1000000000, recipientId=address,secret=MASTER_SECRET)

def add_user(user_id, fname, lname, password):
    secret = gen_secret()
    col.insert_one({
        'uid': user_id,
        'first_name': fname,
        'last_name': lname,
        'password': password,
        'loan_limit': set_limit(),
        'loan_taken': 0,
        'money_in': 0,
        'deadline': None,
        'coin_amt': 0,
        'public_info': {},
        'payback_amt': 0,
        'pipe_address': str(gen_address(secret)),
        'secret': secret
    })
    print(secret)
    print(arky.rest.GET.api.accounts(address=str(gen_address(secret))))

def gen_secret():
    return (binascii.hexlify(os.urandom(24))).decode('ascii')

def set_limit():
    return 240 + 10 * (random.randint(1,26)) 

def make_charge(user, amt):
    stripe.Charge.create(
      amount=amt,
      currency="usd",
      description="$" + str(amt) + " investment from " + user,
      source="tok_visa", 
    )

def get_balance():
    return stripe.Balance.retrieve()

def take_loan(uid, loan_amt, deadline):
    cur = col.find_one({'uid': uid})
    loan_limit = cur['loan_limit']

def send_money(amnt, pipe_address):
    amnt_val = 100000000 * amnt
    print(amnt_val)
    print(pipe_address)
    transaction = arky.core.sendToken(amount=amnt_val, recipientId=pipe_address, secret=MASTER_SECRET)
    print(transaction)


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/create_account")
def create():
    return render_template("create.html")

@app.route("/login_a")
def login_a():
    return render_template("login.html")

@app.route("/lender", methods=['GET'])
def lender():
    x = col.find_one({'uid':'lender'})['coin_amt'] 
    return render_template("investor_platform.html", coin_amt=x)

@app.route("/borrower", methods=['GET', 'POST'])
def borrower():
    loan_lim = col.find_one({'uid': 'borrower'})['loan_limit']
    loan_taken = col.find_one({'uid': 'borrower'})['loan_taken']
    payback_amt = col.find_one({'uid': 'borrower'})['payback_amt']
    deadline = col.find_one({'uid': 'borrower'})['deadline']
    return render_template("loan_platform.html", loan_limit=loan_lim, loan_taken=loan_taken, due_date=deadline, payback_amt=payback_amt)



@app.route('/create_user', methods=['GET', 'POST'])
def create_user():
    if request.method == 'POST':
        user_id = request.values.get('user_id',None)
        fname = request.values.get('first_name',None)
        lname = request.values.get('last_name',None)
        password = request.values.get('password',None)
        print(user_id)
        add_user(user_id, fname, lname, password)
        return "Successfully Created"
    else:
        return "Wrong Request"

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.values.get('user_id', None)
        #password = request.values.get('password', None)
        #cur = col.find_one({'uid': user_id, 'password': password})
        print(user_id)
        if(user_id == "lender"):
            return redirect('/lender')
        else:
            return redirect('/borrower')
            
        # if(cur.count() == 0):
        #   return "Not found"
        # else:
        #   return "Found"
    else:
        return "Wrong Request"


### Loaning Platform

## TODO: Figure out deadline workflow
@app.route('/take_out_loan', methods=['GET', 'POST'])
def take_out_loan():
    if request.method == 'POST':
        print('happning')
        print(request.values.get('amnt', None))
        amnt = float(request.values.get('amnt', None))
        user_id = request.values.get('user_id', None)
        payback_amt = float(request.values.get('payback_amt', None));
        deadline = request.values.get('deadline', None);
        user = col.find_one({'uid': user_id})
        loan_limit = user['loan_limit']
        taken = user['loan_taken']
        amnt += float(taken)
        payback_amt += float(user['payback_amt'])
        if(loan_limit - int(amnt) >= 0):
            col.update_one({'uid': user_id}, {'$set': {'payback_amt': payback_amt, 'loan_taken': amnt, 'deadline': deadline}})
            return redirect('/borrower')
        else:
            return "Tried to take out more than limit"
    else:
        return "Wrong Request"

@app.route('/loan_limit', methods=['POST'])
def loan_limit():
    if request.method == 'POST':
        user_id = request.values.get('user_id', None)
        user = col.find_one({'uid': user_id})
        return str(user['loan_limit'])
    else:
        return "Wrong Request"


### Investment Platform

@app.route('/investment_data_money', methods=['POST'])
def money_in():
    if request.method == 'POST':
        user_id = request.values.get('user_id', None)
        user = col.find_one({'uid': user_id})
        return str(user['money_in'])
    else:
        return "Wrong Request"

@app.route('/investment_data', methods=['POST'])
def coin_amnt():
    if request.method == 'POST':
        user_id = request.values.get('user_id', None)
        user = col.find_one({'uid': user_id})
        return str(user['coin_amnt'])
    else:
        return "Wrong Request"

# 
@app.route('/make_investment', methods=['POST'])
def make_investment():
    if request.method == 'POST':
        user_id = request.values.get('user_id', None)
        amnt = request.values.get('amnt', None)

        user = col.find_one({'uid': user_id})
        make_charge(user["first_name"], int(amnt)*100)
        send_money(int(amnt), user['pipe_address'])
        cur_coin_amt = int(user['coin_amt'])
        amt = str(int(amnt) + cur_coin_amt)

        col.update_one({'uid': user_id}, {'$set': {'coin_amt': amt}})

        return redirect('/lender')
    else:
        return "Wrong Request"
