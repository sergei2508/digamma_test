from flask import Flask, request, jsonify
from werkzeug.exceptions import NotFound
from flask_mysqldb import MySQL
from tenacity import retry, stop_never, wait_fixed, retry_if_exception_type
from pymysql import OperationalError
from config import MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB, MYSQL_PORT

app = Flask(__name__)
app.config['MYSQL_HOST'] = MYSQL_HOST
app.config['MYSQL_PORT'] = MYSQL_PORT
app.config['MYSQL_USER'] = MYSQL_USER
app.config['MYSQL_PASSWORD'] = MYSQL_PASSWORD
app.config['MYSQL_DB'] = MYSQL_DB
mysql = MySQL(app)

# Decorador para aplicar retries a la función de base de datos
def retry_db_operation(func):
    @retry(stop=stop_never, wait=wait_fixed(10), retry=retry_if_exception_type(OperationalError))
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

@retry_db_operation
def execute_db_query(query, params=None):
    cur = mysql.connection.cursor()
    cur.execute(query, params)
    mysql.connection.commit()
    cur.close()

@retry_db_operation
def fetch_db_rows(query, params=None):
    cur = mysql.connection.cursor()
    cur.execute(query, params)
    rows = cur.fetchall()
    cur.close()
    return rows

@app.route('/students', methods=['POST'])
def create_student():
    data = request.json
    name = data['name']
    age = data['age']
    email = data['email']

    try:
        query = "INSERT INTO students (name, age, email) VALUES (%s, %s, %s)"
        execute_db_query(query, (name, age, email))

        return jsonify({'message': 'Student created successfully'})
    except Exception as e:
        error_message = str(e)
        return jsonify({'error': error_message}), 400

@app.route('/students', methods=['GET'])
def get_students():
    query = "SELECT * FROM students"
    rows = fetch_db_rows(query)

    students = []
    for row in rows:
        student = {
            'id': row[0],
            'name': row[1],
            'age': row[2],
            'email': row[3]
        }
        students.append(student)

    return jsonify(students)

@app.route('/students/<int:student_id>', methods=['GET'])
def get_student(student_id):
    query = "SELECT * FROM students WHERE id=%s"
    rows = fetch_db_rows(query, (student_id,))

    if rows:
        row = rows[0]
        student = {
            'id': row[0],
            'name': row[1],
            'age': row[2],
            'email': row[3]
        }
        return jsonify(student)
    else:
        raise NotFound("Student not found")

@app.route('/students/<int:student_id>', methods=['PUT'])
def update_student(student_id):
    query = "SELECT * FROM students WHERE id=%s"
    rows = fetch_db_rows(query, (student_id,))

    if rows:
        data = request.json
        name = data['name']
        age = data['age']
        email = data['email']

        query = "UPDATE students SET name=%s, age=%s, email=%s WHERE id=%s"
        try:
            query = "INSERT INTO students (name, age, email) VALUES (%s, %s, %s)"
            execute_db_query(query, (name, age, email))

            return jsonify({'message': 'Student created successfully'})
        except Exception as e:
            error_message = str(e)
            return jsonify({'error': error_message}), 400
    else:
        raise NotFound("Student not found")

@app.route('/students/<int:student_id>', methods=['DELETE'])
def delete_student(student_id):
    query = "SELECT * FROM students WHERE id=%s"
    rows = fetch_db_rows(query, (student_id,))

    if rows:
        query = "DELETE FROM students WHERE id=%s"
        execute_db_query(query, (student_id,))

        return jsonify({'message': 'Student deleted successfully'})
    else:
        raise NotFound("Student not found")

@retry(stop=stop_never, wait=wait_fixed(1))
def create_table():
    with app.app_context():
        cursor = mysql.connection.cursor()
        table_name = 'students'
        cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
        table_exists = cursor.fetchone()
        if not table_exists:
            create_table_query = '''
            CREATE TABLE students (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100),
                age INT,
                email VARCHAR(100)
            )
            '''
            cursor.execute(create_table_query)
            print("La tabla 'students' se ha creado correctamente.")
        mysql.connection.commit()
        cursor.close()

if __name__ == '__main__':
    create_table()
    app.run(host='0.0.0.0', port=5000, debug=True)

