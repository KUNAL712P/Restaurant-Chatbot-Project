import mysql.connector


def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host="sql.freedb.tech",  # Replace with your FreeDB host
            user="freedb_ayush_freedb",  # Replace with your FreeDB username
            password="xmx8B@Bq%8u&$zG",  # Replace with your FreeDB password
            database=
            "freedb_restaurant_bot"  # Replace with your FreeDB database name
        )
        print("Database connection established")
        return connection
    except mysql.connector.Error as err:
        print(f"Error connecting to database: {err}")
        return None


def save_to_db_with_connection(order: dict, connection):
    try:
        cursor = connection.cursor()
        # Get the next order ID
        query = "SELECT MAX(order_id) FROM order_tracking"
        cursor.execute(query)
        result = cursor.fetchone()[0]
        next_order_id = (result + 1) if result else 1

        # Insert order items
        for food_item, quantity in order.items():
            query = "INSERT INTO order_items (order_id, food_item, quantity) VALUES (%s, %s, %s)"
            cursor.execute(query, (next_order_id, food_item, quantity))

        # Insert order tracking
        query = "INSERT INTO order_tracking (order_id, status) VALUES (%s, %s)"
        cursor.execute(query, (next_order_id, "in progress"))

        connection.commit()
        cursor.close()
        print("Order saved successfully with order_id:", next_order_id)
        return next_order_id
    except mysql.connector.Error as err:
        print(f"Error in save_to_db: {err}")
        return -1


def get_total_order_price_with_connection(order_id: int, connection):
    try:
        cursor = connection.cursor()
        query = """
            SELECT oi.food_item, oi.quantity 
            FROM order_items oi 
            WHERE oi.order_id = %s
        """
        cursor.execute(query, (order_id,))
        items = cursor.fetchall()

        total = 0
        for item in items:
            food_item, quantity = item
            # Fetch price from menu_items table
            price_query = "SELECT price FROM menu_items WHERE food_item = %s"
            cursor.execute(price_query, (food_item,))
            price_result = cursor.fetchone()
            if price_result:
                price = price_result[0]
                total += price * quantity
            else:
                print(f"No price found for item: {food_item}, using default price 5")
                total += 5 * quantity  # Default price if item not in menu

        cursor.close()
        print(f"Calculated total for order_id {order_id}: {total}")
        return total
    except mysql.connector.Error as err:
        print(f"Error in get_total_order_price: {err}")
        return None


def get_order_status(order_id: int):
    connection = get_db_connection()
    if not connection:
        return None
    try:
        cursor = connection.cursor()
        query = "SELECT status FROM order_tracking WHERE order_id = %s"
        cursor.execute(query, (order_id, ))
        result = cursor.fetchone()
        cursor.close()
        connection.close()
        return result[0] if result and isinstance(result, tuple) else None
    except mysql.connector.Error as err:
        print(f"Error in get_order_status: {err}")
        return None
