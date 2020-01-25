# coding: utf-8
# Created on Fri Jul 19 22:47:11 2019
# @author: wahidari

import math
import database
import query

# Do Similiarity Measure
def doSimiliarity(stringquery):
    # get listTermQuery, listBobotQuery, panjangVektorQuery after doProcessQuery function process
    listTermQuery, listBobotQuery, VektorQuery = query.doProcessQuery(stringquery)
    # print("list term query = ", listTermQuery)
    # print("list bobot query = ", listBobotQuery)
    # print("vektor query = ", VektorQuery)
    # koneksi database
    cursor = database.db.cursor()
    # inisiasi variabel untuk menyimpan jumlah dokumen yang mirip dengan query
    totalDokumenMirip = 0
    # jika listTermQuery tidak kosong setelah preprocess
    if listTermQuery:
        print("query not empty after preprocess")
        # ambil total dokumen yang telah di lakukan perhitungan panjang vektor
        cursor.execute("SELECT * FROM `tbvektor` ORDER BY `DocId`")
        dataTabelVektor = cursor.fetchall()
        # untuk setiap baris di tabel Vektor
        for dataVektor in dataTabelVektor:
            # simpan id dokumen ke-i (column[0]) di var DocId
            DocId = dataVektor[0]
            # print("Doc Id = ", DocId)
            # simpan panjang Vektor Dokumen ke-i (column[1]) di var VektorDokumen
            VektorDokumen = dataVektor[1]
            # print("Vektor Dokumen = ", VektorDokumen)
            # variabel ini digunakan untuk menyimpan nilai pemjumlahan hasil dari
            # akar perkalian setiap term ke-i dari query yang sama dengan term ke-i dari dokumen
            # inisiasi dot product awal dengan 0
            similiarity = 0
            # ambil setiap term ke-i di tabel index dari setiap Dokumen ke-i berdasarkan DocId
            cursor.execute("SELECT * FROM `tbindex` WHERE `tbindex`.`DocId` = '" + str(DocId) + "'")
            dataTabelIndex = cursor.fetchall()
            # untuk setiap term ke-i dari setiap Dokumen ke-i di tabel index
            for dataIndex in dataTabelIndex:
                # simpan term ke-i, dari column[1] = (term)
                termDiIndex = dataIndex[1]
                # simpan bobot term ke-i, dari column[4] = (bobot)
                bobotTermDiIndex = dataIndex[4]
                # lakukan perulangan sebanyak panjang dari query yang  berupa list di listTermQuery
                for x in range(len(listTermQuery)):
                    # cek jika term ke-i dari dokumen ke-i sama dengan term ke-i query
                    if termDiIndex == listTermQuery[x]:
                        # print("Term on Doc = ", termDiIndex + " | " + "Term on Query = ", listTermQuery[x])
                        # jika term ke-i dokumen sama dengan term ke-i query lakukan
                        # cari nilai dot product sigma(sqrt(TDij*TQij))
                        # (jumlahkan tiap hasil (akar dari (perkalian bobot term ke-i dokumen dengan term ke-i query)))
                        similiarity = similiarity + (bobotTermDiIndex * listBobotQuery[x])
            # print("Dot Product = ", similiarity)
            # jika nilai dot product antara query dengan dokumen lebih dari 0, simpan !
            if similiarity > 0:
                # hitung nilai Improved Sqrt-Cosine Similiarity
                # dot product/(VECTOR-Doc-ke-i * VECTOR-Q)
                isc = similiarity / (VektorDokumen * VektorQuery)
                # ambil 4 angka di belakang koma
                isc = round(isc, 4)
                # prepare insert query
                cursor.execute("INSERT INTO `tbcache`(`Query`, `DocId`, `Similiarity`) VALUES (%s, %s, %s)",
                               (stringquery.lower(), DocId, isc))
                # commit database
                database.db.commit()
                # tambahkan 1 di totalDokumenMirip
                totalDokumenMirip += 1
        # jika tidak ada dokumen yang mirip dengan query
        if totalDokumenMirip == 0:
            # cek sudah ada query di tbcache atau belum
            cursor.execute("SELECT * FROM `tbcache` WHERE `Query` = '" + stringquery.lower() + "'")
            cursor.fetchall()
            queryexist = cursor.rowcount
            # jika belum ada query di tabel cache
            if not queryexist > 0:
                # prepare insert query
                cursor.execute("INSERT INTO `tbcache`(`Query`, `DocId`, `Similiarity`) VALUES (%s, %s, %s)",
                               (stringquery.lower(), 0, 0))
                # commit database
                database.db.commit()
    if not listTermQuery:
        print("query is empty after preprocess")

