import face_recognition
import cv2
from flask import Flask, request,render_template, redirect
# Load the known image (pre-enrolled user face)
# known_image = face_recognition.load_image_file("images/mahadev.jpg")
# known_face_encoding = face_recognition.face_encodings(known_image)[0]
import time
import mysql.connector
import pymysql
import smtplib
from email.message import EmailMessage
from datetime import datetime
# Initialize webcam
# video_capture = cv2.VideoCapture(0)

  # or cv2.CAP_MSMF

app=Flask(__name__)
#database connection
# db = mysql.connector.connect(
#     host="localhost",
#     user="root",
#     password="Mahadev@2004",  # Replace with your MySQL password
#     database="atmdata"
# )
# cursor = db.cursor(dictionary=True)

db = pymysql.connect(
    host="localhost",
    user="root",
    password="Mahadev@2004",
    database="atmdata",
    cursorclass=pymysql.cursors.DictCursor
)
cursor = db.cursor()

#email message function
def send_email_alert(to_email, subject, body):
    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = subject
    msg['From'] = 'mahadevhulsure65@gmail.com'
    msg['To'] = to_email

    # Use your Gmail or SMTP credentials
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.login('mahadevhulsure65@gmail.com', 'yfka ztjg quct srmw')  # Use app password, not regular password
    server.send_message(msg)
    server.quit()
    
#current time    
current_time = datetime.now().strftime("%d-%m-%Y %I:%M:%S %p")

# pin validation function
def validate_pin(mobile,bank_name):
    cursor.execute("SELECT * FROM account WHERE phone = %s AND bank_name = %s",(mobile, bank_name))
    account = cursor.fetchone()
    if account['pin'] is None:
        return False
    else:
        return True
 
#authentication function
def authenticate(known_face_path):
    print("Authenticating... Please look at the camera.")
    video_capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    authenticated = False
    start_time = time.time()
    
    known_image = face_recognition.load_image_file(known_face_path)
    known_face_encoding = face_recognition.face_encodings(known_image)[0]
    while True:
        ret, frame = video_capture.read()
        if not ret:
           print("failed to capture")
           break
    # else:
    #     print("capture successfully")
    # Resize for faster processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = small_frame[:, :, ::-1]  # BGR to RGB

    # Detect face(s) and get encodings
    # face_locations = face_recognition.face_locations(rgb_small_frame)
        face_locations = face_recognition.face_locations(frame)
        face_encodings = face_recognition.face_encodings(frame, face_locations)
    # face_encodings = face_recognition.face_encodings(rgb_small_frame, known_face_locations=face_locations)
    # face_encodings = face_recognition.face_encodings(rgb_small_frame)
    
        for face_encoding in face_encodings:
        # Compare with known face
           match = face_recognition.compare_faces([known_face_encoding], face_encoding)
           if match[0]:
              authenticated = True
              break

    # Show camera feed
        cv2.imshow('Authentication', frame)

        if authenticated:
          return True

        if time.time() - start_time > 10:
            return False
            # break
        if cv2.waitKey(1) & 0xFF == ord('q'):
           break

    video_capture.release()
    cv2.destroyAllWindows()

    if not authenticated:
       return False

@app.route('/', methods=['GET'])
def base():
    return render_template('index.html')

@app.route('/home',methods=['GET','POST'])
def home():
    if request.method == 'POST':
        mobile = request.form.get('mobile')
        cursor.execute("SELECT * FROM user WHERE phone = %s", (mobile,))
        user = cursor.fetchone()
        # accounts=[]
        if mobile:
            cursor.execute("SELECT bank_name, account_number FROM account WHERE phone = %s",mobile)
            accounts = cursor.fetchall()
        account_count = len(accounts)
        
        # print("accounts:" ,accounts[0]['bank_name'])
        if not user:
            message="Mobile number is not registerd with any back."
            return render_template('index.html', message=message ,user=not user)

        # print(f"User matched: {user['AccountNumber']}")

        face_path = user['face']
        # face_path="images/mahadev.jpg"
        if authenticate(face_path):
            success="Authentication Successfull"
            return render_template('home.html', mobile=mobile, success=success ,ask_pin=True,accounts=accounts)
        else:
            fail="Face authentication failed...."
            return render_template('home.html',fail=fail)

    #return render_template('home.html')
#pin entry route
@app.route('/enter_pin')
def enter_pin():
    mobile = request.args.get('mobile')
    bank = request.args.get('bank')
    if validate_pin(mobile,bank):
        return render_template("enter_pin.html", mobile=mobile, bank=bank, check=True)
    else:
        return render_template("enter_pin.html", check=False, mobile=mobile, bank=bank) 
# menu route
@app.route('/generate_pin', methods=['GET','POST'])
def generate_pin():
    if request.method == 'GET':
        mobile=request.args.get('mobile')
        bank_name=request.args.get('bank')
        return render_template("generate_pin.html", mobile=mobile, bank_name=bank_name ,check="GET")
    else:
        mobile=request.form.get('mobile')
        bank_name=request.form.get('bank')
        pin = request.form.get('pin')
        print("mobile:",mobile)
        print("bank:",bank_name)
        if not pin.isdigit() or len(pin) != 4:
            return "please enter a valid 4-digit PIN."
        
        cursor.execute("UPDATE account SET pin = %s WHERE phone= %s AND bank_name =%s", (pin,mobile,bank_name))
        db.commit()
        print("pin updated:",pin)
        return render_template("generate_pin.html", mobile=mobile, bank_name=bank_name, check="POST",pin=pin)
        
@app.route('/menu', methods=['POST'])
def atmmenu():
    mobile = request.form.get('mobile','').strip()
    pin = request.form.get('pin','').strip()
    bank_name = request.form.get('bank')
    # print("mobile:",mobile)
    # print("pin:",pin)
    cursor.execute("SELECT * FROM user WHERE phone = %s ", (mobile,))
    account=cursor.fetchone()
    # print("acc",account)
    pins=int(pin)
    
    if  not pin.isdigit():
        return "Invalid input. Please enter numeric mobile and PIN."
    
    cursor.execute("SELECT * FROM account WHERE phone = %s AND pin = %s", (mobile, pins))
    user = cursor.fetchone()
    if not user:
        invalid_pin="Invalid PIN. Please try again."
        return render_template("menu.html",invaild_pin=invalid_pin, user=False)

    return render_template("menu.html", name=account['name'], account=user['account_number'], user=True, mobile=user['phone'], bank_name=user['bank_name'],face=account['face'])
    

# transactions route 
@app.route('/balance',methods=['POST'])
def balance():
    mobile= request.form.get('mobile')
    bank_name= request.form.get('bank_name')
    print("bank_name in balance route:",bank_name)
    #print("mobile:",mobile)
    cursor.execute("SELECT * FROM user WHERE phone = %s", (mobile,))
    user = cursor.fetchone()
    #print("user:", user)
    #print("user email:",user['email'])
    cursor.execute("SELECT * FROM account WHERE bank_name = %s ", (bank_name,))
    account=cursor.fetchone()
    #print("account:",account)
    
    # if user is not None:
    #     send_email_alert(
    #         to_email='mahadevhulsure65@gmail.com',
    #         subject="Transaction Alert",
    #         body=f"Dear customer, Payment of 500000 credited to your Acc No. XXXXXX5747 on {current_time} Avl. Balance: ₹100000 "
    #     )
        
    # print("user:", user)
    return render_template("balance.html",balance=account['amount'], check="inquery", mobile=mobile) # You can pull from DB later

@app.route('/withdraw', methods=['GET', 'POST'])
def withdraw():
    if request.method == 'GET':
        mobile= request.args.get('mobile')
        bank_name=request.args.get('bank_name')
        # print("mobile in GET method:",mobile)
        return render_template("balance.html",check="withdraw_amount" ,mobile=mobile,bank_name=bank_name)
    else:
        amount= request.form.get('amount')
        mobile= request.form.get('mobile')
        bank_name= request.form.get('bank_name')
        cursor.execute("SELECT * FROM account WHERE bank_name = %s AND phone =%s", (bank_name , mobile))
        account=cursor.fetchone()
        # print("amount",account['amount'])
        if account['amount']<int(amount):
            insufficient_fund="Insufficient Amount in your Account"
            return render_template("balance.html", message=insufficient_fund, check="debited_amount")
        elif int(amount) <= 99:
            message="withdrawal amount should be greater that 100"
            return render_template("balance.html",message=message , check="debited_amount")
        else:
            cursor.execute("UPDATE account SET amount =amount - %s WHERE bank_name = %s AND phone= %s",(amount, bank_name, mobile))
            db.commit()
            cursor.execute("SELECT RIGHT(account_number , 4) AS four_digit FROM account WHERE bank_name = %s AND phone =%s",(bank_name , mobile))
            last_four_digits=cursor.fetchone()
            cursor.execute("SELECT * From user WHERE phone = %s", (mobile,))
            user=cursor.fetchone()
            print("last four digits:" , last_four_digits)
            send_email_alert(
                to_email=user['email'],
                subject="Transaction Alert",
                body=f"Dear customer, amount  {amount} debited from  your Acc No. XXXXXX{last_four_digits['four_digit']} on {current_time} Avl. Balance: {account['amount']} "
            ) 
            msg=f"{amount} withdraw successfully"
            return render_template("balance.html", amount=amount, check="debited_amount",message=msg)

@app.route('/deposit')
def deposit():
    message= "Please insert cash into the Machine"
    return render_template("balance.html", message=message , check="deposite_amount")

@app.route('/transfer',methods=['GET', 'POST'])
def transfer():
    if request.method == 'GET':
        mobile = request.args.get('mobile')
        bank_name = request.args.get('bank_name')
        return render_template("balance.html", check="GET_transfer", mobile=mobile,bank_name=bank_name)
    else:
        mobile = request.form.get('mobile_input')
        cursor.execute("SELECT bank_name FROM account WHERE phone = %s", (mobile,))
        user=cursor.fetchone()
        if not user:
            return "mobile number is not registerd"
        print("account:",user)
        
        return "Transfer page coming soon"

@app.route('/history')
def history():
    return "Transaction history page coming soon"

@app.route('/exit')
def exit():
    return redirect('/')

if __name__=='__main__':
    app.run(debug=True)
