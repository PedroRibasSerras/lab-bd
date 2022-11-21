from pymongo import MongoClient
from IPython.display import display
from dateutil import parser
import pandas as pd
import numpy as np


def get_database():
 

   client = MongoClient('localhost', 27017)
 
   return client['test']
  
# This is added so that many files can reuse the function get_database()
if __name__ == "__main__":   
  
   # Get the database
   dbname = get_database()
   names = dbname.list_collection_names()

   while(1):


      print("-------------------------------------------")
      for i in range(len(names)):
         print("{i} - {name}".format(i=i+1,name=names[i]))
      print("0 - Para finalizar o programa")

      ip = int(input("escolha uma collection: "))
      if(ip == 0):
         break
      collection_name = dbname[names[ip-1]]

      item_details = collection_name.find()
      items_df = pd.DataFrame(item_details)
      display(items_df)
   

   
    # expiry_date = '2021-07-13T00:00:00.000Z'

    # expiry = parser.parse(expiry_date)
    # item_3 = {
    #     "item_name" : "Bread",
    #     "quantity" : 2,
    #     "ingredients" : "all-purpose flour",
    #     "expiry_date" : expiry
    # }
    # collection_name.insert_one(item_3)