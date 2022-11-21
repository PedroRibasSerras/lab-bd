from pymongo import MongoClient
from dateutil import parser
from pandas import DataFrame


def get_database():
 

   client = MongoClient('localhost', 27017)
 
   return client['user_shopping_list']
  
# This is added so that many files can reuse the function get_database()
if __name__ == "__main__":   
  
   # Get the database
    dbname = get_database()
    collection_name = dbname["myCollection"]
 
    item_details = collection_name.find()
    items_df = DataFrame(item_details)
    print(items_df)
    for item in item_details:
        # This does not give a very readable output
        print(item)

   
    # expiry_date = '2021-07-13T00:00:00.000Z'

    # expiry = parser.parse(expiry_date)
    # item_3 = {
    #     "item_name" : "Bread",
    #     "quantity" : 2,
    #     "ingredients" : "all-purpose flour",
    #     "expiry_date" : expiry
    # }
    # collection_name.insert_one(item_3)