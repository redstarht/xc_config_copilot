from flask import Flask,render_template,request,jsonify
import sqlite3


app = Flask(__name__)

db = 'tests/test.db'

def con_db():
    return sqlite3.connect(db)

@app.route("/load_db")
def load_db():
    try:
        conn = con_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * from test_tb")
        data = cursor.fetchall()
        print(data)
        return jsonify(data)
    
    except Exception as e:
        print(e)
    


def save_recode_to_db(records):
    conn = con_db()
    cursor = conn.cursor()
    # 空欄データの削除
    ## リスト内包表記　https://chatgpt.com/share/6790e8f6-0468-8011-9e00-be5c9a91fbb7
    filtered_records = [record for record in records if any(field.strip() for field in record)]
    # 必要に応じて既存データを削除する
    cursor.execute("DELETE From test_tb")
    # 新しいデータを挿入
    cursor.executemany("INSERT INTO test_tb (id,name,official) VALUES(?,?,?)",filtered_records)

    conn.commit()
    conn.close()



@app.route("/")
def index():
    return render_template("index.html")

@app.route("/save-data",methods=['POST'])
def save_date():
    data = request.get_json()
    # dict型のメソッド .get 第2引数はデフォルト値
    records = data.get('records',[])

# application/jsonとは　：　JSONフォーマットでデータが送信される
    if not records:
        return jsonify({"status":"error","message":"No Records provided"}) ,400
    
    try:
        save_recode_to_db(records)
        return jsonify({"status":"success","message":"Records saved successfully"})
    except Exception as e:
        return jsonify({"status":"error","message":str(e)}),500
    
if __name__ == '__main__':
    app.run(debug=True)

