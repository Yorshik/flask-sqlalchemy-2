import datetime
import random

from data.db_session import *
from data.jobs import Jobs
from data.users import User
import mimesis

global_init('db/database.db')
db_sess = create_session()
i = 1
user = User()
user.name = 'Test'
user.surname = 'Tester'
user.email = 'tester@test.com'
user.age = 23
user.position = 'none'
user.speciality = 'no specialities'
user.set_password('1234')
user.address = 'Saint Petersburg'
db_sess.add(user)
db_sess.commit()
db_sess.close()
