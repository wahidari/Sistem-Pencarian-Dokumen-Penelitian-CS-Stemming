# coding: utf-8
# Created on Fri Jul 19 22:47:11 2019
# @author: wahidari

from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
import math
import database
import preprocess


# do Count Term Frequency Query
def countTFQuery(newQuery):
    # inisiasi dictionary
    indexquery = {}
    # untuk setiap term di newQuery
    for term in newQuery:
        # jika term sudah ada, frekuensi tambahkan 1
        if term in indexquery:
            indexquery[term] = indexquery[term] + 1
        # jika term belum ada frekuensi = 1
        else:
            indexquery[term] = 1
    return indexquery


# do Preprocessing Query
def doProcessQuery(inputQuery):
    factory = StemmerFactory()
    stemmer = factory.create_stemmer()
    # lakukan preprocessing pada query
    newQuery = preprocess.doPreprocessing(inputQuery)
    newQuery = " ".join(newQuery)
    stemquery = stemmer.stem(newQuery)
    newQuery = stemquery.split()
    # print(newQuery)
    # inisiasi termQuery dan bobotQuery sebagai list
    listTermQuery = []
    listBobotQuery = []
    # inisiasi panjangVektorQuery awal dengan 0
    VektorQuery = 0
    # koneksi database
    cursor = database.db.cursor()
    # berapa banyak total dokumen di tabel vektor
    cursor.execute("SELECT * FROM `tbvektor`")
    cursor.fetchall()
    # simpan total jumlah dokumen
    totalDokumen = cursor.rowcount
    # inisiasi list untuk menyimpan term dari query
    # variabel ini digunakan agar term tidak muncul > 1
    # [sistem, informasi, informasi] > [sistem, informasi]
    listQueryIndex = []
    # untuk setiap term ke-i dalam query
    for term in newQuery:
        # mencegah term yang sama dari query masuk index
        if term not in listQueryIndex:
            listQueryIndex.append(term)
    # untuk setiap term ke-i dalam list query baru
    for term in listQueryIndex:
        # hitung frekuensi term dari query asli
        TFQuery = countTFQuery(newQuery)
        # simpan frekuensi dari term
        Frekuensi = TFQuery[term]
        # berapa banyak dokumen yang mengandung term ke-i
        cursor.execute("SELECT COUNT(*) AS N FROM `tbindex` where `tbindex`.`term` = '" + term + "'")
        NTerm = cursor.fetchall()
        for i in NTerm:
            # banyak dokumen yang mengandung term ke - i
            totalDokumenTerdapatTerm = i[0]
        # jika term terdapat di database
        if totalDokumenTerdapatTerm > 0:
            # hitung bobot(idf) query ke-i. log(totalDokumen/totalDokumenTerdapatTerm)
            idfQuery = math.log10(totalDokumen / totalDokumenTerdapatTerm)
            # hitung tf x idf
            tfidfQuery = Frekuensi * idfQuery
            # ambil 3 angka dibelakang koma
            newtfidfQuery = round(tfidfQuery, 3)
            # simpan term & bobot(idf) query ke-i ke masing" list
            listTermQuery.append(term)
            listBobotQuery.append(newtfidfQuery)
            # tambahkan tiap bobot term ke-i dari query
            VektorQuery += newtfidfQuery * newtfidfQuery
        else:
            print("no term in index")
    # akarkan total bobot dari query, ambil 3 angka dibelakang koma
    panjangVektorQuery = math.sqrt(VektorQuery)
    panjangVektorQuery = round(panjangVektorQuery, 3)
    return listTermQuery, listBobotQuery, panjangVektorQuery
