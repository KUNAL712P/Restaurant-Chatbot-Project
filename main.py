from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import generic_helper
import db_helper
import uvicorn

app = FastAPI()

# Global variable
inprogress_orders = {}

@app.post("/")
async def handle_request(request: Request):
    try:
        request_data = await request.json()
        print("Received request from Dialogflow")
        print(f"Full request: {request_data}")

        payload = request_data.get("queryResult")
        if not payload:
            print("No queryResult in request payload")
            return JSONResponse(content={"fulfillmentText": "Invalid request payload"})

        intent = payload.get("intent", {}).get("displayName")
        print(f"Detected intent: {intent}")

        parameters = payload.get("parameters", {})
        print(f"Parameters: {parameters}")

        output_contexts = payload.get("outputContexts", [])
        print(f"Output contexts: {output_contexts}")

        if not output_contexts:
            print("No output contexts found")
            return JSONResponse(content={"fulfillmentText": "No session context found, please try again."})

        session_id = generic_helper.extract_session_id(output_contexts[0].get("name"))
        print(f"Extracted session ID: {session_id}")

        if session_id is None:
            print("Session ID is None, returning error response")
            return JSONResponse(content={"fulfillmentText": "Session ID not found, please try again."})

        intent_map = {
            "order.add": add_to_order,
            "order.complete": complete_order,
            "track.order": track_order,
            "test.connection": test_connection,
            "order.remove": remove_from_order
        }

        if intent not in intent_map:
            print(f"Intent {intent} not found in intent_map")
            return JSONResponse(content={"fulfillmentText": "Intent not supported"})

        print(f"Calling handler for intent: {intent}")
        response = intent_map[intent](parameters, session_id)
        print(f"Final response: {response}")

        return response

    except Exception as e:
        print(f"Error in handle_request: {e}")
        return JSONResponse(content={"fulfillmentText": f"An error occurred: {str(e)}"})

def add_to_order(parameters: dict, session_id: str):
    print("Inside add_to_order function")
    print(f"Session ID: {session_id}")
    print(f"Parameters: {parameters}")
    food_items = parameters.get("food-item", [])
    quantities = parameters.get("number", [])
    if not food_items or not quantities:
        return JSONResponse(content={"fulfillmentText": "Please specify food items and quantities."})
    if session_id not in inprogress_orders:
        inprogress_orders[session_id] = {}
    for i in range(min(len(food_items), len(quantities))):
        inprogress_orders[session_id][food_items[i]] = float(quantities[i])
    # Create response with all items in the current order
    current_order = inprogress_orders[session_id]
    items_list = [f"{int(quantity)} {item}" for item, quantity in current_order.items()]
    response = "So far you have: " + ", ".join(items_list) + ". Do you need anything else?"
    return JSONResponse(content={"fulfillmentText": response})



def complete_order(parameters: dict, session_id: str):
    print("Inside complete_order function")
    print(f"Session ID: {session_id}")
    print(f"Current inprogress_orders: {inprogress_orders}")

    if session_id not in inprogress_orders:
        fulfillment_text = "I'm having trouble finding your order. Sorry! Can you place a new order please?"
        print("Order not found in inprogress_orders")
    else:
        order = inprogress_orders[session_id]
        print(f"Order found: {order}")

        # Use a single connection for all DB operations
        connection = db_helper.get_db_connection()
        if connection is None:
            fulfillment_text = "Sorry, there was an error connecting to the database. Please try again later."
            print("Failed to establish database connection")
            return JSONResponse(content={"fulfillmentText": fulfillment_text})
        try:
            order_id = db_helper.save_to_db_with_connection(order, connection)
            print(f"Order ID from save_to_db: {order_id}")

            if order_id == -1:
                fulfillment_text = "Sorry, I couldn't process your order due to a backend error. Please place a new order again."
                print("Failed to save order to database")
            else:
                order_total = db_helper.get_total_order_price_with_connection(order_id, connection)
                print(f"Order total: {order_total}")

                if order_total is None:
                    fulfillment_text = "Sorry, there was an error calculating your order total."
                    print("Failed to calculate order total")
                else:
                    fulfillment_text = f"Awesome. We have placed your order. Here is your order ID # {order_id}. Your order total is {order_total} which you can pay at the time of delivery!"
                    print("Order successfully placed")

            del inprogress_orders[session_id]
            print(f"Removed session from inprogress_orders: {session_id}")
        finally:
            if connection is not None:
                connection.close()

    print(f"Returning fulfillment text: {fulfillment_text}")
    return JSONResponse(content={"fulfillmentText": fulfillment_text})

def track_order(parameters: dict, session_id: str):
    print("Inside track_order function")
    order_id = int(parameters.get("order_id", -1))
    if order_id == -1:
        return JSONResponse(content={"fulfillmentText": "Please provide a valid order ID."})
    status = db_helper.get_order_status(order_id)
    if status is None:
        return JSONResponse(content={"fulfillmentText": f"No order found with ID {order_id}."})
    return JSONResponse(content={"fulfillmentText": f"The order status for order ID: {order_id} is: {status}."})

def remove_from_order(parameters: dict, session_id: str):
    print("Inside remove_from_order function")
    print(f"Session ID: {session_id}")
    print(f"Parameters: {parameters}")
    food_items = parameters.get("food-item")
    quantities = parameters.get("number")

    if not food_items or quantities is None or session_id not in inprogress_orders:
        return JSONResponse(content={"fulfillmentText": "No order found or invalid request to remove items."})

    # Handle both single value and list cases
    if not isinstance(food_items, list):
        food_items = [food_items]
    if not isinstance(quantities, list):
        quantities = [quantities]

    for i in range(min(len(food_items), len(quantities))):
        item = food_items[i]
        quantity_to_remove = float(quantities[i])
        if item in inprogress_orders[session_id]:
            current_quantity = inprogress_orders[session_id][item]
            if current_quantity <= quantity_to_remove:
                del inprogress_orders[session_id][item]  # Remove item if quantity becomes 0 or less
            else:
                inprogress_orders[session_id][item] -= quantity_to_remove  # Decrease quantity

    # Create response with all remaining items
    current_order = inprogress_orders[session_id]
    if not current_order:
        return JSONResponse(content={"fulfillmentText": "Your order is now empty. Please place a new order."})
    items_list = [f"{int(quantity)} {item}" for item, quantity in current_order.items()]
    response = "Okay sir, I removed the requested items from your order.\nSo far you have: " + ", ".join(items_list) + ". Do you need anything else?"
    return JSONResponse(content={"fulfillmentText": response})

def test_connection(parameters: dict, session_id: str):
    return JSONResponse(content={"fulfillmentText": "Connection test successful!"})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)