import mysql.connector
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Fungsi untuk membuat koneksi ke database MySQL
def create_connection():
    return mysql.connector.connect(
        host='localhost',  # Ganti dengan host MySQL Anda
        user='root',       # Ganti dengan username MySQL Anda
        password='new_password', # Ganti dengan password MySQL Anda
        database='ahp_db'  # Ganti dengan nama database MySQL Anda
    )

# Fungsi untuk membaca data dari database
def read_data_from_db():
    conn = create_connection()
    query = "SELECT * FROM program_studi"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# Fungsi untuk menjalankan algoritma AHP dengan data dari list of dictionaries
def run_ahp_from_db(data, criteria_weights, alternative_weights):
    # Menggabungkan bobot kriteria dan bobot alternatif untuk mendapatkan skor akhir
    final_scores = np.zeros(len(data))
    for criterion, weights in alternative_weights.items():
        final_scores += criteria_weights[list(alternative_weights.keys()).index(criterion)] * np.array(weights)
    
    # Menambahkan skor akhir ke data
    for i, alternative in enumerate(data):
        alternative["skor_akhir"] = final_scores[i]
    
    return data

# Fungsi untuk memperbarui skor akhir ke database
def update_scores_in_db(data):
    conn = create_connection()
    cursor = conn.cursor()
    for alternative in data:
        query = "UPDATE program_studi SET skor_akhir = %s WHERE id = %s"
        cursor.execute(query, (alternative['skor_akhir'], alternative['id']))
    conn.commit()
    cursor.close()
    conn.close()

# Fungsi untuk melakukan CRUD operation (Create, Read, Update, Delete)
def create_program_studi(nama, demand, cost, resources, academic_relevance, student_interest):
    conn = create_connection()
    cursor = conn.cursor()
    query = "INSERT INTO program_studi (nama, demand, cost, resources, academic_relevance, student_interest) VALUES (%s, %s, %s, %s, %s, %s)"
    cursor.execute(query, (nama, demand, cost, resources, academic_relevance, student_interest))
    conn.commit()
    cursor.close()
    conn.close()

def read_program_studi():
    return read_data_from_db()

def update_program_studi(id, nama, demand, cost, resources, academic_relevance, student_interest):
    conn = create_connection()
    cursor = conn.cursor()
    query = "UPDATE program_studi SET nama = %s, demand = %s, cost = %s, resources = %s, academic_relevance = %s, student_interest = %s WHERE id = %s"
    cursor.execute(query, (nama, demand, cost, resources, academic_relevance, student_interest, id))
    conn.commit()
    cursor.close()
    conn.close()

def delete_program_studi(id):
    conn = create_connection()
    cursor = conn.cursor()
    query = "DELETE FROM program_studi WHERE id = %s"
    cursor.execute(query, (id,))
    conn.commit()
    cursor.close()
    conn.close()

# Bobot kriteria (dummy untuk ilustrasi)
criteria_weights = [0.3, 0.2, 0.2, 0.15, 0.15]

# Bobot alternatif berdasarkan kriteria (dummy untuk ilustrasi)
alternative_weights = {
    "demand": [0.1, 0.15, 0.05, 0.2, 0.1, 0.05, 0.1, 0.1, 0.05, 0.1],
    "cost": [0.15, 0.1, 0.05, 0.2, 0.15, 0.05, 0.1, 0.1, 0.05, 0.05],
    "resources": [0.1, 0.15, 0.05, 0.2, 0.1, 0.05, 0.1, 0.1, 0.05, 0.1],
    "academic_relevance": [0.15, 0.1, 0.05, 0.2, 0.15, 0.05, 0.1, 0.1, 0.05, 0.05],
    "student_interest": [0.1, 0.15, 0.05, 0.2, 0.1, 0.05, 0.1, 0.1, 0.05, 0.1]
}

# Membaca data dari database
df = read_data_from_db()
alternatives_list = df.to_dict(orient='records')

# Menjalankan algoritma AHP dengan data dari database
results = run_ahp_from_db(alternatives_list, criteria_weights, alternative_weights)

# Memperbarui skor akhir di database
update_scores_in_db(results)

# Menampilkan hasil
for result in results:
    print(result)

# Menentukan alternatif dengan skor tertinggi
best_alternative = max(results, key=lambda x: x["skor_akhir"])
print(f"\nAlternatif terbaik untuk dibuka adalah: {best_alternative['nama']} dengan skor {best_alternative['skor_akhir']}")

# Membuat grafik bar dari hasil
program_studi = [result["nama"] for result in results]
skor_akhir = [result["skor_akhir"] for result in results]

plt.figure(figsize=(12, 6))
plt.bar(program_studi, skor_akhir, color='skyblue')
plt.xlabel('Program Studi')
plt.ylabel('Skor Akhir')
plt.title('Skor Akhir Program Studi berdasarkan Algoritma AHP')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
