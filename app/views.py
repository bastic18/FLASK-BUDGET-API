from app import app,mysql
from flask import render_template, request, redirect, url_for, jsonify,make_response,abort,session
from .form import LoginForm

from flask_mysqldb import MySQL,MySQLdb
from datetime import datetime,timedelta
import MySQLdb.cursors
from decimal import Decimal
import json
import jwt
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash




########################>>>>>>>>>>> JWT AUTHENTICATION >>>>>>>>>>>>>>>>>>>>>>>>

# token_required check to see if the token provided in the authorization header is validated to true
# decorated_function returns different versions, if authorization is true then a decoded JWT is passed to the routes.
# the data reuturn by this function is a payload that contains user data

#Blacklist is a set that contains jwt token after a user decides to logout
#The set allows for order 1 retrieval of data when checking if the set contains a particular token 
blacklist=set() 

def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        token = request.headers
        if not token['Authorization']:
            return jsonify({'message':'Token is missing', "code":-1}), 401

        token=token['Authorization'].split(" ")
        if token[1] in blacklist:                         #checks if token in blacklist
            return jsonify({'Message':'Please Login Again'}), 200
        try:
            #decodes the jwt token into the payload
            postdata = jwt.decode(token[1],app.config['SECRET_KEY'])  #variable postdata contains the current authenticated user payload 
        except:
            return jsonify({'message':'Token is invalid',"code":-1}),401
        return f(postdata,*args, **kwargs)
    return decorated_function


#This decorator function checks if the current user is a admin.
#This function is used on routes where only admin priviledges are required. 
def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        cur = mysql.connection.cursor()
        token = None
        token = request.headers
        if not token['Authorization']:
            return jsonify({'message':'Token is missing', "code":-1}), 401
        try:
            token=token['Authorization'].split(" ")
            data = jwt.decode(token[1], app.config['SECRET_KEY'])
            cur.execute("select id, email, admin from user where email=%s",(data['email'],))   #get user details using the jwt payload
            current_user = cur.fetchone()
            cur.close()
            admin=current_user['admin']
            if not admin:                   #checks if the current user is an admin
                return jsonify({'Message':'User Not Authorized (Admin Priviledges Required)'}), 401
        except Exception as e:
            return jsonify({'Message':'User Not Found'}), 401
        return f(*args,*kwargs)
    return decorated


#####>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> HELPER FUNCTIONS

# This function returns a user details.
# All user details is returned including all budget details, all expense details and all purchase details 
def all_users(users):
    all_users=[]
    cur = mysql.connection.cursor()
    for user in users:
        user_id=user['id']
        get_user={"id":user_id, "name":user["name"],"email":user["email"]}
        
        cur.execute("select budget.id,budget.name, budget.income, budget.date as date, create_budget.user_id,create_budget.budget_id, create_budget.date as date1 from budget join create_budget on budget.id=create_budget.budget_id where create_budget.user_id=%s",(user_id,))
        user_budgets=list(cur.fetchall())
        budget_list=[]
        for budget in user_budgets:         #get a list of budget details for a user
            budget_id= budget['id']

            get_budget={'id':budget['id'], 'name':budget['name'],'income':budget['income'], 'date':budget['date']}
            
            cur.execute("select expense.id,expense.name, expense.allocation, expense.date as date, create_expense.budget_id,create_expense.expense_id, create_expense.date as date1 from expense join create_expense on expense.id=create_expense.expense_id where create_expense.budget_id=%s",(budget_id,))
            budgets_expenses=list(cur.fetchall())
            expense_list=[]
            for expense in budgets_expenses:            #get a expense details for a budget
                get_expense={'id':expense['id'], 'name':expense['name'],'allocation':expense['allocation'], 'date':expense['date']}
                cur.execute("select purchase.id,purchase.name, purchase.cost, purchase.date as date, create_purchase.expense_id,create_purchase.purchase_id, create_purchase.date as date1 from purchase join create_purchase on purchase.id=create_purchase.purchase_id where create_purchase.expense_id=%s",(expense['id'],))
                expenses_purchase=list(cur.fetchall())
                purchase_list=[]
                for purchase in expenses_purchase:      #get purchases for a expense
                    get_purchase={'id':purchase['id'], 'name':purchase['name'],'cost':purchase['cost'], 'date':purchase['date']}
                    purchase_list.append(get_purchase)
                get_expense["purchases"]=purchase_list
                expense_list.append(get_expense)
            get_budget["expenses"]=expense_list
            budget_list.append(get_budget)
        get_user["budget"]=budget_list
        all_users.append(get_user)
    return all_users



# This function return all the budget details of a unique budget
# including all expense and purchase details are return for unique budget
def user_budget(budget):
    budget_list=[]
    cur = mysql.connection.cursor()
    cur.execute('select * from budget where id=%s',(budget,))
    budget= list(cur.fetchall())
    cur.close()
    
    budget=budget[0]
    get_budget={'id':budget['id'], 'name':budget['name'],'income':budget['income'], 'date':budget['date']}
    cur = mysql.connection.cursor()
    cur.execute("select expense.id,expense.name, expense.allocation, expense.date as date, create_expense.budget_id,create_expense.expense_id, create_expense.date as date1 from expense join create_expense on expense.id=create_expense.expense_id where budget_id=%s",(budget['id'],))
    budgets_expenses=list(cur.fetchall())
    expense_list=[]
    
    for expense in budgets_expenses:     #get expense belonging to a budget
        get_expense={'id':expense['id'], 'name':expense['name'],'allocation':expense['allocation'], 'date':expense['date']}
        cur.execute("select purchase.id,purchase.name, purchase.cost, purchase.date as date, create_purchase.expense_id,create_purchase.purchase_id, create_purchase.date as date1 from purchase join create_purchase on purchase.id=create_purchase.purchase_id where create_purchase.expense_id=%s",(expense['id'],))
        expenses_purchase=list(cur.fetchall())
        purchase_list=[]
        for purchase in expenses_purchase:          #get purchases belonging to a expense
            
            get_purchase={'id':purchase['id'], 'name':purchase['name'],'cost':purchase['cost'], 'date':purchase['date']}
            purchase_list.append(get_purchase)
        get_expense["purchases"]=purchase_list
        expense_list.append(get_expense)
        
    get_budget["expenses"]=expense_list
    budget_list.append(get_budget)

    return budget_list



#Given a expense id, a list of purchases associated with the unique expense is returned
def user_expense(expense):
    expense_list=[]
    cur = mysql.connection.cursor()
    cur.execute('select * from expense where id=%s',(expense,))
    expense= list(cur.fetchall())
    cur.close()
    
    expense=expense[0]
    get_expense={'id':expense['id'], 'name':expense['name'],'allocation':expense['allocation'], 'date':expense['date']}
    cur = mysql.connection.cursor()
    cur.execute("select purchase.id,purchase.name, purchase.cost, purchase.date as date, create_purchase.expense_id,create_purchase.purchase_id, create_purchase.date as date1 from purchase join create_purchase on purchase.id=create_purchase.purchase_id where create_purchase.expense_id=%s",(expense['id'],))
    expenses_purchase=list(cur.fetchall())
    purchase_list=[]
    for purchase in expenses_purchase:              #get purchases for a expense
        
        get_purchase={'id':purchase['id'], 'name':purchase['name'],'cost':purchase['cost'], 'date':purchase['date']}
        purchase_list.append(get_purchase)
    get_expense["purchases"]=purchase_list
    expense_list.append(get_expense)
    return expense_list


#checks if a particular user exist in the database, and return a boolean with said user details
#The function accepts a primary key which is the user id
def check_user_exist(userId):
    cur = mysql.connection.cursor()
    cur.callproc("GETUSER",[userId,])
    user_data= list(cur.fetchall())
    cur.close()
    if user_data==[]:
        return True, user_data
    return False, user_data

#checks if a particular budget exist, the argument is the primary key which is the budget id 
# returns a boolean and the particular budget details 
def check_budget_exist(bid):
    cur = mysql.connection.cursor()
    cur.callproc("GETBUDGET",[bid,])
    budget= list(cur.fetchall())
    cur.close()
    if budget==[]:
        return True, budget
    return False, budget

#checks if a particular expense exist, function takes a expense id 
#returns a boolean and expense details 
def check_expense_exist(eid):
    cur = mysql.connection.cursor()
    cur.callproc("GETEXPENSE",[eid,])
    expense= list(cur.fetchall())
    cur.close()
    if expense==[]:
        return True, expense
    return False, expense

#checks if a particular purchase exist, function takes a purchase id 
#returns a boolean and expense details 
def check_purchase_exist(pid):
    cur = mysql.connection.cursor()
    cur.callproc("GETPURCHASE",[pid,])
    purchase= list(cur.fetchall())
    cur.close()
    if purchase==[]:
        return True, purchase
    return False, purchase



####>>>>>>>>>>>>>>>>>>>>>> RESTFUL API >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

#################################  LOGIN    ###################################

# Login route upon sucessfull authetication, a json object is returned 
# The json object contain message, code and the JWT token that is generated
@app.route('/login', methods=['POST'])
def login():
    auth = request.get_json()
    if not auth or not auth['email'] or not auth['password']:   #checks if email and password is provided in the body of the request  
        return make_response('Could not verify', 401)
    cur = mysql.connection.cursor()   # initialised mysl connection 
    cur.execute('Select* from user where email=%s',(auth['email'],))
    user=list(cur.fetchall())
    user=user[0]
    if not user:                #if user doesnt exist notify the client wi
        return make_response('User verification failed', 401)
    if check_password_hash(user['password'],auth['password']):
        # jwt token is generated using email, password and admin as payload with a time delta
        token = jwt.encode({"email" : user["email"], 'password':user['password'], 'admin':user['admin'] ,'exp' : datetime.utcnow() + timedelta(minutes=60)}, app.config['SECRET_KEY'])
        session['user']=user["email"]
        jwt_token=token.decode("UTF-8")
        return jsonify({"message": "Successfully logged in","code": 0,'jwt' : jwt_token})
    return make_response('Could not verify', 401)


#Logout user clears the session containing the user 
@app.route('/logout', methods=["GET"])
@token_required
def logout(postdata):
    if 'user' in session:
        session.pop('user',None)
    session.clear()                     #clears session containg the user
    token=request.headers['Authorization'].split(" ")
    blacklist.add(token[1])                #blacklist
    return jsonify({"message": "Successfully logged out","code": 0}),200



##########################    CRUD USER  ########################################################


#This route only accessible  to admin
#returns a list of all users that is not a admin 
@app.route('/users', methods=['GET'])
@token_required
@admin_required
def getUsers(postdata):
    cur = mysql.connection.cursor()
    # if postdata['admin']==1:            #checks if the current user is an admin
        
    cur.execute("select user.id,user.name,user.email from user where admin='0'") #get all users that is not an admin
    users= list(cur.fetchall())
    results= all_users(users)           #get user details including budget, expenses and purchases
    #a json object with a success message and all users is sent to the client
    return jsonify({'message':'Successfully returned users','code':0,"users":results}),200   
    # else:
    #      #a json object with erroor code and message is sent to the client if the current user not an admin
    #     return jsonify({'message':'Unauthorized User','code':-1}),401  


#This route allows for a new user to be created 
@app.route('/users', methods=['POST'])
def createUser():
    #checks if all the required key,value pairs are provided in the body of the request to create the user
    if not request.json or not 'name' in request.json or not 'email' in request.json or not 'password' in request.json:
        new_user={'message':'Could not create a new user. Ensure a valid email, name and password is provided','code':-1}
        return jsonify(new_user), 400
    cur = mysql.connection.cursor()
    #retreive the last id number of the user table
    cur.execute('select id,name,email from  user ORDER BY id DESC LIMIT 1')
    last_record=cur.fetchone()
    cur.close()
    if last_record is None:
        last_record = 1
    else:
        last_record = last_record['id'] + 1     #the created user id number
    data=request.get_json()
    hashed_password=generate_password_hash(data['password'], method='sha256')
    cur = mysql.connection.cursor()
    sql = "INSERT INTO user (id,name, email, password) VALUES (%s, %s, %s, %s)"
    val = (last_record, data['name'], data['email'], hashed_password)
    cur.execute(sql, val)
    mysql.connection.commit()
    #generate a jwt token for the newly created user
    token = jwt.encode({"email" : data["email"], 'password':hashed_password, 'admin': 0, 'exp' : datetime.utcnow() + timedelta(minutes=30)}, app.config['SECRET_KEY'])
    jwt_token=token.decode("UTF-8")
    cur.execute('select id,name,email from user where id=%s',(last_record,))
    user= list(cur.fetchall())
    user= all_users(user)       
    #return created user details, success message and code and the JWT token
    return jsonify({'message':'Successfully created user','code':0, 'user':user[0],'jwt' : jwt_token}), 200  



#This route retrieve a unique user, when a user id is provided 
@app.route('/users/<userId>', methods=['GET'])
@token_required
def getUser(postdata,userId):
    cur = mysql.connection.cursor()
    check, user_data=check_user_exist(userId)   #check if the user exist in the database
    if check==True:
        return jsonify({'message':'Could not find that particular user','code':-1, }),400  #notify the client of the error
    if postdata["email"]==user_data[0]["email"] or postdata["admin"]==1:
        user= all_users(user_data)              #get user details including budget, expenses and purchases
        return jsonify({'message':'Successfully returned user','code':0, 'user':user[0]}),200   #notify client of the success and return user details
    return jsonify({'message':'Unauthorized user','code':-1 }),401      #notify client of unauthorized access
    



#update a specific user details 
@app.route('/users/<userId>', methods=['PUT'])
@token_required
def updateUser(postdata,userId):
    data=request.get_json()
    cur = mysql.connection.cursor()
    check, user_data=check_user_exist(userId)   #check if user exist
    if check==True:
        return jsonify({'message':'Could not find that particular user','code':-1, }),400
    #checks if the current user is updating his/her own user details or the user is admin
    if postdata["email"]==user_data[0]["email"] or postdata["admin"]==1:
        if not 'name' in request.json:
            name=user_data[0]['name']
        else:
            name=data['name']
        if not 'income' in request.json:
            email=user_data[0]['email']
        else:
            email=data['email']
        if not 'password'in request.json:
            password=user_data[0]['password']
        else:
            password=generate_password_hash(data['password'], method='sha256')
        cur.execute('UPDATE user set name=%s,email=%s, password=%s where id=%s',(name,email,password,userId,))
        mysql.connection.commit()
        cur = mysql.connection.cursor()
        cur.execute('select id,name,email from user where id=%s',(userId,))
        user= list(cur.fetchall())
        user= all_users(user)           #get user details including budget, expenses and purchases
        user=user[0]
        user={'message':'Successfully updated user','code':0, 'user':user}
        return jsonify(user),200    #return a specific user and all the details including budgets, expenses and purchases
    if postdata["email"]!=user_data[0]["email"]:
        return jsonify({'message':'Unauthorized user','code':-1 }),401             #notify client of unauthorized access

    
    
#delete a particular user
@app.route('/users/<userId>', methods=["DELETE"])
@token_required
def deleteUser(postdata,userId):
    cur = mysql.connection.cursor()
    check, user_data=check_user_exist(userId)   #checks if user exist
    if check==True:
        return jsonify({'message':'Could not find that particular user','code':-1, }),400
    #only a user can delete his/her self or an admin
    if postdata["email"]==user_data[0]["email"] or postdata["admin"]==1: 
        cur.execute('DELETE from user where id=%s',(userId,))
        mysql.connection.commit()
        return jsonify({'message':'User deleted', 'code':0}), 200
    user={'message':'Unauthorized user','code':-1 }
    return jsonify(user),401
    




##########################budget

#Returns all the budgets details of a specified user
@app.route('/users/<userId>/budgets', methods=['GET'])
@token_required
def getMyBudgets(postdata,userId):
    cur = mysql.connection.cursor()
    check, user_data=check_user_exist(userId)   #check if user exist
    if check==True:
        return jsonify({'message':'Could not find that particular user','code':-1, }),400
    #checks if the user is authorized or a admin    
    if postdata["email"]==user_data[0]["email"] or postdata["admin"]==1:
        cur.execute("select budget.id,budget.name, budget.income, budget.date as date, create_budget.user_id,create_budget.budget_id, create_budget.date as date1 from budget join create_budget on budget.id=create_budget.budget_id where create_budget.user_id=%s",(userId,))
        user_budgets=list(cur.fetchall())
        cur.close()
        user_budgets= all_users(user_data)  #get user details including budget, expenses and purchases
        return jsonify({'message':'Successfully returned budgets', 'code':0, 'budgets':user_budgets[0]['budget']}), 200
    return jsonify({'message':'Unauthorized user','code':-1 }),401


#Create a budget for a particular user
@app.route('/users/<userId>/budgets', methods=['POST'])
@token_required
def createBudget(postdata,userId):
    cur = mysql.connection.cursor()
    check, user_data=check_user_exist(userId)
    if check==True:
        return jsonify({'message':'Could not find that particular user','code':-1, }),400
    #esnure all the require values are provided in the post request body
    if not request.json or not 'name' in request.json or not 'income' in request.json :
        return jsonify({'message':'Could not create a new budget. Ensure a valid name and income is provided','code':-1}), 400
    #checks if the user is authorized or a admin
    if postdata["email"]==user_data[0]["email"]  or postdata["admin"]==1:
        cur.execute('select id,name,income,date from  budget ORDER BY id DESC LIMIT 1')
        last_record=cur.fetchone()
        cur.close()
        if last_record is None:
            last_record = 1
        else:
            last_record = last_record['id'] + 1
        data=request.get_json()
        cur = mysql.connection.cursor()
        sql = "INSERT INTO budget (id,name, income, date) VALUES (%s, %s, %s, %s)"
        val = (last_record, data['name'], data['income'],  datetime.now())
        cur.execute(sql, val)
        mysql.connection.commit()

        ####insert into relationship
        cur = mysql.connection.cursor()
        sql = "INSERT INTO create_budget (user_id,budget_id, date) VALUES (%s, %s, %s)"
        val = (userId, last_record,   datetime.now())
        cur.execute(sql, val)
        mysql.connection.commit()
    
        user_budgets= user_budget(last_record)      #get all the details of a particular budget
        return jsonify({'message':'Successfully created budget', 'code':0,"budget":user_budgets}), 200
    return jsonify({'message':'Unauthorized user','code':-1 }),401





######################################unique budgets

#Return a given budget and all its details
def budget_query(bid):
    cur = mysql.connection.cursor()
    cur.callproc("GETBUDGET_DETAILS",[bid])
    budget_details= list(cur.fetchall())
    cur.close()
    return budget_details[0]


#Return a specified budget details when a primary key is provided
@app.route('/budgets/<budgetId>', methods=['GET'])
@token_required
def getBudget(postdata,budgetId):
    cur = mysql.connection.cursor()
    check, budget =check_budget_exist(budgetId)   #check if a budget exist
    if check==True:
        return jsonify({'message':'Could not find the required budget','code':-1 }),400
    user_details= budget_query(budgetId)    #get the specified budget and user details 
    if postdata["email"]==user_details["email"] or postdata["admin"]==1:
        budget=user_budget(budgetId)            #get all the details of a particular budget
        return jsonify({'message':'Successfully returned budgets', 'code':0, 'budget':budget[0]}), 200
    return jsonify({'message':'Unauthorized user','code':-1, }),401

#Update a specific budget
@app.route('/budgets/<budgetId>', methods=['PUT'])
@token_required
def updateBudget(postdata,budgetId):
    data=request.get_json()  #get data from the post request body
    cur = mysql.connection.cursor()
    check, budget =check_budget_exist(budgetId)  #checks if the budget exist
    if check==True:
        return jsonify({'message':'Could not find the required budget','code':-1 }),400
    user_details= budget_query(budgetId)   #get the specified budget and user details
     #checks if the user is authorized or a admin
    if postdata["email"]==user_details["email"] or postdata["admin"]==1:
        if not 'name' in request.json:
            name=budget[0]['name']
        else:
            name=data['name']
        if not 'income' in request.json:
            income=budget[0]['income']
        else:
            income=data['income']
        
        cur.execute('UPDATE budget set name=%s,income=%s where id=%s',(name,income,budgetId,))
        mysql.connection.commit()
        budget=user_budget(budgetId)            #get all the details of a particular budget
        return jsonify({'message':'Successfully updated budget', 'code':0, 'budget':budget[0]}), 200
    return jsonify({'message':'Unauthorized user','code':-1 }),401

#Deletes a specified budget given the id number
@app.route('/budgets/<budgetId>', methods=['DELETE'])
@token_required
def deleteBudget(postdata,budgetId):
    cur = mysql.connection.cursor()
    check, budget =check_budget_exist(budgetId)  #checks if a budget exist
    if check==True:
        return jsonify({'message':'Could not find the required budget','code':-1 }),400
    user_details= budget_query(budgetId)            #get the specified budget and user details
    #checks if the user is authorized or a admin
    if postdata["email"]==user_details["email"] or postdata["admin"]==1:
        cur.execute('DELETE from budget where id=%s',(budgetId,))
        mysql.connection.commit()
        return jsonify({'message':'Budget deleted', 'code':0}), 200
    return jsonify({'message':'Unauthorized user','code':-1 }),401


#########################budget and expenses

#Returns the expenses a particular budget given the budget id number
@app.route('/budgets/<budgetId>/expenses', methods=['GET'])
@token_required
def getBudgetExpenses(postdata,budgetId):
    cur = mysql.connection.cursor()
    check, budget =check_budget_exist(budgetId)
    if check==True:
        return jsonify({'message':'Could not find the required budget','code':-1 }),400
    user_details= budget_query(budgetId)        #get the specified budget and user details
    #checks if current user accessing this route is authorized or is an admin
    if postdata["email"]==user_details["email"] or postdata["admin"]==1:
            
        cur.execute("select expense.id,expense.name, expense.allocation, expense.date as date, create_expense.budget_id,create_expense.expense_id, create_expense.date as date1 from expense join create_expense on expense.id=create_expense.expense_id where create_expense.budget_id=%s",(budgetId,))
        budgets_expenses=list(cur.fetchall())
        cur.close()
        expenses=user_budget(budgetId)      #get all the details of a particular budget including expenses
        return jsonify({'message':'Successfully returned expenses', 'code':0, 'expenses':expenses[0]['expenses']}), 200
    return jsonify({'message':'Unauthorized user','code':-1 }),401
 
#create a new expense for budget given the budget id number
@app.route('/budgets/<budgetId>/expenses', methods=['POST'])
@token_required
def createExpense(postdata,budgetId):
    #esnure all the require values are provided in the post request body
    if not request.json or not 'name' in request.json or not 'allocation' in request.json :
        return jsonify({'message':'Could not create a new expense. Ensure a valid name and allocation is provided','code':-1}), 400
    cur = mysql.connection.cursor()
    check, budget =check_budget_exist(budgetId)
    if check==True:
        return jsonify({'message':'Could not find the required budget','code':-1 }),400
    user_details= budget_query(budgetId)            #get the specified budget and user details
    #checks if current user accessing this route is authorized or is an admin
    if postdata["email"]==user_details["email"] or postdata["admin"]==1:
        
        cur = mysql.connection.cursor()
        cur.execute('select id,name,allocation,date from  expense ORDER BY id DESC LIMIT 1')
        last_record=cur.fetchone()
        cur.close()
        if last_record is None:
            last_record = 1
        else:
            last_record = last_record['id'] + 1
        data=request.get_json()
        cur = mysql.connection.cursor()
        sql = "INSERT INTO expense (id,name, allocation, date) VALUES (%s, %s, %s, %s)"
        val = (last_record, data['name'], data['allocation'],  datetime.now())
        cur.execute(sql, val)
        mysql.connection.commit()

        ####insert into relationship
        cur = mysql.connection.cursor()
        sql = "INSERT INTO create_expense (budget_id,expense_id, date) VALUES (%s, %s, %s)"
        val = (budgetId, last_record, datetime.now())
        cur.execute(sql, val)
        mysql.connection.commit()
        expenses=user_budget(budgetId)              #get all the details of a particular budget including expenses
        return jsonify({'message':'Successfully created expense', 'code':0,'expenses':expenses[0]['expenses']}), 200
    
    return jsonify({'message':'Unauthorized user','code':-1 }),401
    


###########expenses


#returns all details of a particular expense and user details, given the expense id number  
def expense_query(eid):
    cur = mysql.connection.cursor()
    cur.execute('select * from create_expense where expense_id=%s',(eid,))
    expense=list(cur.fetchall())
    if expense==[]:
        return []
    bid=expense[0]['budget_id']
    cur.execute('select user.id, user.email, create_budget.budget_id from user join create_budget on user.id=create_budget.user_id where create_budget.budget_id=%s',(bid,))
    expense_details= list(cur.fetchall())   
    return expense_details[0]

#returns details about  a expense when a expense id is provided
@app.route('/expenses/<expenseId>', methods=['GET'])
@token_required
def getExpense(postdata, expenseId):
    cur = mysql.connection.cursor()
    check, exp =check_expense_exist(expenseId)
    user_details= expense_query(expenseId)  #get expense and user details to which that expense belongs to
    #checks if a expense exist and checks if expense belongs to any users 
    if check==True or user_details==[]:
        return jsonify({'message':'Could not find that particular expense','code':-1 }),400
    #checks if user is authorized or an admin
    if postdata["email"]==user_details["email"] or postdata["admin"]==1:
        expense=user_expense(expenseId)     #get all the details of a particular expense including purchases
        return jsonify({'message':'Successfully returned expense', 'code':0, 'expenses':expense[0]}), 200
    return jsonify({'message':'Unauthorized user','code':-1 }),401
    
#Update a particular expense and its details 
@app.route('/expenses/<expenseId>', methods=['PUT'])
@token_required
def updateExpense(postdata,expenseId):
    cur = mysql.connection.cursor()
    check, exp =check_expense_exist(expenseId)
    user_details= expense_query(expenseId)  #get expense and user details to which that expense belongs to
    if check==True or user_details==[]:
        return jsonify({'message':'Could not find that particular expense','code':-1 }),400
    #check if user is authorized or an admin
    if postdata["email"]==user_details["email"] or postdata["admin"]==1:
        data=request.get_json()
        cur = mysql.connection.cursor()
        cur.execute('select * from expense where id=%s',(expenseId,))
        expense= list(cur.fetchall())

        if not 'name' in request.json:
            name=expense[0]['name']
        else:
            name=data['name']
        if not 'allocation' in request.json:
            allocation=expense[0]['allocation']
        else:
            allocation=data['allocation']
        
        cur.execute('UPDATE expense set name=%s,allocation=%s where id=%s',(name,allocation,expenseId,))
        mysql.connection.commit()
        cur = mysql.connection.cursor()
        expense=user_expense(expenseId)    #get all the details of a particular expenses including purchases
        return jsonify({'message':'Successfully updated expense', 'code':0, 'expense':expense[0]}), 200
    return jsonify({'message':'Unauthorized user','code':-1 }),401
        
#Delete a specific expense given a expense id number
@app.route('/expenses/<expenseId>', methods=['DELETE'])
@token_required
def deleteExpense(postdata,expenseId):
    cur = mysql.connection.cursor()
    check, exp =check_expense_exist(expenseId)
    user_details= expense_query(expenseId)          #get expense and user details to which that expense belongs
    if check==True or user_details==[]:
        return jsonify({'message':'Could not find that particular expense','code':-1 }),400
    if postdata["email"]==user_details["email"] or postdata["admin"]==1:
        cur = mysql.connection.cursor()
        cur.execute('DELETE from expense where id=%s',(expenseId,))  #delete the expense from the database
        mysql.connection.commit()
        return jsonify({'message':'Expense deleted', 'code':0}), 200
    return jsonify({'message':'Unauthorized user','code':-1 }),401
    




#########################3expense and purchase

#Return the purchases belonging to a particular expense
@app.route('/expenses/<expenseId>/purchases', methods=['GET'])
@token_required
def getExpensePurchases(postdata,expenseId):
    cur = mysql.connection.cursor()
    check, exp =check_expense_exist(expenseId)
    if check==True:
        return jsonify({'message':'Could not find that particular expense','code':-1 }),400
    user_details= expense_query(expenseId)          #get expense and user details to which that expense belongs 
    if postdata["email"]==user_details["email"] or postdata["admin"]==1:
        expense=user_expense(expenseId)         #get all the details of a particular expenses including purchases
        return jsonify({'message':'Successfully returned purchases', 'code':0, 'purchases':expense[0]['purchases']}), 200
    return jsonify({'message':'Unauthorized user','code':-1 }),401

#Create a purchase for a particular expense 
@app.route('/expenses/<expenseId>/purchases', methods=['POST'])
@token_required
def createPurchase(postdata,expenseId):
    cur = mysql.connection.cursor()
    #esnure all the require values are provided in the post request body to create a purchase
    if not request.json or not 'name' in request.json or not 'cost' in request.json :
        return jsonify({'message':'Could not create a new purchase. Ensure a valid name and cost is provided','code':-1}), 400
    check, exp =check_expense_exist(expenseId)
    if check==True:
        return jsonify({'message':'Could not find that particular expense','code':-1 }),400
    user_details= expense_query(expenseId)          #get expense and user details to which that expense belongs 
    if postdata["email"]==user_details["email"] or postdata["admin"]==1:

        cur.execute('select id,name,cost,date from  purchase ORDER BY id DESC LIMIT 1')
        last_record=cur.fetchone()
        cur.close()
        if last_record is None:
            last_record = 1
        else:
            last_record = last_record['id'] + 1
        data=request.get_json()
        
        cur = mysql.connection.cursor()
        sql = "INSERT INTO purchase (id,name, cost, date) VALUES (%s, %s, %s, %s)"
        val = (last_record, data['name'], data['cost'],  datetime.now())
        cur.execute(sql, val)
        mysql.connection.commit()

        ####insert into relationship
        cur = mysql.connection.cursor()
        sql = "INSERT INTO create_purchase (expense_id,purchase_id ,date) VALUES (%s, %s, %s)"
        val = (expenseId, last_record,   datetime.now())
        cur.execute(sql, val)
        mysql.connection.commit()
        cur.execute('select * from purchase where id=%s',(last_record,))
        purchase= list(cur.fetchall())
        return jsonify({'message':'Successfully created purchase', 'code':0, "purchase":purchase[0]}), 200
    return jsonify({'message':'Unauthorized user','code':-1 }),401

   
################################################################purchase

#Returns user details that is linked to a particular purchase
def purchase_query(pid):
    cur = mysql.connection.cursor()
    cur.execute('select create_expense.budget_id, create_expense.expense_id, create_purchase.purchase_id from create_expense join create_purchase on create_expense.expense_id=create_purchase.expense_id where create_purchase.purchase_id=%s',(pid,))
    purchase=cur.fetchall()
    bid=purchase[0]['budget_id']
    cur.execute('select user.id, user.email, create_budget.budget_id from user join create_budget on user.id=create_budget.user_id where create_budget.budget_id=%s',(bid,))
    purchase_details= list(cur.fetchall())
    return purchase_details[0]

#Returns a specific purchase, given a purchase id number
@app.route('/purchases/<purchaseId>', methods=['GET'])
@token_required
def getPurchase(postdata,purchaseId):
    cur = mysql.connection.cursor()
    check, purchase =check_purchase_exist(purchaseId)       #checks if purchase exist
    if check==True:
        return jsonify({'message':'Could not find that particular purchase','code':-1 }),400
    user_details= purchase_query(purchaseId)   #get purchase and user details to which that purchase belongs
    if postdata["email"]==user_details["email"] or postdata["admin"]==1:
        return jsonify({'message':'Successfully returned purchase', 'code':0, 'purchase':purchase[0]}), 200
    return jsonify({'message':'Unauthorized user','code':-1 }),401

#Update a specific purchase, given a purchase id number
@app.route('/purchases/<purchaseId>', methods=['PUT'])
@token_required
def updatePurchase(postdata,purchaseId):
    cur = mysql.connection.cursor()
    check, purchase =check_purchase_exist(purchaseId)
    if check==True:
        return jsonify({'message':'Could not find that particular purchase','code':-1 }),400
    user_details= purchase_query(purchaseId)        #get purchase and user details to which that purchase belongs
    if postdata["email"]==user_details["email"] or postdata["admin"]==1:
        data=request.get_json()
        if not 'name' in request.json:
            name=purchase[0]['name']
        else:
            name=data['name']
        if not 'cost' in request.json:
            cost=purchase[0]['cost']
        else:
            cost=data['cost']
        
        cur.execute('UPDATE purchase set name=%s,cost=%s where id=%s',(name,cost,purchaseId,))
        mysql.connection.commit()
        cur = mysql.connection.cursor()
        cur.execute('select * from purchase where id=%s',(purchaseId,))
        purchase= list(cur.fetchall())
        return jsonify({'message':'Successfully updated expense', 'code':0, 'purchase':purchase[0]}), 200
    return jsonify({'message':'Unauthorized user','code':-1 }),401

#Delete a purchase, given a purchase id number 
@app.route('/purchases/<purchaseId>', methods=['DELETE'])
@token_required
def deletePurchase(postdata,purchaseId):
    cur = mysql.connection.cursor()
    check, purchase =check_purchase_exist(purchaseId)   #check if purchase exist in the database
    if check==True:
        return jsonify({'message':'Could not find that particular purchase','code':-1 }),400
    user_details= purchase_query(purchaseId)
    #checks that current user is authorized or an admin
    if postdata["email"]==user_details["email"] or postdata["admin"]==1:
        cur.execute('DELETE from purchase where id=%s',(purchaseId,))
        mysql.connection.commit()
        return jsonify({'message':'Purchase deleted', 'code':0}), 200
    return jsonify({'message':'Unauthorized user','code':-1 }),401



@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port="8080")