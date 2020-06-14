
# STEP 1  DATABASE SETUP:

N.B the name of the database is called "budget", ensure there is no other database on your system with that name
The database used is MariaDb (Flask mysqldb is used for communication with the database)
To set up the database, the budget.sql needs to be execute from the mariaDb command line interface:

+ Use the command \\.{path of file}\budget.sql  to run the budget.sql file
+ {path of file} refers to the full path location of the file on the computer.
+ For example,  \\. C:\Users\bastic\Documents\assessment\budget.sql

The database will now contain dummy data to help facilitate testinhg. 

**Admin Users include :**
+ email:admin@speurgroup.com  password: admin
- email:alex@gmail.com        password: admin

**Regular Users include :**     
+ email:alexgrant@gmail.com  password: 1234
* email:bastic@gmail.com     password: 1234


# STEP 2 VIRTUAL ENVIRONMENT ACTIVATION:
We need to change directory from the root directory to the Scripts folder inside the venv directory
The commands to do this are listed below

1.   **cd venv**
2.   **cd Scripts**
3.   **./activate** 
4.   Use the **cd..** command to go back to root folder

# STEP 3 INSTALL REQUIREMENTS.TXT:
1. from the root folder use the command **pip install requirements.txt**

# STEP 4 RUN THE APPLICATION:
1. from the root folder run the application with the command **python run.py**

# STEP 5 USING POSTMAN:
1. start up postman and enter the following url http://localhost:8080/login
2. select body from the options provided below the url section, then select raw and lastly change text to JSON 
3. enter a JSON object containing email and password. For example 
    + { "email" : "admin@speurgroup.com",     "password": "admin" }
    + { "email" : "alexgrant@gmail.com",      "password": "1234"  }
4. After providing the JSON object in the body send a post request to the http://localhost:8080/login and response containing a code, message and JWT token will be provided.
5. To access any other route/url, select authorization from the options below the url bar, then select Bearer Token  from the type drop downlist.  Then copy and paste the JWT token in the token bar. Then all routes will be accessible if the person is authorized. 
6. Then navigate to any route/url provided that the current user is authorized.
 

# Assumptions

1. To invalidate the JWT token without using a database, a set is used to stored tokens that have been used to logged out. This set is referred to as a blacklist, it is volatile. Refresh the server to clear the blacklist.
2. The payload for the JWT token include user email, user hashed password and admin role for ease of access when granting authorization and checking current user roles. 