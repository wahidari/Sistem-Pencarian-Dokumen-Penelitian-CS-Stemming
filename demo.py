# coding: utf-8
# Created on Fri Jul 19 22:47:11 2019
# @author: wahidari

import math
import database

# do ProcessText in demopage
def doDemoTextProcess(string):
    # to fix eror local variable 'dataindexdemo' referenced before assignment
    dataindexdemo = []
    newdataindexdemo = []
    vektor = 0

    # Indexing, Weighting and VectorLength Process
    # Prepare a cursor object using cursor() method
    cursor = database.db.cursor()
    # clear data on table demoindex
    cursor.execute("TRUNCATE `demoindex`")
    # if string not null
    if string:
        # Indexing Process
        # Iterate by word
        for word in string:
            # if word not null
            if word:
                # cek ada berapa baris hasil yang dikembalikan query tersebut
                cursor.execute("SELECT `frekuensi` FROM `demoindex` WHERE `term` = '" + word + "'")
                # ambil data dari database
                row_value = cursor.fetchall()
                # banyak baris dari hasil query
                rows_count = cursor.rowcount
                # cek jika ada data di database
                if rows_count > 0:
                    # ambil nilai dari kolom Frekuensi[0]
                    for row in row_value:
                        freq = row[0]
                    # jika sudah ada DocId dan Term tersebut freq + 1
                    freq += 1
                    # prepare update query
                    sqlupdate = "UPDATE `demoindex` SET `Frekuensi` = %s WHERE `Term` = %s"
                    # eksekusi query
                    cursor.execute(sqlupdate, (freq, word))
                    # commit database
                    database.db.commit()
                # jika belum ada data di database untuk term dan dokumen i
                else:
                    # eksekusi query dengan frekuensi yaitu 1
                    cursor.execute("INSERT INTO `demoindex` (term, frekuensi) VALUES ('" + word + "'"", 1)")
                    # commit database
                    database.db.commit()

        # Weighting Process
        # cek ada berapa banyak dokumen
        cursor.execute("SELECT DISTINCT DocId FROM tbindex")
        cursor.fetchall()
        # berapa banyak dokumen (N)
        NDoc = cursor.rowcount
        # print("NDoc = ", NDoc)
        # ambil semua data di tb demoindex
        cursor.execute("SELECT * FROM `demoindex`")
        dataindexdemo = cursor.fetchall()
        # untuk setiap baris di tb demoindex
        for i in dataindexdemo:
            # ambil id di kolom ke[0]
            id = i[0]
            # ambil tf di kolom ke[2]
            tf = i[2]
            # ambil term di kolom ke[1]
            term = i[1]
            # ada berapa banyak dokumen yang mengandung term  ke-i?
            cursor.execute("SELECT COUNT(*) AS N FROM tbindex WHERE Term = '" + term + "'")
            getNDocHaveTerm = cursor.fetchall()
            # simpan banyak dokumen yang mengandung term ke-i
            for j in getNDocHaveTerm:
                NDocHaveTerm = j[0]
            # hitung idf = log(banyak dokumen di corpus / banyak dokumen mengandung term)
            idf = math.log10(NDoc / NDocHaveTerm)
            # hitung tf x idf
            tfidf = round(tf * idf, 3)
            # update weight query
            sqlupdateweight = "UPDATE `demoindex` SET bobot = %s WHERE id = %s"
            # execute query
            cursor.execute(sqlupdateweight, (tfidf, id))
            # commit database
            database.db.commit()

        # Vector Length
        cursor.execute("SELECT * FROM `demoindex`")
        newdataindexdemo = cursor.fetchall()
        # inisiasi bobot total awal
        bobottotal = 0
        # untuk setiap baris di tb demoindex
        for j in newdataindexdemo:
            # ambil bobot di kolom ke[3]
            bobot = j[3]
            # tambahkan seiap bobot
            bobottotal += bobot * bobot
            # print("Bobot = ", bobot)
            # print("BobotTotal = ", bobottotal)
        # akarkan total bobot
        vektor = round(math.sqrt(bobottotal), 3)

    return dataindexdemo, newdataindexdemo, vektor
