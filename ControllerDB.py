
import pymysql, json
from models import Task
from database import data_connection

debug_mode_on = True    # False: in deployment!
# Nota:
# Podrían mejorarse las conversiónes de
# touple a JSON aplicando alguna librería externa!

def get_connection():
    if debug_mode_on:
        # localhost database
        return pymysql.connect(
            user = data_connection.dev_database_user,
            password = data_connection.dev_database_passw,
            host = data_connection.dev_database_host,
            database = data_connection.dev_database_name
        )
    else:
        # (In production: GearHost MySQL database)
        return pymysql.connect(
            user = data_connection.database_user,
            password = data_connection.database_passw,
            host = data_connection.database_host,
            database = data_connection.database_name
        )

def query(sql_query):
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(sql_query)
    except Exception as e:
        connection.rollback()
    else:
        connection.commit()
        cursor.close()
        connection.close()

def select_query(sql_query, get_json):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(sql_query)
    rows = cursor.fetchall()

    if get_json:
        records = json.dumps(tuple(rows), indent=4, sort_keys=True, default=str)
        # print(records)
    else:
        records = rows

    cursor.close()
    connection.close()
    return records


def authentication(username, keyValue):
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT * FROM users")
    except Exception as e:
        raise e
    else:
        # rows = cursor.fetchall()
        rows = cursor.fetchone()
        results = []
        while rows is not None:
            results.append(rows)
            rows = cursor.fetchone()
    
        cursor.close()
        connection.close()
        for elem in results:
            if elem[0] == username and elem[1] == keyValue:
                return True
        raise Exception("Error de autenticación: clave incorrecta")


def insert_task(task, username):
    # Insert task in table Task:
    status_task = 1 if (task.status == True) else 0
    
    # task: (id,name,description,date_task,status,is_active)
    sql_query = "insert into task values(null, '{}', '{}', '{}', {}, 1)"
    query(sql_query.format(task.name, task.description, task.date_task, status_task))

    # Insert in table task_user:
    relation_task_user(task, username)
    pass

def relation_task_user(task, username):
    id_task = get_task_id(task.name, task.description)
    sql_query = "insert into task_user(id,username) values({}, '{}')"
    query(sql_query.format(id_task, username))

def get_last_task_id():
    pass

def get_task_id(name, description):
    sql_query = "select id from task where name='{}' and description='{}'".format(name, description)    
    records = select_query(sql_query, get_json=False)
    # id_task = results[0][0]
    print(records)
    if records == None:
        raise Exception("No se encontró")
    else:
        return int(records[0][0])


def get_all_tasks_from_user(username):
    sql_query = """select tu.id, tu.username, t.name, t.description, t.date_task,
    t.status from task_user tu join task t on(t.id=tu.id)
    where tu.username='{}' and t.is_active=1"""
    records = select_query(sql_query.format(username), get_json=False)
    data = []
    for t in records:
        task = Task.Task(t[0], t[2], t[3], t[4], t[5])
        data.append(task_to_object(task))
    
    return str(data).replace("'", '"')

def delete_task_from_user(id_task):
    sql_query = "update task set is_active=0 where id={}".format(id_task)
    query(sql_query)

def delete_all_tasks_from_user(username):
    pass

# t as task()
def task_to_object(t):
    return {"id": t.id_task, "name": t.name, "description": t.description, "date": t.date_task, "status": t.status}

