import sqlite3
import datetime

conn = sqlite3.connect('./data.db')


sql = conn.execute('''DELETE FROM users''')

conn.commit()
#conn.execute('''CREATE TABLE channels (number integer, id integer, subscriptions text, subs_count integer, writer integer, status integer, chaked_channels text, black_list integer, checked_channels text, fined integer)''')

#conn.execute('''CREATE TABLE users (id integer, balance integer, alltime_subs integer, fine_count integer, referals text, ref_father integer, alltime_get_subs integer)''')





     
#for x in sql:
    #print(x)
conn.commit()
#CREATE TABLE channels (number integer, id integer, subscriptions text, subs_count integer, writer integer, status integer, chaked_channels text, black_list integer, checked_channels text, fined integer)


#CREATE TABLE users (id integer, balance integer, alltime_subs integer, fine_count integer, referals text, ref_father integer, alltime_get_subs integer)

#TABLE other(last_check)

#CREATE TABLE black_list (id integer)

#CREATE TABLE test (one, two, three)
