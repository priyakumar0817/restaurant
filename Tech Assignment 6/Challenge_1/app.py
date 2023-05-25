"""
Priya Senthilkumar, ECE 140A Winter 2023
Technical Assignment 6 - Challenge 1
This challenge creates the routes needed for client side to interact
with the server side in a more structured way. We set up our database
and create the necessary CRUD operations for requests in our Restaurant
Ordering system.
"""
# Add the necessary imports
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles  # Used mounting our static files
import uvicorn
import os  # environment variable access for database

import mysql.connector as mysql
from dotenv import load_dotenv

''' Environment Variables '''
load_dotenv("credentials.env")

db_host = os.environ['MYSQL_HOST']
db_user = os.environ['MYSQL_USER']
db_pass = os.environ['MYSQL_PASSWORD']
db_name = os.environ['MYSQL_DATABASE']

app = FastAPI()  # Specify the "app" that will run the routing
# Mount the public director
app.mount("/public", StaticFiles(directory="public"), name="public")

# --- Helper functions for CRUD funtionalities --- #


def create_menu_item(name: str, price: int) -> int:
    """Inserts menu item created by the user into the menu database and returns its id

    Args:
        name (str): name of menu item
        price (int): price for the item

    Returns:
        int: new menu item id
    """
    db = mysql.connect(host=db_host, database=db_name,
                       user=db_user, passwd=db_pass)
    cursor = db.cursor()
    # insert query with the corresponding fields from idea
    cursor.execute(
        'INSERT INTO Menu_Items(name,price) VALUES (%s, %s)', (name, price))
    db.commit()
    db.close()
    # return the id which would be what the cursor is pointing to
    return cursor.lastrowid


def create_order(item_id: int, name: str, quantity: int, status: str) -> int:
    """Inserts order item created by the user into the  orders database and returns its id

    Args:
        item_id (int): primary key from the menu database
        name (str): name of the user who placed the order
        quantity (int): how many orders the user received
        status (str): pending or completed status of order, init to pending

    Returns:
        int: newly created order item id
    """
    db = mysql.connect(host=db_host, database=db_name,
                       user=db_user, passwd=db_pass)
    cursor = db.cursor()
    # insert query with the corresponding fields from idea
    cursor.execute('INSERT INTO Orders(item_id,name,quantity,status) VALUES (%s, %s, %s, %s)',
                   (item_id, name, quantity, status))
    db.commit()
    db.close()
    # return the id which would be what the cursor is pointing to
    return cursor.lastrowid


def select_menu_items(item_id: int = None) -> list:
    """query selects all the menu items from menu database

    Args:
        item_id (int, optional): id of the menu item. Defaults to None.

    Returns:
        list: all the items in menu or just one
    """
    db = mysql.connect(host=db_host, database=db_name,
                       user=db_user, passwd=db_pass)
    cursor = db.cursor()

    # select all the menu items if no id was given
    if item_id == None:
        query = f'select item_id, name, price from menu_items;'
        cursor.execute(query)
        result = cursor.fetchall()
    else:
        # otherwise only select the one matching the id
        query = f'select item_id, name, price from menu_items where item_id = {item_id};'
        cursor.execute(query)
        result = cursor.fetchone()
    db.close()
    return result


def select_orders(item_id: int = None) -> list:
    """selects all the order items from order database corresponding to the menu id

    Args:
        item_id (int, optional): foreign key of menu id. Defaults to None.

    Returns:
        list: all the items in the order or just one
    """
    db = mysql.connect(host=db_host, database=db_name,
                       user=db_user, passwd=db_pass)
    cursor = db.cursor()

    if item_id == None:
        query = f'select order_id, item_id, name, quantity, status from orders;'
        cursor.execute(query)
        result = cursor.fetchall()
    else:
        query = f'select order_id, item_id, name, quantity, status from orders where item_id = {item_id};'
        cursor.execute(query)
        result = cursor.fetchone()
    db.close()
    return result


def update_menu(item_id: int, name: str, price: int) -> bool:
    """query to update an existing menu item

    Args:
        item_id (int): menu primary key
        name (str): name of menu item
        price (int): price of menu item

    Returns:
        bool: true if successful update or false for not
    """
    db = mysql.connect(host=db_host, database=db_name,
                       user=db_user, passwd=db_pass)
    cursor = db.cursor()
    # use parameters given
    query = 'update menu_items set name = %s, price = %s where item_id = %s;'
    values = (name, price, item_id)
    cursor.execute(query, values)
    db.commit()
    db.close()
    # true if the cursor completed the query
    return True if cursor.rowcount >= 1 else False


def update_orders(order_id: int, item_id: int, name: str, quantity: int, status: str) -> bool:
    """query the menu items that changed in the order database

    Args:
        order_id (int): order id primary key
        item_id (int): foreign menu id key
        name (str): order name
        quantity (int): order size
        status (str): order status

    Returns:
        bool: true if cursor changed indicating successful query
    """
    db = mysql.connect(host=db_host, database=db_name,
                       user=db_user, passwd=db_pass)
    cursor = db.cursor()
    query = 'update orders set item_id = %s, name = %s, quantity = %s, status = %s where order_id = %s;'
    values = (item_id, name, quantity, status, order_id)
    cursor.execute(query, values)
    db.commit()
    db.close()
    return True if cursor.rowcount == 1 else False


def delete_menu_item(item_id: int) -> bool:
    """deletes an item from the menu db

    Args:
        item_id (int): menu primary key id

    Returns:
        bool: true if successful deletion, false otherwise
    """
    db = mysql.connect(host=db_host, database=db_name,
                       user=db_user, passwd=db_pass)
    cursor = db.cursor()
    cursor.execute(f'delete from menu_items where item_id={item_id};')
    print("hello")
    db.commit()
    db.close()
    return True if cursor.rowcount == 1 else False


def delete_order(item_id: int) -> bool:
    """delete item from orders db

    Args:
        item_id (int): menu id foreign key

    Returns:
        bool: true if successful deletion, false otherwise
    """
    db = mysql.connect(host=db_host, database=db_name,
                       user=db_user, passwd=db_pass)
    cursor = db.cursor()
    cursor.execute(f"delete from orders where item_id={item_id};")
    db.commit()
    db.close()
    print(cursor.rowcount)
    return True if cursor.rowcount >= 1 else False


@app.get("/", response_class=HTMLResponse)
def get_html() -> HTMLResponse:
    """Used to retrieve the main html page of this challenge
    Returns:
        HTMLResponse: order.html page corresponding to the root route
    """
    with open("order.html") as html:
        return HTMLResponse(content=html.read())


@app.get("/admin", response_class=HTMLResponse)
def get_dash() -> HTMLResponse:
    """Used to retrieve the admin html page of this challenge
    Returns:
        HTMLResponse: admin.html page corresponding to the orders page
    """
    with open("admin.html") as html:
        return HTMLResponse(content=html.read())


@app.get("/menu")
def get_menu() -> dict:
    """Used to retrieve all menu objects from the database

    Returns:
        response dictionary with each menu object inside
    """
    menu_items = select_menu_items()
    keys = ['item_id', 'name', 'price']
    menu_items = [dict(zip(keys, item)) for item in menu_items]
    return {'menu_items': menu_items}


@app.get("/orders")
def get_orders() -> dict:
    """Used to query a collection of all orders

    Returns:
        JSON object where the key is menu_items and the value is the list
    """
    orders = select_orders()
    keys = ['order_id', 'item_id', 'name', 'quantity', 'status']
    orders = [dict(zip(keys, order)) for order in orders]
    return {'orders': orders}


@app.get('/menu/{item_id}')
def get_menu_item(item_id: int) -> dict:
    """retrieves 1 menu item, invokes helper function created on top of page

    Args:
        item_id (int): menu primary key id

    Returns:
        dict: menu item corresponding to the id
    """
    item = select_menu_items(item_id)
    response = {} if item == None else {
        'item_id': item[0], 'name': item[1], 'price': item[2]}
    return response


@app.get('/orders/{order_id}')
def get_ord(order_id: int) -> dict:
    """retrieves 1 order item, invokes helper function created on top of page

    Args:
        order_id (int): order primary key id

    Returns:
        dict: order item corresponding to the id, multiple if they exist
    """

    item = select_orders(order_id)
    print(item)
    response = {} if item == None else {
        'order_id': item[0], 'item_id': item[1], 'name': item[2], 'quantity': item[3], 'status': item[4]}
    return response


@app.post("/menu")
def add_menu_item(menu: dict):
    """adds menu item to menu db by invoking the helper function created towards top of page

    Args:
        menu (dict): menu item dictionary to add to menu db

    Returns:
        _type_: the new id of the item just added
    """
    new_id = create_menu_item(menu['name'],
                              menu['price'])
    return new_id


@app.post("/orders")
def add_order(order: dict):
    """adds order item to order db by invoking the helper function created towards top of page

    Args:
        order (dict): order item dictionary to add to order db

    Returns:
        _type_: the new id of the order just added
    """
    new_id = create_order(
        order['item_id'], order['name'], order['quantity'], order['status'])
    return select_orders(new_id)


@app.put("/menu/{item_id}")
def update_men(item_id: int, menu: dict):
    """updates an item from the menu db, uses helper function

    Args:
        item_id (int): primary key
        menu (dict): menu item to update

    Returns:
        _type_: item that was updated
    """
    return {'success': update_menu(item_id, menu['name'], menu['price'])}


@app.put("/orders/{order_id}")
def update_order(order_id: int, orders: dict):
    """updates an item from the menu db, uses helper function

    Args:
        order_id (int): primary key
        orders (dict): order item to update

    Returns:
        _type_: order item that was updated
    """
    print(orders)
    return {'success': update_orders(order_id, orders['item_id'], orders['name'], orders['quantity'], orders['status'])}


@app.delete("/menu/{item_id}")
def delete_menu(item_id: int) -> dict:
    """deletes an item from the menu db, uses helper function

    Args:
        item_id (int): primary key in menu db

    Returns:
        _type_: menu item that was deleted
    """

    return {'success': delete_menu_item(item_id)}


@app.delete("/orders/{item_id}")
def delete_ord(item_id: int) -> dict:
    """updates an item from the menu db, uses helper function

    Args:
        item_id (int): foreign menu key id
    Returns:
        _type_: order item that was deleted
    """
    return {'success': delete_order(item_id)}


# Run the app by a uvicorn call passing in localhost or 0.0.0.0
if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=6543)
