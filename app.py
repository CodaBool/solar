from sense_energy import Senseable
from dotenv import load_dotenv
import os
from pymongo import MongoClient
from datetime import datetime, timedelta
import calendar

load_dotenv()
sense = Senseable()
# for some reason my email is broken by the @ symbol
sense.authenticate(os.environ.get("USERNAME") + "@pm.me", os.environ.get("PASSWORD"))
sense.update_realtime()
print ("usage", int(sense.active_power), "W")
print ("solar", int(sense.active_solar_power), "W")
client = MongoClient(os.environ.get("MONGO_URI"))

now = datetime.now()
est = now - timedelta(hours = 4) # est is -4
db = client['myFirstDatabase']
col = db['days']
col.create_index('expireAt', expireAfterSeconds=0)
col.insert_one({
  "usage": int(sense.active_power),
  "solar": int(sense.active_solar_power),
  "day": est.weekday(),
  "expireAt": est + timedelta(seconds=604800),
  'createdAt': est,
})

# only write monthly data at the end of the month
last_day = calendar.monthrange(est.date().year, est.date().month)[1]
is_last_day = est.date().day == last_day
target_time = datetime.combine(est.date(), datetime.min.time()) + timedelta(hours=23, minutes=55)
if not is_last_day and est.time() < target_time.time():
  print(f"month data upload in {last_day - est.date().day} days and {target_time-est} hours")
  exit(0)

# Check if a document exists with the given query
col = db['months']
document_exists = col.count_documents({
  'month': est.month,
  'year': est.year
}) > 0

# if there is no montly data for this month, add it
if not document_exists:
  sense.update_trend_data()
  print ("month usage:", int(sense.monthly_usage), "W")
  print ("month solar", int(sense.monthly_production), "W")
  col.insert_one({
    "average_usage": int(sense.monthly_usage),
    "average_solar": int(sense.monthly_production),
    "month": est.month,
    "year": est.year,
    'createdAt': est,
  })
else:
  print("no need to update monthly data")