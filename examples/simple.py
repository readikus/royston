from royston.royston import Royston
from datetime import datetime as dt
import pytz

roy = Royston()

# ingest a few documents
roy.ingest({ 'id': '123', 'body': 'Random text string', 'date': dt.now(pytz.UTC) })
roy.ingest({ 'id': '456', 'body': 'Antoher random string', 'date': dt.now(pytz.UTC) })

# find the trends - with this example, it won't find anything, as it's only got two stories!
trends = roy.trending()
print(trends)
