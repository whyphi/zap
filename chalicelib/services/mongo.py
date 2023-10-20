
from pymongo.mongo_client import MongoClient

class MongoService:
  """Manages connections to MongoDB."""
  def __init__(self):
    """Establishes connection to MongoDB server"""
    self.user = "admin"
    self.password = "quhL3ghIwNt03cNe"
    self.uri = f"mongodb+srv://{self.user}:{self.password}@cluster0.9gtht.mongodb.net/?retryWrites=true&w=majority"

    # Create a new client and connect to the server
    self.client = MongoClient(self.uri)

  def connect(self):
    # Send a ping to confirm a successful connection
    try:
        self.client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)
    
    # store db variable
    self.vault = self.client.vault
    
  def get_all_data(self):
    """fetches all data in specified collection"""
    try:
      self.users = self.vault.users.find()  # parameterize this
      # assert(self.users.count() != 0)   # this doesn't work, fix silent failure!!
    except Exception as e:
       print(e)
    
    # for u in self.users:
    #    print(u)
    return self.users

    # insert more CRUD methods here
    
# MongoTester = MongoService()
# MongoTester.connect()
# MongoTester.get_all_data()
