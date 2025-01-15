from flask import Flask, render_template,request,redirect,session,url_for
import time
from flask.helpers import url_for
from flask_mysqldb import MySQL
from cryptography.fernet import Fernet
from datetime import timedelta
from itsdangerous import TimedJSONWebSignatureSerializer as serializer
from flask_mail import Mail,Message
import random


app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'users'

mysql = MySQL(app)
app.secret_key = "pass"
app.permanent_session_lifetime = timedelta(days=5)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'cardman8459@gmail.com'
app.config['MAIL_PASSWORD'] = 'Shreyas@8237'

mail = Mail(app)

def load_key():

    return open("secret.key").read()

@app.route('/about')
def about():
    return render_template('index.html')

@app.route('/',methods=["GET","POST"])
def home():
    if "id" in session:
        return redirect("/profile")
    else:
        return render_template('home.html')

@app.route('/register',methods=["GET","POST"])
def register():
    already = False
    if request.method=="POST":
        input_name = request.form['fullname']
        input_email = request.form['email']
        input_mobile = request.form['contact']
        input_password = request.form['password1']
        password2 = request.form['password2']
        if password2!=input_password:
            result="Password and Confirm Password should be same !"
            return render_template('register.html',result=result)
        else:
            cur = mysql.connection.cursor()
            emails = cur.execute("SELECT email FROM user_table")
            if emails>0:
                all_data = cur.fetchall()
                for data in all_data:
                    if input_email in data:
                        already = True
                        break
                if already:
                    result = "This Email ID does already exist ! Please LOGIN or Try again with different Email."
                    return render_template('register.html',result=result)

                elif len(input_password)<10:
                    key = load_key()
                    
                    encrypt_key = Fernet(key)
                    encoded_password = input_password.encode()
                    encrypted_password = encrypt_key.encrypt(encoded_password)
                    cur.execute("INSERT INTO user_table(name,email,mobile,password) values(%s,%s,%s,%s)",(input_name,input_email,input_mobile,encrypted_password))
                    mysql.connection.commit()
                    cur.close()
                    result = "User Saved, Now LOGIN"
                    time.sleep(2)
                    return render_template('register.html',result=result)
                else:
                    result = "Password Should not be greater than 10 Characters."
                    return render_template('register.html',result=result)
            else:
                key = load_key()
                
                encrypt_key = Fernet(key)
                encoded_password = input_password.encode()
                encrypted_password = encrypt_key.encrypt(encoded_password)
                if len(input_password)<10:

                    cur.execute("INSERT INTO user_table(name,email,mobile,password) values(%s,%s,%s,%s)",(input_name,input_email,input_mobile,encrypted_password))
                    mysql.connection.commit()
                    cur.close()
                    result = "User Saved, Now LOGIN"
                    time.sleep(2)
                    return render_template('register.html',result=result)
                else:
                    result = "Password Should not be greater than 10 Characters."
                    return render_template('register.html',result=result)

    else:
        return render_template('register.html')



@app.route('/login_user',methods=["POST","GET"])
def users():
    if "id" in session:
        return redirect('/profile')

    elif request.method=="POST":
        login_email = request.form['email']
        login_password = request.form['password']
        cur = mysql.connection.cursor()
        data = cur.execute("SELECT * FROM user_table")
        if data>0:
            all_data = cur.fetchall()
            cur.close()

            for validate in all_data:

                if login_email in validate:

                    validation_password = validate[4]
                    key = load_key()
                    decrypt_key = Fernet(key)

                    decrypted_password = decrypt_key.decrypt(validation_password.encode())

                    plain_password = decrypted_password.decode()
                    if login_password == plain_password:
                        session['email'] = validate[2]
                        session['id'] = validate[0]
                        session['name'] = validate[1]
                        time.sleep(2)
                        return redirect('/profile')

                    else:
                        result = "Invalid Password !"
                        time.sleep(1)
                        return render_template('login_user.html',result=result)


                elif validate[0] == data:
                        if login_email == validate[2]:
                            if login_password ==  plain_password:
                                session['email'] = validate[2]
                                session['id'] = validate[0]
                                session['name'] = validate[1]
                                time.sleep(2)
                                return redirect('/profile')
                            else:
                                result = "Invalid Password !"
                                time.sleep(1)
                                return render_template('login_user.html',result=result)
                        else:
                            result = "This Email ID is not registered !"
                            return render_template('login_user.html',result=result)





        else:
            result = "This Email ID is not registered !"
            return render_template('login_user.html',result=result)

    else:
        return render_template('login_user.html')



@app.route('/profile',methods=["POST","GET"])
def profile():
    if "id" in session:
        cur = mysql.connection.cursor()
        login_email = session.get('email')
        data = cur.execute('SELECT * FROM user_table where email = %s',(login_email,))
        if data>0:
            all_data =cur.fetchall()
            for user in all_data:

                profile_id = user[0]
                profile_name = user[1]

                profile_email = user[2]
                profile_mobile = user[3]
                profile_password = user[4]
                user_name = session.get('name')
                name = profile_name.split(" ")
                joined_name = "_".join(name)
                settings_name = profile_name.split(" ")[0]

                return render_template('profile.html',full=session.get('name'),id=profile_id,name= joined_name, email=profile_email,mobile=profile_mobile,password=profile_password,settings_name=settings_name)
    else:
        return redirect('/need_login')


@app.route('/password_manager',methods=["POST","GET"])
def password_manager():
    email = session.get('email')
    name = session.get('name')

    if "email" in session:
        if request.method=="POST":
            app_name = request.form['application']
            app_email = request.form['appemail']
            app_pass = request.form['password']
            id = session.get('id')


            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM user_table WHERE email = %s",(email,))
            cur_pass = mysql.connection.cursor()
            saved_passwords = cur_pass.execute("SELECT app_name from passwords where id=%s",(id,))
            saved_passwords_data = cur_pass.fetchall()

            data = cur.fetchall()

            for user_data in data:
                id = user_data[0]

            key = load_key()
            encrypt_key = Fernet(key)
            encoded_app_pass = app_pass.encode()
            encrypted_password =  encrypt_key.encrypt(encoded_app_pass)
            appname_splited = app_name.split(" ")
            appname = "_".join(appname_splited)
            cur.execute("INSERT INTO passwords(id,app_name,app_email,app_pass) values(%s,%s,%s,%s)",(id,appname,app_email,encrypted_password))
            mysql.connection.commit()
            result = "Password Saved!"
            cur.close()
            name = session.get('name')
            return render_template('password_manager.html',name=name.split(" ")[0],result=result)
        else:
            return render_template('password_manager.html',name=name.split(" ")[0])

    else:
        return redirect('/need_login')



@app.route('/my_passwords')
def show_all():
    if "id" in session:
        id = session.get('id')
        cur = mysql.connection.cursor()
        num_of_data=cur.execute("SELECT app_name FROM passwords where id = %s",(id,))

        if num_of_data>0 and num_of_data<=4:
            data = cur.fetchall()

            return render_template('show_passwords.html',data = data,count=0)
        elif num_of_data>4:
            count=0
            data = cur.fetchall()
            for num in data:
                count=count+10

            return render_template('show_passwords.html',data = data,count=count)
        else:
            return render_template('show_passwords.html',count=0)

    else:
        return redirect('/need_login')

@app.route('/show',methods=["POST","GET"])
def show():
    if "id" in session:
        if request.method=="POST":
            app_name = request.form['submit']
            session['appname'] = app_name

            id = session.get('id')
            cur = mysql.connection.cursor()
            num_of_passwords = cur.execute("SELECT app_email,app_pass FROM passwords where id=%s and app_name = %s",((id),(app_name)))

            if num_of_passwords > 0:
                data = cur.fetchall()
                mysql.connection.commit()
                cur.close()
                for value in data:
                    appname = app_name
                    appemail = value[0]
                    apppass = value[1]



                key = load_key()
                encrypt_key = Fernet(key)
                encrypted_pass = apppass.encode()
                decrypted_password = encrypt_key.decrypt(encrypted_pass)
                plain_password = decrypted_password.decode()






                return render_template('password_page.html',appname = appname,appemail=appemail,apppass=plain_password)
            else:
                return redirect('/my_passwords')
        else:return redirect('/my_passwords')
    else:
        return redirect('/need_login')


@app.route('/delete',methods=["GET","POST"])
def delete():
    if "id" in session:
        appname = session.get('appname')
        cur = mysql.connection.cursor()
        data = cur.execute('DELETE  FROM passwords WHERE app_name=%s',(appname,))
        mysql.connection.commit()
        cur.close()
        session.pop('appname')
        return redirect('/my_passwords')
    else:
        return redirect('/need_login')





@app.route('/delete_passwords')
def delete_all():
    if "id" in session:
        id = session.get('id')
        cur = mysql.connection.cursor()
        cur.execute('delete from passwords where id = %s ',(id,))
        mysql.connection.commit()
        cur.close()
        return render_template('show_passwords.html',count=0)
    else:
        return redirect('/need_login')

@app.route('/logout')
def logout():


    if "email" in session:
        session.pop('email')
        session.pop('name')
        session.pop('id')
        time.sleep(2)

        return render_template('login_user.html')

    else:

        return render_template('login_user.html')



@app.route('/need_login')
def need_login():
    return render_template('need_login.html')

def send_email() :
    email = session.get('reset_email')
    mytoken = token_generate(email).decode()
    
    verification_link = url_for('reset_password',token = mytoken.encode())
    msg = Message('Password Reset Request',recipients=[email],sender='noreply@encryptogmail.com')
    msg.body=f'''To Reset Your Password, Please tap on the below link. This link will expire in next 5 minutes.
                 Do not share it with any one in order to keep your account safe.

            
                http://localhost:5000{verification_link}

    If you didn't make any password reset request, please ignore this message.
    
    '''
    
    mail.send(msg)

def token_generate(email):
    serial = serializer(app.secret_key,expires_in=300)
    token = serial.dumps(email)
    return token

def verify(token):
    serial = serializer(app.secret_key)
    token_text = serial.loads(token)
    if session.get('reset_email') == token_text:
        return token_text


@app.route('/reset',methods=["GET","POST"])
def reset():
    if request.method=="POST":
        email = request.form['email']
        cur = mysql.connection.cursor()
        data = cur.execute("select email from user_table")
        
        all_data = cur.fetchall()
        print(all_data)
        for user in all_data:
            if email in user:

                session['reset_email'] = email
                
                try: 
                    send_email()
                    result = "Verification Link has been sent to your Email address. Click on the link to proceed."
                    return render_template('forgot.html',result=result)
                except:
                    return 'Is your Email Correct ? <br>Anyway, Try again, It may work'
        else:
            result = "This Email ID is not Registered. Please Register yourself if you do not have an account."
            return render_template('forgot.html',result=result)
    
    else:
        return render_template('forgot.html')



@app.route('/reset_password/<token>',methods=["GET","POST"])

def reset_password(token):
    serial = serializer(app.secret_key)
    if request.method=="POST":
        try:
            reset_email = serial.loads(token)
            print(reset_email)
            new_password = request.form['newpassword']
            key = load_key()
            encrypted_key = Fernet(key)
            encrypted_password = encrypted_key.encrypt(new_password.encode())
            cur = mysql.connection.cursor()
            cur.execute("update user_table set password=%s where email = %s",(encrypted_password,reset_email))
            mysql.connection.commit()
            session.pop('reset_email')
                      
            return redirect('/login_user')
        except:
            return render_template('corrupted.html')
            
    else:
        return render_template('reset_password.html')
    
@app.route('/login_user/changed')
def changed():
    result= "Password Updated Successfully, Now Login using New Password."
    return render_template('login_user.html',result=result)

@app.route('/generate',methods=["GET","POST"])
def generate():
    if request.method=="POST":
        count = int(request.form["count"])
        if count<=0 or count>12:
            time.sleep(1)
            return render_template('generate.html',result="I don't think this is a good password length.")
        elif count<5:
            time.sleep(1)
            return render_template('generate.html',result="Don't you think this would be very weak password ?")
        elif count>5 and count<8:
            time.sleep(1)
            return render_template('generate.html',result="Secure passwords do have length more than or equal to 8.")
        
        upper = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 
                     'I', 'J', 'K', 'M', 'N', 'O', 'p', 'Q',
                     'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y',
                     'Z']
        lower = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 
                     'i', 'j', 'k', 'm', 'n', 'o', 'p', 'q',
                     'r', 's', 't', 'u', 'v', 'w', 'x', 'y',
                     'z']
        special = ['@', '#', '$', '%', '?', '.','*']
        digits = [0,1,2,3,4,5,6,7,8,9]
        password = "" 
        for i in range(1,int((count/2))+1):
            
            if i==2:
                password = password + random.choice(upper)
            else:
                password = password + random.choice(lower)
        
        
        password = password + random.choice(special)
        if count%2==0:
            end=int(count/2)
        else:
            end = int((count/2))+1
        for j in range(1,end):
            password = password+str(random.choice(digits))
        
        final_pass_list = []
        for char in password:
            final_pass_list.append(char)
        random.shuffle(final_pass_list)
        final_pass = "".join(final_pass_list)
        print(final_pass)
        result = "This seems to be a strong and safe password. Do not share it with anyone."
        time.sleep(2)
        return render_template('generate.html',password=final_pass,result=result)
    else:
        
        return render_template('generate.html')
    

if __name__=="__main__":
    app.run(debug=True)
