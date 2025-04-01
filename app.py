from flask import Flask,render_template, request
from flask_cors import CORS
from flask_mysqldb import MySQL
from flask import jsonify
from collections import defaultdict
from datetime import datetime
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_httpauth import HTTPBasicAuth


app = Flask(__name__)

# Initialize Limiter
limiter = Limiter(get_remote_address, app=app)

# Initialize Basic Auth
auth = HTTPBasicAuth()

# Sample user data for Basic Auth 
users = {
    "Username": "password123",  # username: password
    "Password": "kanzaFatima"
}

# Basic Authentication - Verify username and password
@auth.verify_password
def verify_password(username, password):
    # Logging for debugging
    print(f"Verifying user: {username} with password: {password}")
    
    if users.get(username) == password:
        return username
    return None  

app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'saqib0099'  # Enter your MySql password 
app.config['MYSQL_DB'] = 'BazaarTechnologies'

mysql = MySQL(app)

@app.route('/')                   
def printhello():
    return jsonify({"msg":"Welcome to the Kiryana Store"})

@app.route('/AddCity', methods=['POST'])
@auth.login_required  # Require authentication for this route
@limiter.limit("10/minute")
def addCity():
    cityCode = request.get_json().get('cityCode')
    cityName = request.get_json().get('cityName')

    if not cityCode:
        return jsonify({'msg': 'Please provide city code'})

    if not cityName:
        return jsonify({'msg': 'Please provide city name'})

    cursor = mysql.connection.cursor()

    # Insert city into the database
    cursor.execute('INSERT INTO City (CityCode, CityName) VALUES (%s, %s)', (cityCode, cityName))

    # Commit the transaction to the database
    mysql.connection.commit()

    city = cursor.fetchone()  # Get the ID of the last inserted city
    cursor.close()

    return jsonify({'msg': f'City added with city code {cityCode} and city name {cityName}'})


# Add Store
@app.route('/AddStore', methods=['POST'])
@auth.login_required  # Require authentication for this route
@limiter.limit("10/minute")
def addStore():
    storeName = request.get_json().get('storeName')
    cityCode = request.get_json().get('cityCode')
    location = request.get_json().get('location')
    status = request.get_json().get('status')

    if not storeName or not cityCode or not location or not status:
        return jsonify({'msg': 'Please provide store details'})

    cursor = mysql.connection.cursor()
    cursor.execute('INSERT INTO Store (storeName, cityCode, location, status) VALUES (%s, %s, %s, %s)',
                   (storeName, cityCode, location, status))
    mysql.connection.commit()
    cursor.close()

    return jsonify({'msg': f'Store {storeName} added in city {cityCode}'})

@app.route('/AddProductCategory', methods=['POST'])
@auth.login_required  # Require authentication for this route
@limiter.limit("10/minute")
def addProductCategory():
    pCategoryName = request.get_json().get('pCategoryName')
    pCategoryDesc = request.get_json().get('pCategoryDesc')

    if not pCategoryName:
        return jsonify({'msg': 'Please provide category name'})

    cursor = mysql.connection.cursor()
    cursor.execute('INSERT INTO ProductCategory (pCategoryName, pCategoryDesc) VALUES (%s, %s)',
                   (pCategoryName, pCategoryDesc))
    
    mysql.connection.commit()
    cursor.close()

    return jsonify({'msg': f'Product category {pCategoryName} added'})

# Get all Product Categories (only pCategoryId and pCategoryName)
@app.route('/GetProductCategories', methods=['GET'])
@auth.login_required  # Require authentication for this route
@limiter.limit("10/minute")
def getProductCategories():
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT pCategoryId, pCategoryName FROM ProductCategory')
    categories = cursor.fetchall()
    cursor.close()
    return jsonify(categories)

# Add Product SubCategory
@app.route('/AddProductSubCategory', methods=['POST'])
@auth.login_required  # Require authentication for this route

@limiter.limit("10/minute")
def addProductSubCategory():
    pSubCatName = request.get_json().get('pSubCatName')
    pCategoryId = request.get_json().get('pCategoryId')

    if not pSubCatName or not pCategoryId:
        return jsonify({'msg': 'Please provide subcategory details'})

    cursor = mysql.connection.cursor()
    cursor.execute('INSERT INTO ProductSubCategory (pSubCatName, pCategoryId) VALUES (%s, %s)',
                   (pSubCatName, pCategoryId))
    mysql.connection.commit()
    cursor.close()

    return jsonify({'msg': f'Product subcategory {pSubCatName} added'})

# Get all Product SubCategories
@app.route('/GetProductSubCategories', methods=['GET'])
@auth.login_required  # Require authentication for this route
@limiter.limit("10/minute")

def getProductSubCategories():
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT pSubCatId, pSubCatName FROM ProductSubCategory')
    subcategories = cursor.fetchall()
    cursor.close()

# Add Product
@app.route('/AddProduct', methods=['POST'])
@limiter.limit("10/minute")

def addProduct():
    expiryDate = request.get_json().get('expiryDate')
    pSubCatId = request.get_json().get('pSubCatId')
    stockId = request.get_json().get('stockId')
    price = request.get_json().get('price')
    brand = request.get_json().get('brand')
    consumerType = request.get_json().get('consumerType')
    status = request.get_json().get('status')

    if not expiryDate or not pSubCatId or not stockId or not price or not brand or not consumerType or not status:
        return jsonify({'msg': 'Please provide complete product details'})

    cursor = mysql.connection.cursor()
    cursor.execute('INSERT INTO Products (expiryDate, pSubCatId, stockId, price, brand, consumerType, status) VALUES (%s, %s, %s, %s, %s, %s, %s)',
                   (expiryDate, pSubCatId, stockId, price, brand, consumerType, status))
    
    lastporudct=cursor.fetchone();
    print(lastporudct)

    mysql.connection.commit()
    cursor.close()

    return jsonify({'msg': f'Product added successfully'})

# add a sale
@app.route('/AddSale', methods=['POST'])
@auth.login_required  # Require authentication for this route
@limiter.limit("10/minute")

def addSale():
        # Get the data from the request
        data = request.get_json()

        pSubCatId = data.get('pSubCatId')
        storeId = data.get('storeId')
        pId = data.get('pId')

        # Check if all necessary fields are provided
        if not pSubCatId or not storeId or not pId:
            return jsonify({"error": "Product SubCategory ID, Store ID, and Product ID are required"}), 400

        # Open a connection to the database
        cursor = mysql.connection.cursor()

        # Insert the sale record into the Sales table
        cursor.execute('INSERT INTO Sales (pSubCatId, storeId, pId) VALUES (%s, %s, %s)',(pSubCatId, storeId, pId))
        
        mysql.connection.commit()

        # Get the saleId of the newly inserted sale
        saleId = cursor.lastrowid


        # Close the connection
        cursor.close()
        mysql.connection.close()

        # Return the success response
        return jsonify({
            "message": "Sale added successfully",
            "saleId": saleId,
            "pSubCatId": pSubCatId,
            "storeId": storeId,
            "pId": pId
        }), 201

@app.route('/AddStock', methods=['POST'])
@auth.login_required  # Require authentication for this route
@limiter.limit("10/minute")

def addStock():
    # Get the data from the request body
    data = request.get_json()

    # Extract fields from the request data
    pSubCatId = data.get('pSubCatId')
    itemQuantity = data.get('itemQuantity')
    storeId = data.get('storeId')

    # Validation for missing data
    if not pSubCatId or not itemQuantity or not storeId:
        return jsonify({'msg': 'Please provide product subcategory ID, item quantity, and store ID'})

    # Create a cursor to interact with MySQL database
    cursor = mysql.connection.cursor()

    # Insert the new stock record into the Stock table
    cursor.execute('INSERT INTO Stock (pSubCatId, itemQuantity, storeId) VALUES (%s, %s, %s)', 
                   (pSubCatId, itemQuantity, storeId))

    # Commit the transaction
    mysql.connection.commit()

    # Get the stockId of the newly inserted stock record
    stockId = cursor.lastrowid

    # Close the cursor
    cursor.close()

    # Return success response with the stockId of the newly added stock
    return jsonify({
        'msg': f'Stock added successfully with stockId {stockId}',
        'stockId': stockId,
        'pSubCatId': pSubCatId,
        'itemQuantity': itemQuantity,
        'storeId': storeId
    }), 201


#store wise sales given the date range

@app.route('/GetTotalSales', methods=['GET'])
@auth.login_required  # Require authentication for this route
@limiter.limit("10/minute")
def getTotalSales():
    # Extract parameters from the query string
    startDate = request.args.get('startDate')
    endDate = request.args.get('endDate')
    storeId = request.args.get('storeId')

    if not startDate or not endDate or not storeId:
        return jsonify({"msg": "Please provide startDate, endDate, and storeId parameters"}), 400

    # Query the database for the total sales in the given date range and store
    cursor = mysql.connection.cursor()

    cursor.execute('''
        SELECT SUM(p.price) AS total_sales
        FROM Sales s
        JOIN Products p ON s.pId = p.pId
        JOIN Stock st ON p.stockId = st.stockId
        WHERE s.saleDate BETWEEN %s AND %s
        AND st.storeId = %s
    ''', (startDate, endDate, storeId))

    # Fetch the result
    result = cursor.fetchone()
    print(result)

    # Check if result is not None and access the total_sales correctly
    if result and result[0] is not None:
        total_sales = result[0]
    else:
        total_sales = 0

    cursor.close()

    # Return the total sales result
    return jsonify({
        "msg": "Total sales fetched successfully",
        "total_sales": total_sales
    })

#most sold product category with any specific store
@app.route('/getpopularproductcategory', methods=['GET'])
@auth.login_required  # Require authentication for this route
@limiter.limit("10/minute")

def getpopularproductcat():
    # Extract parameters from the query string
    startDate = request.args.get('startDate')
    endDate = request.args.get('endDate')
    storeId = request.args.get('storeId')

    if not startDate or not endDate or not storeId:
        return jsonify({"msg": "Please provide startDate, endDate, and storeId parameters"}), 400

    # Query the database for the total sales in the given date range and store
    cursor = mysql.connection.cursor()

    cursor.execute('''
        SELECT 
            st.storeId,
            st.pSubCatId,
        FROM Sales s
        JOIN Products p ON s.pId = p.pId
        JOIN Stock st ON p.stockId = st.stockId
        WHERE s.saleDate BETWEEN %s AND %s
        AND st.storeId = %s
    ''', (startDate, endDate, storeId))

    # Fetch the result
    result = cursor.fetchone()
    print(result)

    # Check if result is not None and access the most sold subcategory correctly
    if result:
        store_id = result[0]
        p_sub_cat_id = result[1]
    else:
        return jsonify({"msg": "No sales data found for the given parameters"}), 404

    cursor.close()

    # Return the total sales result with the most sold product subcategory
    return jsonify({
        "msg": "Total sales and most sold subcategory fetched successfully",
        "storeId": store_id,
        "most_sold_subcategory": p_sub_cat_id,
    })


app.run(host='0.0.0.0', port=2000)

