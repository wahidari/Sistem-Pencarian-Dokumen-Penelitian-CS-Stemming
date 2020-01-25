# coding: utf-8
# Created on Fri Jul 19 22:47:11 2019
# @author: wahidari

import mysql.connector

# Set up & Open database connection
db = mysql.connector.connect(user='root',
                             password='',
                             host='127.0.0.1',
                             database='cs_stemming')

# Cek if Database id Connected
if db.is_connected():
    print("Database Connected !")


# ambil data dari tbpaper
def getTabelPaper():
    cursor = db.cursor()
    # Prepare and execute sql
    cursor.execute("SELECT * FROM `tbpaper`")
    # Get data after sql execute
    datatabelpaper = cursor.fetchall()
    # print (rowvalue)
    return datatabelpaper


# ambil data dari tbpreprocessing
def getTabelPreprocessing():
    cursor = db.cursor()
    # Prepare and execute sql
    cursor.execute("SELECT * FROM `tbpreprocessing`")
    # Get data after sql execute
    datatabelpreprocessing = cursor.fetchall()
    # print (rowvalue)
    return datatabelpreprocessing


# ambil data dari tbindex
def getTabelIndexing():
    cursor = db.cursor()
    # Prepare and execute sql
    cursor.execute("SELECT * FROM `tbindex`")
    # Get data after sql execute
    datatabelindexing = cursor.fetchall()
    # print (rowvalue)
    return datatabelindexing


# ambil data bobot dari tbindex
def getTabelWeighting():
    cursor = db.cursor()
    # Prepare and execute sql
    cursor.execute("SELECT DISTINCT Bobot FROM tbindex")
    # Get data after sql execute
    tabelweighting = cursor.fetchall()
    # print (rowvalue)
    datatabelweighting = cursor.rowcount
    return datatabelweighting


# ambil data dari tbvektor
def getTabelVektor():
    cursor = db.cursor()
    # Prepare and execute sql
    cursor.execute("SELECT * FROM `tbvektor`")
    # Get data after sql execute
    datatabelvektor = cursor.fetchall()
    # print (rowvalue)
    return datatabelvektor
