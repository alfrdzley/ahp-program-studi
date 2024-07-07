import mysql.connector
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import random

# Fungsi untuk membuat koneksi ke database MySQL
def create_connection():
    return mysql.connector.connect(
        host='localhost',  # Ganti dengan host MySQL Anda
        user='root',       # Ganti dengan username MySQL Anda
        password='new_password', # Ganti dengan password MySQL Anda
        database='ahp_db'  # Ganti dengan nama database MySQL Anda
    )

# Fungsi untuk menjalankan algoritma AHP dengan data dari list of dictionaries
def run_ahp_from_db(data, criteria_weights):
    # Menggabungkan bobot kriteria dan bobot alternatif untuk mendapatkan skor akhir
    num_alternatives = len(data)
    final_scores = np.zeros(num_alternatives)
    
    # Extract individual criteria weights from the data
    demand_weights = np.array([d["demand"] for d in data])
    cost_weights = np.array([d["cost"] for d in data])
    resources_weights = np.array([d["resources"] for d in data])
    academic_relevance_weights = np.array([d["academic_relevance"] for d in data])
    student_interest_weights = np.array([d["student_interest"] for d in data])
    
    # Calculate final scores
    final_scores += criteria_weights[0] * demand_weights
    final_scores += criteria_weights[1] * cost_weights
    final_scores += criteria_weights[2] * resources_weights
    final_scores += criteria_weights[3] * academic_relevance_weights
    final_scores += criteria_weights[4] * student_interest_weights
    
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
    conn = create_connection()
    query = "SELECT * FROM program_studi"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def update_program_studi(id, nama, demand, cost, resources, academic_relevance, student_interest):
    conn = create_connection()
    cursor = conn.cursor()
    query = "UPDATE program_studi SET nama = %s, demand = %s, cost = %s, resources = %s, academic_relevance = %s, student_interest = %s WHERE id = %s"
    cursor.execute(query, (nama, demand, cost, resources, academic_relevance, student_interest, id))
    conn.commit()
    cursor.close()
    conn.close()

def delete_program_studi_by_name(name):
    conn = create_connection()
    cursor = conn.cursor()
    query = "DELETE FROM program_studi WHERE nama = %s"
    cursor.execute(query, (name,))
    conn.commit()
    cursor.close()
    conn.close()

# Fungsi untuk menghapus duplikat
def delete_duplicates():
    conn = create_connection()
    cursor = conn.cursor()
    query = """
    DELETE t1 FROM program_studi t1
    INNER JOIN program_studi t2 
    WHERE 
        t1.id < t2.id AND 
        t1.nama = t2.nama;
    """
    cursor.execute(query)
    deleted_rows = cursor.rowcount
    conn.commit()
    cursor.close()
    conn.close()
    return deleted_rows

# Generate 100 random data dan insert ke database
for i in range(100):
    nama = f"Program Studi {i+1}"
    demand = random.uniform(0.05, 0.2)
    cost = random.uniform(0.05, 0.2)
    resources = random.uniform(0.05, 0.2)
    academic_relevance = random.uniform(0.05, 0.2)
    student_interest = random.uniform(0.05, 0.2)
    create_program_studi(nama, demand, cost, resources, academic_relevance, student_interest)

# Menghapus duplikat
deleted_rows = delete_duplicates()
print(f"Jumlah data duplikat yang dihapus: {deleted_rows}")

# Bobot kriteria (dummy untuk ilustrasi)
criteria_weights = [0.3, 0.2, 0.2, 0.15, 0.15]

# Membaca data dari database
df = read_program_studi()
alternatives_list = df.to_dict(orient='records')

# Menjalankan algoritma AHP dengan data dari database
results = run_ahp_from_db(alternatives_list, criteria_weights)

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
bars = plt.bar(program_studi, skor_akhir, color='skyblue')
plt.xlabel('Program Studi')
plt.ylabel('Skor Akhir')
plt.title('Skor Akhir Program Studi berdasarkan Algoritma AHP')
plt.xticks(rotation=90)

# Menandai alternatif terbaik
for bar in bars:
    if bar.get_height() == best_alternative['skor_akhir']:
        bar.set_color('red')

plt.tight_layout()
plt.show()
