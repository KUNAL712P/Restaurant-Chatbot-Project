
#### Step 1: GitHub Pe README.md File Banayein
1. GitHub pe apne repo (https://github.com/KUNAL712P/Restaurant-Chatbot-Project) mein jao.
2. "Add file" > "Create new file" pe click karo.
3. File name: `README.md` (`.md` zaroori hai).
4. Niche content area mein yeh paste karo (main neeche template de raha hu).
5. "Commit new file" pe click karo (default settings ke saath).

#### Step 2: README.md Content (Professional Template)
Yeh template English mein hai aur detailed instructions deta hai:

```markdown
# Restaurant Chatbot Project

## Overview
Welcome to the **Restaurant Chatbot Project**, a robust and scalable solution built with **Python**, **FastAPI**, **Dialogflow**, and **MySQL** to manage restaurant orders. This chatbot allows users to add, remove, and complete orders, with dynamic pricing fetched from a database. The project is designed to be self-hosted, enabling you to run it on your local machine or any server.

## Features
- Add items to an order (e.g., "I want 2 lassi and 2 burgers").
- Remove items from an order (e.g., "remove 1 burger").
- Complete an order and generate an order ID with a total price.
- Track order status using the order ID.
- Dynamic pricing based on a menu stored in the MySQL database.

## Prerequisites
Before setting up the project, ensure you have the following installed on your system:
- **Python 3.7+**
- **pip** (Python package manager)
- **MySQL Server** (or any MySQL-compatible database like MariaDB)
- **Git** (for cloning the repository)
- **Dialogflow Account** (for integrating the chatbot intent)

## Installation and Setup

### Step 1: Clone the Repository
1. Open your terminal or command prompt.
2. Run the following command to clone the repository:
   ```
   git clone https://github.com/KUNAL712P/Restaurant-Chatbot-Project.git
   ```
3. Navigate to the project directory:
   ```
   cd Restaurant-Chatbot-Project
   ```

### Step 2: Install Dependencies
1. Create a virtual environment (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
2. Install the required Python packages:
   ```
   pip install fastapi uvicorn mysql-connector-python
   ```

### Step 3: Set Up the MySQL Database
1. Install and start your MySQL server (e.g., using XAMPP, WAMP, or MySQL Workbench).
2. Create a new database (e.g., `restaurant_bot`):
   ```
   CREATE DATABASE restaurant_bot;
   ```
3. Create the required tables by running these SQL commands:
   ```sql
   USE restaurant_bot;

   CREATE TABLE menu_items (
       food_item VARCHAR(100) PRIMARY KEY,
       price DECIMAL(10, 2) NOT NULL
   );

   CREATE TABLE order_items (
       order_id INT,
       food_item VARCHAR(100),
       quantity DECIMAL(10, 2),
       PRIMARY KEY (order_id, food_item),
       FOREIGN KEY (food_item) REFERENCES menu_items(food_item)
   );

   CREATE TABLE order_tracking (
       order_id INT PRIMARY KEY,
       status VARCHAR(50)
   );
   ```
4. Insert sample menu items with prices:
   ```sql
   INSERT INTO menu_items (food_item, price) VALUES
   ('pizza', 127.00),
   ('burger', 39.00),
   ('mango lassi', 29.00),
   ('lassi', 25.00);
   ```

### Step 4: Configure Environment Variables
1. Create a `.env` file in the project root directory.
2. Add the following lines with your MySQL credentials:
   ```
   DB_HOST=localhost
   DB_USER=your_mysql_username
   DB_PASSWORD=your_mysql_password
   DB_NAME=restaurant_bot
   ```
   - Replace `your_mysql_username` and `your_mysql_password` with your MySQL credentials.
   - Use `localhost` as `DB_HOST` if running on your local machine, or your server’s IP if hosted remotely.

### Step 5: Set Up Dialogflow
1. Sign up for a Dialogflow account (https://dialogflow.cloud.google.com/).
2. Create a new agent (e.g., "RestaurantBot").
3. Define intents:
   - `order.add`: Training phrases like "I want 2 lassi", parameters: `number` (@sys.number), `food-item` (@sys.any).
   - `order.remove`: Training phrases like "remove 1 burger", parameters: `number` (@sys.number), `food-item` (@sys.any).
   - `order.complete`: Training phrases like "complete my order".
   - `track.order`: Training phrases like "track my order 123", parameter: `order_id` (@sys.number).
4. Enable webhook fulfillment for all intents and set the URL to `http://localhost:8080` (or your server’s URL when deployed).

### Step 6: Run the Application
1. Start the FastAPI server:
   ```
   uvicorn main:app --reload
   ```
   - This will run the server on `http://localhost:8080`.
2. Test the chatbot using the Dialogflow simulator or a custom client (e.g., Postman).

## Usage
- Interact with the chatbot via Dialogflow:
  - Add items: "I want 2 lassi and 1 pizza".
  - Remove items: "remove 1 pizza".
  - Complete order: "complete my order".
  - Track order: "track my order 1".
- The system will respond with the current order status and total price.

## Contributing
Feel free to fork this repository, make improvements, and submit pull requests. For major changes, please open an issue first to discuss.

## License
This project is licensed under the [MIT License](LICENSE) - see the [LICENSE](LICENSE) file for details.

## Acknowledgments
- Inspired by open-source chatbot projects.
- Thanks to the FastAPI, Dialogflow, and MySQL communities for their support.
