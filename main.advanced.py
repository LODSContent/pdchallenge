#Add test code here.
from datetime import date
import sys
import modifyCustomerCode
import exportCode
import json

#Read in the test #.
test = 0
noTest = False
if len(sys.argv) < 2:
    noTest = True
else:
    try:
      test = int(sys.argv[1])
      if  test < 1 or test > 4:
          noTest = True
    except:
        noTest = True
if noTest:
    print("Invalid test specification.\nUsage: python3 main.py [test #]\nWhere [test #] is the test you want to run:\n1 - Test connection\n2 - Test data retrieval\n3 - Test data modification\n4 - Test exception handling")
    sys.exit()


#Set up globals

with open('settings.json') as sFile:
    settings = json.load(sFile)
sqlHost = settings["sqlHost"]
sqlPort = settings["sqlPort"]
database = "classicmodels"
user=settings["user"]
password=settings["password"]

# Manage results files
def saveResults(file,object):
    path = "/home/coder/challenge/results.{}.json".format(file)
    fileName = "results.{}.json".format(file)
    with open(path,"w") as f:
        json.dump(object,f,indent=2)
    return "To view the results, open the {} file ".format(fileName)



testOrderNumber = 1000000


testOrder = {
    "orderNumber":testOrderNumber,
    "orderDate": date.fromisoformat("2020-12-05"),
    "requiredDate": date.fromisoformat("2020-12-23"),
    "shippedDate": date.fromisoformat("2020-12-10"),
    "status":"Shipped",
    "customerNumber":119
}

testDetails = [
    {
        "orderNumber":testOrderNumber,
        "productCode":"S18_1749",
        "quantityOrdered": 50,
        "priceEach":153.00,
        "orderLineNumber":1
    },
    {
        "orderNumber":testOrderNumber,
        "productCode":"S18_2325",
        "quantityOrdered": 40,
        "priceEach":120.00,
        "orderLineNumber":2
    }
]

def clearTestOrders(conn):
    sql1 = "DELETE FROM orderdetails where orderNumber = %s;" 
    sql2 = "DELETE from orders where orderNumber = %s;"
    csr = conn.cursor(dictionary=True)
    csr.execute(sql1, (testOrderNumber,))
    conn.commit()
    csr.close()
    csr = conn.cursor(dictionary=True)
    csr.execute(sql2, (testOrderNumber,))
    conn.commit()
    csr.close()

def getOrder(conn):
    sql = "SELECT * FROM orders WHERE orderNumber = {}".format(testOrderNumber)
    csr = conn.cursor(dictionary=True)
    csr.execute(sql)
    output = csr.fetchone()
    csr.close()    
    return output

def getOrderDetails(conn):
    sql = "SELECT * FROM orderdetails WHERE orderNumber = {}".format(testOrderNumber)
    csr = conn.cursor(dictionary=True)
    output = []
    csr.execute(sql)
    for result in csr:
        output.append(result)
    csr.close()    
    return output

if test == 1:
    try:
        conn = modifyCustomerCode.getConnection(sqlHost, sqlPort, database, user, password)
        if conn.database == database:
            print('You have successfully connected to the classicmodels database.')
            clearTestOrders(conn)
            rowCount = modifyCustomerCode.insertOrder(conn,testOrder)
            verify = getOrder(conn)
            if verify is None:
                print("You did not insert an order record.")
            else:
                verify["orderDate"] = str(verify["orderDate"] )
                verify["requiredDate"] = str(verify["requiredDate"] )
                verify["shippedDate"] = str(verify["shippedDate"] )
                print("You inserted the order record. {}".format(saveResults("insertOrder", verify)))
                try:
                    rowCount = modifyCustomerCode.insertOrder(conn,testOrder)
                    if rowCount is None:
                        print("You have successfully handled the IntegrityError exception in the insertOrder function.")
                    else:
                        print("You have not properly handled the IntegrityError exception in the insertOrder function.")
                except Exception as exin:
                    print("You have not properly handled the IntegrityError exception in the insertOrder function.")
                rowCount = modifyCustomerCode.insertDetails(conn,testDetails)
                verify = getOrderDetails(conn)
                if verify is None:
                    print("You did not insert order details")
                else:
                    for item in verify:
                        item["priceEach"] = float(item["priceEach"])
                    print("You inserted the order details. {}".format(saveResults("insertDetails", verify)))
                    try:
                        rowCount = modifyCustomerCode.insertDetails(conn,testDetails)
                        if rowCount is None:
                            print("You have successfully handled the IntegrityError exception in the insertDetails function.")
                        else:
                            print("You have not properly handled the IntegrityError exception in the insertDetails function.")
                    except Exception as exin:
                        print("You have not properly handled the IntegrityError exception in the insertDetails function.")
        else:
            print("You did not connect to the classicmodels database.")
    except Exception as ex:
        print("There was an exception raised while modifying relational data:\n{}".format(ex))


if test == 2:
    try:
        conn = modifyCustomerCode.getConnection(sqlHost, sqlPort, database, user, password)
        exportCode.exportCustomerOrders(conn)
    except Exception as ex:
        print("There was an error exporting order data:\n {}".format(ex))