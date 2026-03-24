import xmlrpc.client
import time
from datetime import datetime

url = 'https://testodin.odinrideshare.com'
db = 'testodin'
username = 'admin'
password = '123'

common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
uid = common.authenticate(db, username, password, {})

models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))

now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

order_id = models.execute_kw(db, uid, password, 'sale.order', 'create', [{
    'partner_id': 1,
    'is_food_order': True,
    'food_restaurant_id': 1,
    'state': 'sale',
}])

print(f"Created Sale Order {order_id} at {now}")
