def extract_session_id(session_str: str):
  print(f"Extracting session ID from: {session_str}")
  if not session_str:
      print("Session string is empty")
      return None
  try:
      session_parts = session_str.split("/")
      session_index = session_parts.index("sessions") + 1
      session_id = session_parts[session_index]
      print(f"Extracted session ID: {session_id}")
      return session_id
  except (IndexError, ValueError, AttributeError) as e:
      print(f"Error extracting session ID: {e}")
      return None


def get_str_from_food_dict(food_dict: dict):
  """
  Converts a dictionary of food items and quantities into a readable string.
  Example: {'pizza': 2, 'burger': 1} -> "2 pizza, 1 burger"
  """
  try:
      # Convert quantity to int to remove decimal points
      result = ", ".join([
          f"{int(quantity)} {item}" for item, quantity in food_dict.items()
      ])
      return result
  except Exception as e:
      print(f"Error converting food dict to string: {e}")
      return "Error in order format"
