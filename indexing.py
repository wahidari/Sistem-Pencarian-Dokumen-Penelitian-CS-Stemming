# coding: utf-8
# Created on Fri Jul 19 22:47:11 2019
# @author: wahidari

import database
import math

# fungsi indexing
def doIndexing(id, string):
    # pecah kalimat per kata
    stringsplit = string.split()
    # untuk setiap kata di stringsplit
    for word in stringsplit:
        doc_id = id
        # jika word tidak null
        if word:
            cursor = database.db.cursor()
            # cek ada berapa baris hasil yang dikembalikan query tersebut
            sqlselect = "SELECT `Frekuensi` FROM `tbindex` WHERE `Term` = %s AND `DocId` = %s"
            # execute query
            cursor.execute(sqlselect, (word, doc_id))
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
                sqlupdate = "UPDATE `tbindex` SET `Frekuensi` = %s WHERE `Term` = %s AND DocId = %s"
                # eksekusi query
                cursor.execute(sqlupdate, (freq, word, doc_id))
                # commit database
                database.db.commit()
            # jika belum ada data di database untuk term dan dokumen i
            else:
                # prepare insert query
                sqlinsert = "INSERT INTO `tbindex` (Term, DocId, Frekuensi) VALUES (%s, %s, 1)"
                # eksekusi query
                cursor.execute(sqlinsert, (word, doc_id))
                # commit database
                database.db.commit()

# fungsi weighting
def doWeighting():
    cursor = database.db.cursor()
    # ambil total dokumen
    cursor.execute("SELECT DISTINCT `DocId` FROM `tbindex`")
    cursor.fetchall()
    # banyak dokumen (N)
    totaldoc = cursor.rowcount
    # ambil term, docid, frekuensi
    cursor.execute("SELECT * FROM `tbindex` ORDER BY `Id`");
    data = cursor.fetchall()
    for row in data:
        # id dokumen
        id = row[0]
        # term ke-i di dokumen
        term = str(row[1])
        # frekuensi kemunculan term dalam suatu dokumen (tf)
        tf = row[3]
        # ambil total dokumen yang mengandung term tersebut (df)
        cursor.execute("SELECT COUNT(*) AS N FROM tbindex WHERE Term = '" + term + "'")
        getN = cursor.fetchall()
        # berapa banyak dokumen yang mengandung term tersebut (df)
        for i in getN:
            # simpan banyak dokumen yang mengandung term tersebut (df)
            termondoc = i[0]
        # hitung idf = log(N/df)
        idf = math.log10(totaldoc / termondoc)
        # hitung tfidf = tf x idf
        tfidf = tf * idf
        # ambil 3 angka dibelakang koma
        newtfidf = round(tfidf, 3)
        # update bobot
        sqlupdateweight = "UPDATE tbindex SET Bobot = %s WHERE Id = %s"
        # eksekusi query update bobot
        cursor.execute(sqlupdateweight, (newtfidf, id))
        # commit database
        database.db.commit()
