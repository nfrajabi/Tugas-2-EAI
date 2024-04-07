from flask import Flask, jsonify, request
from flask_mysqldb import MySQL
from datetime import datetime

app = Flask (__name__)

# MySQL config
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '' 
app.config['MYSQL_DB'] = 'task_manager'

mysql = MySQL(app)

@app.route('/')
def root():
    return 'Selamat datang di aplikasi Manajemen Tugas'

@app.route('/task_list', methods=['GET', 'POST'])
def task_list():
    if request.method == 'GET':
        cursor = mysql.connection.cursor()
        query_params = request.args.to_dict()
        
        # Membangun query berdasarkan parameter yang diterima
        sql = "SELECT * FROM task_list WHERE 1=1"
        for key, value in query_params.items():
            sql += f" AND {key} = '{value}'"
        
        cursor.execute(sql)
        
        # Dapatkan nama kolom dari cursor.description
        column_names = [i[0] for i in cursor.description]
        
        # Ambil data dan format menjadi list of dictionaries
        data = []
        for row in cursor.fetchall():
            data.append(dict(zip(column_names, row)))
        
        cursor.close()
        
        return jsonify({'status': 'success', 'data': data}), 200

    elif request.method == 'POST':
        # Mengambil data dari request JSON
        data = request.json
        task_name = data.get('task_name')
        description = data.get('description')
        status = data.get('status')

        # Membuka koneksi dan melakukan insert ke database
        cursor = mysql.connection.cursor()
        sql = "INSERT INTO task_list (task_name, description, status) VALUES (%s, %s, %s)"
        val = (task_name, description, status)
        cursor.execute(sql, val)
        mysql.connection.commit()
        cursor.close()

        return jsonify({'status': 'success', 'message': 'Tugas berhasil ditambahkan!', 'timestamp': datetime.now()}), 201

@app.route('/task_detail')
def task_detail():
    if 'id' in request.args:
        cursor = mysql.connection.cursor()
        sql = "SELECT * FROM task_list WHERE id = %s"
        val = (request.args['id'],)
        cursor.execute(sql, val)

        # Mengambil nama-nama kolom dari cursor.description
        column_names = [i[0] for i in cursor.description]

        # Mengambil data dan memformatnya menjadi list of dictionaries
        data = []
        for row in cursor.fetchall():
            data.append(dict(zip(column_names, row)))

        cursor.close()
        
        return jsonify({'status': 'success', 'data': data}), 200
    else:
        return jsonify({'status': 'error', 'message': 'Parameter "id" diperlukan!'}), 400
    
@app.route('/delete_task', methods=['DELETE'])
def delete_task():
    if 'id' in request.args:
        cursor = mysql.connection.cursor()
        sql = "DELETE FROM task_list WHERE id = %s"
        val = (request.args['id'],)
        cursor.execute(sql, val)
        
        mysql.connection.commit()
        
        cursor.close()

        return jsonify({'status': 'success', 'message': 'Tugas berhasil dihapus!', 'timestamp': datetime.now()}), 200
    else:
        return jsonify({'status': 'error', 'message': 'Parameter "id" diperlukan!'}), 400

@app.route('/edit_task', methods=['PUT'])
def edit_task():
    if 'id' in request.args:
        data = request.get_json()
        cursor = mysql.connection.cursor()
        sql = "UPDATE task_list SET task_name=%s, description=%s, status=%s WHERE id = %s"
        val = (data['task_name'], data['description'], data['status'], request.args['id'],)
        cursor.execute(sql, val)
        mysql.connection.commit()
        cursor.close()

        return jsonify({'status': 'success', 'message': 'Tugas berhasil diperbarui!', 'timestamp': datetime.now()}), 200
    else:
        return jsonify({'status': 'error', 'message': 'Parameter "id" diperlukan!'}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)