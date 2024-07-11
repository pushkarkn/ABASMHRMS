import streamlit as st
import sqlite3
import hashlib
import pandas as pd
from datetime import date
import streamlit_authenticator as stauth
from io import BytesIO
import pyotp
import base64
import io
import os
import smtplib
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import secrets
import string
from datetime import datetime, timedelta


def hash_password(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_company_exists():
    conn = sqlite3.connect('hr_system.db')
    c = conn.cursor()
    c.execute("SELECT * FROM Companies")
    result = c.fetchone()
    conn.close()
    return result is not None

# def register_company(company_name):
#     conn = sqlite3.connect('hr_system.db')
#     c = conn.cursor()
#     try:
#         c.execute("INSERT INTO Companies (company_name) VALUES (?)", (company_name,))
#         company_id = c.lastrowid
#         conn.commit()
#         return company_id
#     except sqlite3.IntegrityError:
#         return None
#     finally:
#         conn.close()

def register_company_with_key(company_name, subscription_key):
    conn = sqlite3.connect('hr_system.db')
    c = conn.cursor()
    try:
        c.execute("SELECT * FROM SubscriptionKeys WHERE key = ? AND used_by IS NULL", (subscription_key,))
        key_data = c.fetchone()
        if not key_data:
            return None, "Invalid or used subscription key"
        
        c.execute("INSERT INTO Companies (company_name) VALUES (?)", (company_name,))
        company_id = c.lastrowid
        
        c.execute("UPDATE SubscriptionKeys SET used_by = ?, used_at = CURRENT_TIMESTAMP WHERE key = ?",
                  (company_id, subscription_key))
        
        conn.commit()
        return company_id, "Success"
    except sqlite3.IntegrityError:
        return None, "Company name already exists"
    finally:
        conn.close()

def get_companies():
    conn = sqlite3.connect('hr_system.db')
    c = conn.cursor()
    c.execute("SELECT company_id, company_name FROM Companies")
    companies = c.fetchall()
    conn.close()
    return companies

def get_users_by_company(company_id):
    conn = sqlite3.connect('hr_system.db')
    c = conn.cursor()
    c.execute("SELECT username FROM Users WHERE company_id = ?", (company_id,))
    users = c.fetchall()
    conn.close()
    return [user[0] for user in users]

def insert_employee_request(username, name, employee_id, job_title, leave_days, from_date, to_date, leave_type, reason, main_type,
                            Appointment_from_date=None, Appointment_to_date=None, sick_from_date=None, sick_to_date=None,
                            appointment_letter_PDF=None, sick_letter_PDF=None, other_reason=None):
    try:
        conn = sqlite3.connect('hr_system.db')
        c = conn.cursor()

        # Convert file objects to binary data if they exist
        if appointment_letter_PDF:
            appointment_letter_PDF = appointment_letter_PDF.read() if hasattr(appointment_letter_PDF, 'read') else appointment_letter_PDF
        if sick_letter_PDF:
            sick_letter_PDF = sick_letter_PDF.read() if hasattr(sick_letter_PDF, 'read') else sick_letter_PDF

        c.execute("""
                  INSERT INTO Employees_Requests (
                    Username, Name, Employee_id, Job_title, Leave_request_days, from_date, to_date, 
                    Type_of_leave, Reason, main_type, Appointment_from_date, Appointment_to_date, 
                    sick_from_date, sick_to_date, appointment_letter_PDF, sick_letter_PDF, other_reason
                  ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                  """,(username, name, employee_id, job_title, leave_days, from_date, to_date, leave_type, 
                  reason, main_type, Appointment_from_date, Appointment_to_date, sick_from_date, 
                  sick_to_date, appointment_letter_PDF, sick_letter_PDF, other_reason))

        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return False
    finally:
        conn.close()

def fetch_all_employee_requests():
    conn = sqlite3.connect('hr_system.db')
    c = conn.cursor()
    c.execute(""" SELECT *
              FROM Employees_Requests """)
    rows = c.fetchall()
    conn.close()
    return rows

def get_leave_status(employee_id, from_date, to_date, leave_type):
    conn = sqlite3.connect('hr_system.db')
    c = conn.cursor()
    c.execute("SELECT Leave_status FROM Leave_Status WHERE Employee_id = ? AND from_date = ? AND to_date = ? AND leave_type = ?", (employee_id, from_date, to_date, leave_type))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

def insert_leave_status(username, name, employee_id, leave_status, from_date, to_date, leave_type):
    conn = sqlite3.connect('hr_system.db')
    c = conn.cursor()
    c.execute("INSERT INTO Leave_Status (Username, Name, Employee_id, Leave_status, from_date, to_date, leave_type) VALUES (?, ?, ?, ?, ?, ?, ?)",
              (username, name, employee_id, leave_status, from_date, to_date, leave_type))
    conn.commit()
    conn.close()

def get_companies():
    conn = sqlite3.connect('hr_system.db')
    c = conn.cursor()
    c.execute("SELECT company_id, company_name FROM Companies")
    companies = c.fetchall()
    conn.close()
    return companies

def get_employee_username_by_hr_username(hr_username):
    conn = sqlite3.connect('hr_system.db')
    c = conn.cursor()
    c.execute("SELECT username FROM Users WHERE company_id = (SELECT company_id FROM HR_Managers WHERE username = ?)", (hr_username,))
    results = c.fetchall()
    conn.close()
    return [result[0] for result in results] if results else []

def fetch_all_employee_requests_under_me(hr_username):
    conn = sqlite3.connect('hr_system.db')
    c = conn.cursor()
    c.execute("SELECT * FROM Employees_Requests WHERE Username IN (SELECT username FROM Users WHERE company_id = (SELECT company_id FROM HR_Managers WHERE username = ?))", (hr_username,))
    rows = c.fetchall()
    conn.close()
    return rows

def get_user_email_by_username(username):
    conn = sqlite3.connect('hr_system.db')
    c = conn.cursor()
    c.execute("SELECT user_email FROM Users WHERE username = ?", (username,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

def get_hr_email_by_employee_username(employee_username):
    conn = sqlite3.connect('hr_system.db')
    c = conn.cursor()
    c.execute("""
        SELECT HR_Managers.hr_email 
        FROM HR_Managers 
        JOIN Users ON HR_Managers.company_id = Users.company_id 
        WHERE Users.username = ?
    """, (employee_username,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None


#------------------

def register_hr(username, password, company_id, email):
    conn = sqlite3.connect('hr_system.db')
    c = conn.cursor()
    try:
        c.execute("INSERT INTO HR_Managers (username, password, company_id, hr_email) VALUES (?, ?, ?, ?)",
                  (username, hash_password(password), company_id, email))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def register_user(username, password, company_id, email):
    conn = sqlite3.connect('hr_system.db')
    c = conn.cursor()
    try:
        c.execute("INSERT INTO Users (username, password, company_id, user_email) VALUES (?, ?, ?, ?)",
                  (username, hash_password(password), company_id, email))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()
def login_hr(username, password):
    conn = sqlite3.connect('hr_system.db')
    c = conn.cursor()
    c.execute("SELECT * FROM HR_Managers WHERE username = ? AND password = ?",
              (username, hash_password(password)))
    result = c.fetchone()
    conn.close()
    return result is not None

def login_user(username, password):
    conn = sqlite3.connect('hr_system.db')
    c = conn.cursor()
    c.execute("SELECT user_id, company_id FROM Users WHERE username = ? AND password = ?",
              (username, hash_password(password)))
    result = c.fetchone()
    conn.close()
    
    if result:
        user_id, company_id = result
        if is_subscription_valid(company_id):
            return True
        else:
            return "Subscription expired"
    return False

load_dotenv()
def send_otp_email(email, otp):
    
    sender_email = os.getenv('EMAIL_USER')
    sender_password = os.getenv('EMAIL_PASSWORD')
    message = MIMEMultipart("alternative")
    message["Subject"] = "Your OTP for HR Management System"
    message["From"] = sender_email
    message["To"] = email

    text = f"Your OTP is: {otp}"
    html = f"""\
    <html>
      <body>
        <p>Your OTP for HR Management System is: <strong>{otp}</strong></p>
      </body>
    </html>
    """

    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")

    message.attach(part1)
    message.attach(part2)

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, email, message.as_string())
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False
    

# def verify_otp(stored_otp, entered_otp):
#     return stored_otp == entered_otp


def user_exists(username):
    conn = sqlite3.connect('hr_system.db')
    c = conn.cursor()
    c.execute("SELECT * FROM Users WHERE username = ? UNION SELECT * FROM HR_Managers WHERE username = ?", (username, username))
    result = c.fetchone()
    conn.close()
    return result is not None

def generate_otp():
    return ''.join(random.choices('0123456789', k=6))



def verify_otp(stored_otp, entered_otp):
    return str(stored_otp) == str(entered_otp)



def register_hr(username, password, company_id, email):
    conn = sqlite3.connect('hr_system.db')
    c = conn.cursor()
    try:
        # Generate a new OTP secret for the HR manager
        otp_secret = pyotp.random_base32()
        c.execute("INSERT INTO HR_Managers (username, password, company_id, hr_email, otp_secret) VALUES (?, ?, ?, ?, ?)",
                  (username, hash_password(password), company_id, email, otp_secret))
        conn.commit()
        return True, "Success"
    except sqlite3.IntegrityError as e:
        return False, f"IntegrityError: {str(e)}"
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"
    finally:
        conn.close()

def register_user(username, password, company_id, email):
    conn = sqlite3.connect('hr_system.db')
    c = conn.cursor()
    try:
        # Generate a new OTP secret for the user
        otp_secret = pyotp.random_base32()
        c.execute("INSERT INTO Users (username, password, company_id, user_email, otp_secret) VALUES (?, ?, ?, ?, ?)",
                  (username, hash_password(password), company_id, email, otp_secret))
        conn.commit()
        return True, "Success"
    except sqlite3.IntegrityError as e:
        return False, f"IntegrityError: {str(e)}"
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"
    finally:
        conn.close()

def generate_subscription_key(days):
    key = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(16))
    conn = sqlite3.connect('hr_system.db')
    c = conn.cursor()
    c.execute("INSERT INTO SubscriptionKeys (key, duration) VALUES (?, ?)", (key, days))
    conn.commit()
    conn.close()
    return key


def is_subscription_valid(company_id):
    conn = sqlite3.connect('hr_system.db')
    c = conn.cursor()
    c.execute("""
        SELECT used_at, duration 
        FROM SubscriptionKeys 
        WHERE used_by = ? 
        ORDER BY used_at DESC 
        LIMIT 1
    """, (company_id,))
    result = c.fetchone()
    conn.close()
    
    if not result:
        return False
    
    used_at, duration = result
    expiry_date = datetime.strptime(used_at, '%Y-%m-%d %H:%M:%S') + timedelta(days=duration)
    return datetime.now() < expiry_date



def authenticate_admin(username, password):
    conn = sqlite3.connect('hr_system.db')
    c = conn.cursor()
    c.execute("SELECT * FROM Abasm_Admins WHERE username = ? AND password = ?", 
              (username, hash_password(password)))
    result = c.fetchone()
    conn.close()
    return result is not None


def create_initial_admin(username, password):
    conn = sqlite3.connect('hr_system.db')
    c = conn.cursor()
    try:
        c.execute("INSERT INTO Abasm_Admins (username, password) VALUES (?, ?)",
                  (username, hash_password(password)))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def get_all_subscriptions():
    conn = sqlite3.connect('hr_system.db')
    c = conn.cursor()
    c.execute("""
        SELECT id, key, duration, created_at, used_at
        FROM SubscriptionKeys
        ORDER BY created_at DESC
    """)
    subscriptions = c.fetchall()
    conn.close()
    return subscriptions