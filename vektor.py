# coding: utf-8
# Created on Fri Jul 19 22:47:11 2019
# @author: wahidari

import math
import database


# fungsi hitung panjang vektor dokumen
def doVektor():
    cursor = database.db.cursor()
    # ambil term, docid, frekuensi dari tbindex
    cursor.execute("SELECT DISTINCT `DocId` FROM `tbindex` ORDER BY `DocId`");
    data = cursor.fetchall()
    # untuk setiap dokumen ke-i
    for row in data:
        # simpan id dokumen ke-i
        DocId = row[0]
        # print("Dok Id = ", DocId)
        # ambil term, bobot dari dokumen ke-i
        cursor.execute("SELECT `Term`,`Bobot` FROM `tbindex` WHERE `DocId` = '" + str(DocId) + "'")
        # ambil data bobot dari term ke-i di dokumen ke-j
        databobot = cursor.fetchall()
        # bobot awal
        bobottotal = 0
        # untuk setiap term ke-i dari dokumen ke-i
        for i in databobot:
            # ambil term di kolom i[0]
            term = i[0]
            # ambil bobot di kolom i[1]
            bobot = i[1]
            # tambahkan ke bobottotal, bobot kuadrat dari tiap term di dokumen ke-i
            bobottotal += bobot * bobot
        # hitung akar dari total bobot dokumen ke-i
        vektor = math.sqrt(bobottotal)
        # ambil 3 angka dibelakang koma
        newtvektor = round(vektor, 3)
        # masukkan id dokumen dan nilai panjang vektor ke tabel tbvektor
        sqlinsert = "INSERT INTO `tbvektor` (`DocId`, `Vektor`) VALUES (%s, %s)"
        # jalankan query
        cursor.execute(sqlinsert, (DocId, newtvektor))
        # commit database
        database.db.commit()
