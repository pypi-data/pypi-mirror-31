### Mori Scaffold


> Basic User

```python

from mori_utils import query_mysql, query_mongo, query_odps
from mori_utils import execute_mysql
from mori_utils import invoke_dubbo, DubboParamInstance

mori_entry = DubboParamInstance('com.yit.ml.updater.entity.MoriEntity',
                                moriA='Test Content',
                                moriB=1234,
                                MoriC=['123', '456'])

print(invoke_dubbo('com.yit.ml.updater.api.MlUpdaterService', 'MoriTest', 'zookeeper', [mori_entry, 'test', 234.0]))

print(query_mysql('bisystem', 'SELECT * FROM action_types'))

print(query_mysql('bisystem', 'SELECT * FROM action_types', use_dict=True))

insert_id = execute_mysql('bisystem', 'INSERT INTO action_types(name) VALUE ("test")')

print(insert_id)

execute_mysql('bisystem', 'DELETE FROM action_types WHERE id = %d' % insert_id)

print(next(query_mongo('userprofile', {'_id': '244448'})))

print(next(query_mongo('userprofile', {'_id': 33251}, 'productProfile')))

print(list(query_odps('data_odps',
                      'SELECT * FROM yit_data_traffic.yit_product_view WHERE dt=20171223 LIMIT 5')))

print(list(query_odps('data_odps',
                      'SELECT * FROM yit_data_traffic.yit_product_view WHERE dt=20171222 LIMIT 5',
                      use_dict=True)))

```