from flask import Flask, redirect, request, render_template
from flask_sqlalchemy import SQLAlchemy 
from datetime import date, datetime
import os 

app = Flask( __name__    )
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)


emp_json = {
            'emp_id' : '', 
            'emp_name' :'', 
            'emp_dob' : '',
            'emp_designation' : ''
        }

class Employee(db.Model) :
    eid = db.Column( db.Integer, primary_key=True ) 
    name = db.Column( db.String(50), nullable=False)
    dob  = db.Column( db.Date, nullable=False)
    designation = db.Column( db.String(50), nullable=False)
    date_created = db.Column( db.DateTime, default= date.today())


@app.route('/', methods=['GET','POST'])
def home(logged_messages=None):
    return render_template('home.html', logged_messages=logged_messages)


@app.route('/choice', methods=['GET','POST'])
def choice():
    if request.method == 'POST' :
        c = int(request.form['choice'])
        action_page = "/"
        if c == 1 : 
            action_page = "/create"
        elif c == 2: 
            action_page = "/search"
            
    return  redirect( action_page )


@app.route('/create')
def create():
    return render_template('create.html')

@app.route('/search')
def search():
    return render_template('search.html', emp_data = emp_json,
                                        results = [],
                                        query_result = None)

@app.route('/update/<int:id>', methods=['GET','POST'])
def update(id):
    employee = Employee.query.get_or_404(id)
    if request.method == 'POST' : 
        employee.id = request.form['emp_id']
        employee.name = request.form['emp_name']
        employee.dob = datetime.strptime(request.form['emp_dob'],"%Y-%m-%d").date()
        employee.designation = request.form['emp_designation']
        db.session.commit() 
        message = f'SUCCESS : Record of employee with employee id = {id} updated successfully. '
        return render_template('home.html', logged_messages = [message])
    else : 
        return render_template('update.html', employee = employee)

@app.route('/delete/<int:id>')
def delete(id): 
    employee = Employee.query.get_or_404(id)
    db.session.delete(employee)
    db.session.commit() 
    message = f'SUCCESS : Record of employee with employee id = {id} is deleted sucessfully.'
    return render_template('home.html', logged_messages=[message])



def isEmployeeExists(id): 
    records = db.session.query(Employee).filter(Employee.eid==id).all() 
    return len(records)>0 


def addEmployee(employee): 
    emp_obj = Employee (eid = employee['emp_id'], 
                        name = employee['emp_name'], 
                        dob = datetime.strptime(employee['emp_dob'],"%Y-%m-%d").date(),
                        designation = employee['emp_designation']
                       ) 
    db.session.add(emp_obj)
    db.session.commit()            


def log_message(message): 
    with open('logged_messages.txt','a') as f : 
        f.write(message + ' ' + datetime.now().strftime("%d/%m/%Y %H:%M:%S")+'\n' )


@app.route('/add_to_db', methods=['GET', 'POST'])
def add_to_db(): 
    if request.method == 'POST' :
        is_exists = isEmployeeExists( int(request.form['emp_id']) ) 
        if is_exists : 
            message = f"ERROR : An employee with employee id =  {request.form['emp_id']} already exists ! "
        else : 
            addEmployee(request.form)
            message = f"SUCCESS : New employee details with id = {request.form['emp_id']} added to database successfully. " 
        log_message(message)
    return render_template('home.html', logged_messages=[message])    


@app.route('/search_db',methods=['GET','POST'])
def search_db():
    if request.method == 'POST' :
        query = db.session.query(Employee)
        if request.form['emp_id'] != '' : 
            query = query.filter(Employee.eid == int(request.form['emp_id']) )
        if request.form['emp_name'] != '' : 
            query = query.filter(Employee.name == request.form['emp_name'] )
        if request.form['emp_dob'] != '' : 
            query = query.filter(Employee.dob == datetime.strptime(request.form['emp_dob'],"%Y-%m-%d").date() )
        if request.form['emp_designation'] != '' : 
            query = query.filter(Employee.designation == request.form['emp_designation'])
        
        results = query.all() 

        message = f'Query successful : {len(results)} records returned as shown below.'
            
        return render_template('search.html', emp_data = request.form, results=results, query_result=message)

@app.route('/clean', methods=['GET','POST'])
def clean_database(): 
    try : 
        os.remove('database.db')
        message = f'SUCCESS : Database deleted successfully '
        
    except : 
        pass 
        
    db.create_all()   # create employee table again.

    return render_template('home.html', logged_messages=[message])

db.create_all()