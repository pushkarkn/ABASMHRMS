import sqlite3

def init_db():

    conn = sqlite3.connect('hr_system.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS Companies
                 (company_id INTEGER PRIMARY KEY AUTOINCREMENT,
                  company_name TEXT NOT NULL UNIQUE)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS HR_Managers
                 (manager_id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT NOT NULL UNIQUE,
                  password TEXT NOT NULL,
                  company_id INTEGER,
                  hr_email TEXT NOT NULL,
                  otp_secret TEXT NOT NULL,
                  FOREIGN KEY (company_id) REFERENCES Companies(company_id))''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS Users
                 (user_id INTEGER PRIMARY KEY AUTOINCREMENT,   
                  username TEXT NOT NULL UNIQUE,
                  password TEXT NOT NULL,
                  company_id INTEGER,
                  user_email TEXT NOT NULL,
                  otp_secret TEXT NOT NULL,
                  FOREIGN KEY (company_id) REFERENCES Companies(company_id))''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS Employees_Requests (
                 Username TEXT NOT NULL,
                 Name TEXT NOT NULL,
                 Employee_id TEXT NOT NULL,
                 Job_title TEXT NOT NULL,
                 Leave_request_days TEXT NOT NULL,
                 from_date TEXT NOT NULL,
                 to_date TEXT NOT NULL,
                 Type_of_leave TEXT NOT NULL,
                 Reason TEXT NOT NULL,
                 main_type TEXT,
                 Appointment_from_date TEXT,
                 Appointment_to_date TEXT,
                 sick_from_date TEXT,
                 sick_to_date TEXT,
                 appointment_letter_PDF BLOB,
                 sick_letter_PDF BLOB,
                 other_reason TEXT,
                 FOREIGN KEY (Username) REFERENCES Users(username))''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS Leave_Status
             (Username TEXT NOT NULL,
              Name TEXT NOT NULL,
              Employee_id TEXT NOT NULL,
              Leave_status TEXT NOT NULL,
              from_date TEXT NOT NULL,
              to_date TEXT NOT NULL,
              leave_type TEXT NOT NULL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS Abasm_Admins
             (abasm_admin_id INTEGER PRIMARY KEY AUTOINCREMENT,
              username TEXT NOT NULL UNIQUE,
              password TEXT NOT NULL)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS SubscriptionKeys (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              key TEXT UNIQUE,
              duration INTEGER,  
              created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
              used_by INTEGER,  
              used_at DATETIME)''')
    c.execute('''CREATE TABLE IF NOT EXISTS Abasm_Admins
             (admin_id INTEGER PRIMARY KEY AUTOINCREMENT,
              username TEXT NOT NULL UNIQUE,
              password TEXT NOT NULL)''')
    
    conn.close()