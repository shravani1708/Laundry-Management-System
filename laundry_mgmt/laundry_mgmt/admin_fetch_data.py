import pyrebase
import pandas as pd

import os
from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv('API_KEY')
AUTH_DOMAIN = os.getenv('AUTH_DOMAIN')
DATABASE_URL = os.getenv('DATABASE_URL')
PROJECT_ID = os.getenv('PROJECT_ID')
STORAGE_BUCKET = os.getenv('STORAGE_BUCKET')
MESSAGING_SENDERID = os.getenv('MESSAGING_SENDERID')
APP_ID = os.getenv('APP_ID')
MEASUREMENT_ID = os.getenv('MEASUREMENT_ID')


firebaseConfig = {
  "apiKey": API_KEY,
  "authDomain": AUTH_DOMAIN,
  "databaseURL": DATABASE_URL,
  "projectId": PROJECT_ID,
  "storageBucket": STORAGE_BUCKET,
  "messagingSenderId": MESSAGING_SENDERID,
  "appId": APP_ID,
  "measurementId": MEASUREMENT_ID
};

firebase=pyrebase.initialize_app(firebaseConfig)
auth= firebase.auth()
db=firebase.database()

def get_orderdf():
    Orders_dict = db.child("Orders").get().val()
    Orders_dict = dict(Orders_dict)
    orders = list(Orders_dict.keys()) #list of orders

    delivery_date = []
    instructions = []
    num_garm = []
    pick_date = []
    price = []
    user = []

    for order in orders:
        delivery_date.append(db.child("Orders").child(order).child('delivery_date').get().val())
        instructions.append(db.child("Orders").child(order).child('instructions').get().val())
        num_garm.append(db.child("Orders").child(order).child('num_garm').get().val())
        pick_date.append(db.child("Orders").child(order).child('pick_date').get().val())
        price.append(db.child("Orders").child(order).child('price').get().val())
        user.append(db.child("Orders").child(order).child('user').get().val())

    orders_data = {'OrderId': orders, 'Delivery_date' : delivery_date , 'Num_Garments' : num_garm, 'Instructions' : instructions, 'Pick_date' : pick_date,
                'Price' : price , 'Username' : user}
    orders_df = pd.DataFrame.from_dict(orders_data)
    return orders_df

def get_userdf():
    Users_dict = db.child("Users").get().val()
    Users_dict.pop('ADMIN')
    Users_dict = dict(Users_dict)
    users = list(Users_dict.keys()) #list of users

    address = []
    email = []
    phoneno = []

    for user in users:
        address.append(db.child("Users").child(user).child('Address').get().val())
        email.append(db.child("Users").child(user).child('Email').get().val())
        phoneno.append(db.child("Users").child(user).child('PhoneNum').get().val())

    users_data = {'Username' : users , 'Address' : address, 'Email' : email, 'PhoneNo' : phoneno,}
    users_df = pd.DataFrame.from_dict(users_data)
    return users_df