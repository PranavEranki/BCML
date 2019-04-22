import pymongo
import stripe
import random
stripe.api_key = "<stripe_api_key>"
url = "<mongodb_url>"

client = pymongo.MongoClient(url);
db = client.pipedb
col = db.users


def add_user(user_id, fname, lname):
    col.insert_one({
        'uid': user_id,
        'first_name': fname,
        'last_name': lname,
        'loan_limit': set_limit(),
        'loan_taken': 0,
        'money_in': 0,
        'deadline': None,
        'coin_amt': 0,
        'public_info': {},
        'payback_amt': 0,
        'pipe_address': gen_address(),
        'secret': gen_secret()
    })

def set_limit():
    return 240 + 10 * (random.randint(1,26))

def make_charge(user, amt):
    stripe.Charge.create(
      amount=amt,
      currency="usd",
      description="$" + str(amt) + " donation from " + user,
      source="tok_visa",
      idempotency_key='en4aQEL58owJ2Fkd'
    )
    give_coin(amt)

def get_balance():
    return stripe.Balance.retrieve()

def take_loan(uid, loan_amt, deadline):
    cur = col.find_one({'uid': uid})
    loan_limit = cur['loan_limit']

add_user('peranki', 'Pranav', 'Eranki')
