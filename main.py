from flask import Flask, jsonify, request
from flask_cors import CORS
import mysql.connector
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from pprint import pprint
app = Flask(__name__)
CORS(app)

#ketnoicsdl
try:
    mydb = mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="",
        database="agri-original"
    )

    query = '''
    select * from sanpham, danhmuc where sanpham.SP_MaDM = danhmuc.DM_Ma
    '''
    df_sanpham = pd.read_sql(query, mydb)
    pprint(df_sanpham.head())

except mysql.connector.Error as e:
    print(f'Error : {e}')

finally:
    if mydb:
        mydb.close()

# Gom đặc trưng
def combineFeatures(row):
    return str(row['DM_Ten']) + ". " + str(row['SP_MoTa'])

df_sanpham['combineFeatures'] = df_sanpham.apply(combineFeatures, axis=1)
pprint(df_sanpham['combineFeatures'].head())

# tính toán tương đồng
tf = TfidfVectorizer()
tfMatrix = tf.fit_transform(df_sanpham['combineFeatures'])
print("\ntfMaxtrix: ", tfMatrix)
similar = cosine_similarity(tfMatrix)
number = 5

print("\nsimilar: ", similar)

@app.route('/apiRecomend', methods=['GET'])
def get_data():
    ket_qua = []
    productid = request.args.get('id')
    productid = int(productid)

    # print(request.args)

    # return jsonify(request.args)

    # Thêm một tham số mới để trừ id sản phẩm
    exclude_current = request.args.get('exclude_current', default='true', type=str)
    exclude_current = exclude_current.lower() in ['true', '1', 'yes', 'y', 't']

    if productid not in df_sanpham['SP_Ma'].values:
        return jsonify({'Loi': 'Id khong hop le'})
  
    indexproduct = df_sanpham[df_sanpham['SP_Ma'] == productid].index[0]
    similarProduct = list(enumerate(similar[indexproduct]))
    # pprint(similarProduct)
    sortedSimilarProduct = sorted(similarProduct, key=lambda x:x[1], reverse=True)
    print("\nsortedSimilarProduct: ")
    pprint(sortedSimilarProduct)
    # trừ sản phẩm hiện tại
    if exclude_current:
        sortedSimilarProduct = [(index, score) for index, score in sortedSimilarProduct if index != indexproduct]

    ####
    # def lay_ten(index):
    #     return df_sanpham[df_sanpham.index == index]['S_Ten'].values[0]
    # # def lay_gia(index):
    # #     return df_sanpham[df_sanpham.index == index]['S_GiaBan'].values[0]
    # for i in range(1, number + 1):
    #     print(lay_ten(sortedSimilarProduct[i][0]))
    #     ket_qua.append(lay_ten(sortedSimilarProduct[i][0]))
    #     # ket_qua.append(lay_gia(sortedSimilarProduct[i][0]))

    # data = {'san pham goi y': ket_qua}
    # return jsonify(data)

    ####

    # Lấy thông tin và thêm kết quả
    for i in range(min(number, len(sortedSimilarProduct))):
        product_info = df_sanpham.iloc[sortedSimilarProduct[i][0]]
        product_data = {
            'rate' : sortedSimilarProduct[i][1],
            'SP_Ma' : int(product_info['SP_Ma']),
            'SP_Ten': product_info['SP_Ten'],
            'SP_Gia': int(product_info['SP_Gia']),
            'SP_HinhAnh' : product_info['SP_HinhAnh'],
            'SP_MoTa' : product_info['SP_MoTa'],
        }
        print("\nproduct_data: ");
        pprint(product_data)
        ket_qua.append(product_data)

    data = {'data': ket_qua}
    return jsonify(data)



@app.route("/hello")

def hello(): 
    return "Hello, Welcome to GeeksForGeeks"

   

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5557)

