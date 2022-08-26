import sqlite3
import datetime
import random
from settings import *
conn = sqlite3.connect('data.db')

def is_user_in_db(id):
    
    count_of_user_id_in_db = conn.execute(f'''SELECT COUNT(id) FROM users WHERE id = {id}''')
    return count_of_user_id_in_db.fetchall()[0][0]
    
def add_user_to_db(id, **ref_father):
    if ref_father:
        ref_father = ref_father['ref_father']
        conn.execute('''INSERT INTO users(id, ref_father, balance, referals, alltime_subs, fine_count, alltime_get_subs) VALUES(?,?,?,?,?,?,?)''', (id, ref_father, 0,str([]), 0, 0, 0))
        referals_of_ref_father = conn.execute(f'''SELECT referals FROM users WHERE id = ?''', (ref_father,))
        referals_of_ref_father = eval(referals_of_ref_father.fetchall()[0][0])
        referals_of_ref_father.append(id)
        referals_of_ref_father = str(referals_of_ref_father)
        conn.execute(f'''UPDATE users SET referals = ? WHERE id = ?''', (referals_of_ref_father, ref_father,))
        conn.execute('''UPDATE users SET balance = (balance + ?) WHERE id = ?''', (REF_BONUS, ref_father,))
        conn.commit()
    else:
        conn.execute('''INSERT INTO users(id, ref_father, balance, referals, alltime_subs, fine_count, alltime_get_subs) VALUES(?,?,?,?,?,?,?)''', (id, 0, 0, str([]), 0, 0, 0))
        conn.commit()
        
def user_balance(id):
    balance = conn.execute(f'''SELECT balance FROM users WHERE id = ?''', (id,))
    balance = balance.fetchall()[0][0]
    
    return balance
    
def alltime_subs(id):
    subscriptions = conn.execute(f'''SELECT alltime_subs FROM users WHERE id = {id}''')
    subscriptions = subscriptions.fetchall()[0][0]
    return subscriptions
    
def alltime_get_subs(id):
    subscriptions = conn.execute(f'''SELECT alltime_get_subs FROM users WHERE id = {id}''')
    subscriptions = subscriptions.fetchall()[0][0]
    return subscriptions
    
def fine_count(id):
    count = conn.execute(f'''SELECT fine_count  FROM users WHERE id = {id}''')
    count = count.fetchall()[0][0]
    return count
    
def referals(id):
    count = conn.execute(f'''SELECT referals  FROM users WHERE id = {id}''')
    count = eval(count.fetchall()[0][0])
    count = len(count)
    return count
    
def save_channel(**writer):
    if writer['writer'] and 'channel_id' in writer:
        number = conn.execute('''SELECT COUNT(number) FROM channels''').fetchall()[0][0] + 1
        conn.execute('''INSERT INTO channels(number, id, writer, status, checked_channels, fined) VALUES(?,?,?,?,?,?)''', (number, writer['channel_id'], writer['writer'], 0, str([]), str([]),))
        conn.commit()
        return number
    if writer['subs_count'] and writer['writer']:
        number = conn.execute('''SELECT MAX(number) FROM channels WHERE writer = ?''', (writer['writer'],))
        number = number.fetchall()[0][0]
        conn.execute('''UPDATE channels SET subscriptions = ?, subs_count = ? WHERE number = ?''', (str({}), writer['subs_count'], number,))
        
        conn.commit()
        
def get_channel_stat(writer):
    number = conn.execute('''SELECT MAX(number) FROM channels WHERE writer = ?''', (writer,))
    number = number.fetchall()[0][0]
    stat_list = conn.execute('''SELECT subs_count, id FROM channels WHERE writer = ? AND number = ?''', (writer, number,))
    return stat_list.fetchall(), number
    
def confirm_order(number):
    try:
        number = int(number)
        prom_info = conn.execute('''SELECT writer, subs_count FROM channels WHERE number = ?''', (number,))
        prom_info = prom_info.fetchall()
        id = prom_info[0][0]
        count = prom_info[0][1]
        conn.execute('''UPDATE channels SET status = 1 WHERE number = ?''', (number,))
        conn.execute('''UPDATE users SET balance = balance - ? WHERE id = ?''', (count, id,))
        conn.commit()
        return 1
    except Exception as e:
        return e
    
def delete_channel_from_db(number):
    number = int(number)
    status = conn.execute('''SELECT status FROM channels WHERE number = ?''', (number,))
    if status.fetchall()[0][0] == 0:
        conn.execute('''DELETE FROM channels WHERE number = ?''', (number,))
        conn.commit()
    else:
        return 0
    
def channel_for_subscribe(id):
    channels = conn.execute('''SELECT * FROM channels WHERE status = 1 AND subs_count >= 1''')
    channels_list = channels.fetchall()
    if len(channels_list) >= 1:
        good_channels = {}
        for x in channels_list:
            if len(eval(x[2])) < x[3] and id not in eval(x[2]):
                good_channels[x[1]] = x[0]
            else:
                delete_channel_from_db(x[0])
        if len(good_channels) >= 1:
            return good_channels
        else:
            return 0
    else:
        return 0
    
    
def edit_promotion_status(number, status):
    sql = conn.execute('''SELECT COUNT(number), writer, subscriptions, subs_count FROM channels WHERE number = ?''', (number,))
    sql_fetchall = sql.fetchall()
    if sql_fetchall[0][0] == 1 and status == 0:
        conn.execute('''UPDATE channels SET status = ? WHERE number = ?''', (status, number,))
        delta = len(eval(sql_fetchall[0][2])) - sql_fetchall[0][3]
        delta = abs(delta) * 0.5
        delta = round(delta, 0)
        conn.execute('''UPDATE users SET balance = balance + ? WHERE id = ?''', (delta, sql_fetchall[0][1],))
        conn.commit()
        return sql_fetchall[0][1]
        
def promotion_info(number_of_promotion):
    number = int(number_of_promotion)
    check_promotion = conn.execute('''SELECT COUNT(number) FROM channels WHERE number = ?''', (number,))
    if check_promotion.fetchall()[0][0] == 1:
        info = conn.execute('''SELECT subscriptions, subs_count, id FROM channels WHERE number = ?''', (number,))
        info = info.fetchall()
        subscriptions = info[0][0]
        subscriptions = eval(subscriptions)
        subs_count = info[0][1]
        if len(subscriptions) < subs_count:
            return 1, info[0][2]
        else:
            return 0, info[0][2]
    else:
        return 0, info[0][2]
        
def add_user_to_subscribers(number, user_id):
    
    number = int(number)
    get_count_of_num_i_status = conn.execute('''SELECT COUNT(number), status FROM channels WHERE number = ?''', (number,))
    get_count_of_num_i_status = get_count_of_num_i_status.fetchall()
    count_of_number = get_count_of_num_i_status[0][0]
    status = get_count_of_num_i_status[0][1]
    
    if count_of_number == 1 and status == 1:
        sql = conn.execute('''SELECT subscriptions, subs_count, id FROM channels WHERE number = ?''', (number,))
        global sql_fetchall
        sql_fetchall = sql.fetchall()
        subscriptions = sql_fetchall[0][0]
        subscriptions = eval(subscriptions)
        subs_count = sql_fetchall[0][1]
        if len(subscriptions) < subs_count:
            subscriptions[user_id] = datetime.datetime.now()
            conn.execute('''UPDATE channels SET subscriptions = ? WHERE number = ?''', (str(subscriptions), number))
            conn.execute('''UPDATE users SET balance = balance + 1 WHERE id = ?''', (user_id,))
            conn.commit()
            return 1, sql_fetchall[0][2]
        else:
            return 0, sql_fetchall[0][2]
    else:
        return 0, sql_fetchall[0][2]
        
def check_user_to_do_this(number, user_id):
    sql = conn.execute('''SELECT subscriptions FROM channels WHERE number = ?''', (number,))
    subs = eval(sql.fetchall()[0][0])
    if user_id in subs:
        return True
    else:
        return False
        
def check_channel_in_db(id):
    count_of_active_channels = conn.execute('''SELECT COUNT(id) FROM channels WHERE id = ? AND status = 1''', (id,))
    count_of_active_channels = count_of_active_channels.fetchall()[0][0]
    if count_of_active_channels == 1:
        return 0
    elif count_of_active_channels == 0:
        return 1
        
def get_users_for_mailing():
    users = conn.execute('''SELECT id FROM users''')
    return users.fetchall()
    
def user_banned(id):
    id = int(id)
    count = conn.execute('''SELECT COUNT(id) FROM black_list WHERE id = ?''', (id,))
    if count.fetchall()[0][0] == 0:
        return False
    else:
        return True

def uban_user(id, decision):
    count = conn.execute('''SELECT COUNT(id) FROM black_list WHERE id = ?''', (id,))
    id = int(id)
    decision = int(decision)
    if decision == 1:
        count = count.fetchall()[0][0]
        if count == 1:
            conn.execute('''DELETE FROM black_list WHERE id = ?''')
            conn.commit()
            return 'Пользователь был успешно удален из черного списка.'
        else:
            return 'Пользователь не был найден в черном списке или произошла непредвиденая ошибка'
    if decision == 0:
        count = count.fetchall()[0][0]
        if count == 0:
            conn.execute('''INSERT INTO black_list(id) VALUES(?)''', (id,))
            conn.commit()
            return 'Пользователь был успешно добавлен в черный список.'
        else:
            return 'Пользователь уже добавлен в черный список или произошла непредвиденная ошибка.'
            
def change_balance(id, value):
    count = conn.execute('''SELECT COUNT(id) FROM users WHERE id = ?''', (id,))
    if count.fetchall()[0][0] == 1:
        id = int(id)
        value = int(value)
        conn.execute('''UPDATE users SET balance = balance + ? WHERE id = ?''', (value, id, ))
        conn.commit()
        return 'Баланс пользователя был успешно изменён.'
    else:
        return 'Пользователь не был найден в БД или количесиво записей для его id != 1.'
        
def get_channels_for_check():
    channels = conn.execute('''SELECT * FROM channels WHERE black_list IS null''')
    channels = channels.fetchall()
    return channels
    
    
def get_last_check():
    sql = conn.execute('''SELECT * FROM other''')
    last_check = sql.fetchone()
    if last_check == None:
        return last_check
    else:
        return eval(last_check[0][0])
        
def set_last_check():
    conn.execute('''UPDATE other SET last_check = ?''', (str(datetime.datetime.now()),))
    conn.commit()
        
def add_promotion_to_uncheck(number_of_promotion):
    conn.execute('''UPDATE channels SET black_list = 0 WHERE number = ?''', (number_of_promotion,))
    conn.commit()
    
def add_member_to_checked(number, id):
    sql = conn.execute('''SELECT checked_channels FROM channels WHERE number = ?''', (number,))
    checked_users = eval(sql.fetchall()[0][0])
    checked_users.append(int(id))
    conn.execute('''UPDATE channels SET checked_channels = ? WHERE number = ?''', (checked_users, number,))
    conn.commit()
    
def count_of_channels():
    count = conn.execute('''SELECT COUNT(number) FROM channels''')
    return count.fetchall()[0][0]
    
def add_user_to_fined(number, id):
    get_fined = conn.execute('''SELECT fined FROM channels WHERE number = ?''', (number,))
    fined = eval(get_fined.fetchall()[0][0])
    if id not in fined:
        fined.append(id)
        conn.execute('''UPDATE channels SET fined = ? WHERE number = ?''', (str(fined), number,))
        conn.commit()
    
def user_was_fine(number, id):
    get_list_of_fined = conn.execute('''SELECT fined FROM channels WHERE number = ?''', (number,))
    if id in eval(get_list_of_fined.fetchall()[0][0]):
        return True
    else:
        return False
        
        
def increase_fine_count(id):
    conn.execute('''UPDATE users SET fine_count = fine_count - ? WHERE id = ?''', (FINE_FOR_UNSUBSCRIBING, id,))
    conn.commit()
    
