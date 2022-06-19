from routes import * 

db.create_all()  # create all tables in database 
if __name__ == "__main__" : 
    app.run( debug =True)

