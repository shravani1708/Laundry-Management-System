from django.shortcuts import render, redirect
from django.shortcuts import HttpResponse
from laundry_mgmt import admin_fetch_data as admin_fn
import pyrebase
 
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

def index(request):
  return render(request,"index.html")

def signUp(request):
  order_dict = request.POST
  if(order_dict):
    order_dict = order_dict.dict()
    order_dict.pop('csrfmiddlewaretoken')
    user = order_dict['username']
    email = order_dict['email']
    password = order_dict['password']
    address = order_dict['address']
    phone = order_dict['phone']
    check = 0
    def create_user(user, email, password, address, phone):
        data = {"Address" : address, "PhoneNum": phone, "Email": email}
        try:
          auth.create_user_with_email_and_password(email=email,password=password)
          db.child("Users").child(user).set(data)
          print("Successfully added to database")
          return True
        except Exception as e:
          print(e)
        return False
        # login = auth.sign_in_with_email_and_password(email, password)
        # token_id = login['idToken']
        #auth.send_email_verification(token_id)
      
    if(order_dict['password'] == order_dict['conf-password']):
        if(len(order_dict['password']) >=6):
            if(create_user(user, email, password, address, phone)):
              return redirect("/")
        else:
          print("Weak Password")
    else:
      print("password does not match")

  return render(request, "signup.html")

def login(request):
  form_dict = request.POST
  if(form_dict):
    username = form_dict['username']
    password = form_dict['password']
    email = db.child('Users').child(username).child('Email').get().val()

    try:
      login = auth.sign_in_with_email_and_password(email, password)
      if(login):
        request.session['user'] = username
        if(username != "ADMIN"):
          return redirect("/home")
        else:
          return redirect("/admin-view")
    except Exception as e:
      print(e)
    
  return render(request, "login.html")

def home(request):
  if request.session.get('user'):
    user = request.session.get('user')
    return render(request,"homepage.html", {'user': user})
  else:
    return render(request,"error.html")

def admin_view(request):
  if request.session.get('user'):
    user = request.session.get('user')
    users_df = admin_fn.get_userdf()
    orders_df = admin_fn.get_orderdf()
    return render(request,"admin.html", {'curr_user' : user, 'users_df' : users_df.to_html(), 'orders_df' : orders_df.to_html()})
  else:
    return render(request,"error.html")

def OrderReq(request):
    if request.session.get('user'):
      user = request.session.get('user')
      # user = request.POST.get('user', False)
      # laundry_type = request.POST.get('laundry_type', False)
      # cloth_type = request.POST.get('cloth_type', False)
      # desc = request.POST.get('desc', False)
      # pick_date = request.POST.get('pick_date', False)
      # delivery_date = request.POST.get('delivery_date', False)
      order_dict = request.POST
      if(order_dict):
        order_dict = order_dict.dict()
        order_dict.pop('csrfmiddlewaretoken')
        id = None
        Orders_db = db.child("Orders").get().val()
        if(Orders_db):
          length = len(Orders_db)
          id = "T"+ str(length)
        else:
          id = "T"+str(0)
        order_dict['user'] = user
        def push_order(id, order_dict):
          try:
              db.child("Orders").child(id).update(order_dict)
              print("Successfully added to database")
          except:
              print("Failed to add to database")
        push_order(id, order_dict)
        return render(request,"placeorder.html", {'id':id}) 
      return render(request,"placeorder.html")
    else:
      return render(request, "error.html")

def track_order(request):
  if request.session.get('user'):
    user = request.session.get('user')
    form_dict = request.POST
    if(form_dict):
      id = form_dict['TID']
      Order_data = db.child("Orders").child(id).get().val()
      if(Order_data):
        return render(request, "tracking.html", {'id': id , 'num_garm': Order_data['num_garm'], 'instructions': Order_data['instructions'], 'pick_date': Order_data['pick_date'], 'delivery_date': Order_data['delivery_date'], 'price': Order_data['price'], 'user': Order_data['user'],
        'curr_user' : user})
      else:
        print("Order ID does not exist!")
        return render(request, "tracking.html", {'curr_user' : user})
    else:
      return render(request, "tracking.html", {'curr_user' : user})
  else:
    form_dict = request.POST
    user = False
    if(form_dict):
      id = form_dict['TID']
      Order_data = db.child("Orders").child(id).get().val()
      if(Order_data):
        return render(request, "tracking.html", {'id': id , 'num_garm': Order_data['num_garm'], 'instructions': Order_data['instructions'], 'pick_date': Order_data['pick_date'], 'delivery_date': Order_data['delivery_date'], 'price': Order_data['price'], 'user': Order_data['user'], 
                      'curr_user' : user})
    return render(request, "tracking.html", {'curr_user' : user})

def logout(request):
  if request.session.get('user'):
    user = request.session.get('user')
    del request.session['user']
    return redirect("/")