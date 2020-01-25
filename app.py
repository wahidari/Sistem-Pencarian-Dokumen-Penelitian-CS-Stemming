# coding: utf-8
# Created on Fri Jul 19 22:47:11 2019
# @author: wahidari

from flask import Flask, render_template, request
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
import database
import preprocess
import indexing
import similiarity
import vektor
import demo
import time

app = Flask(__name__)


# home page
@app.route("/", methods=['POST', 'GET'])
def page_home():
    # cek sudah melakukan pencarian atau belum
    search = False
    # if any button clicked
    if request.method == 'POST':
        # sudah melakukan pencarian
        search = True
        # if button Indexing clicked
        if request.form['button'] == 'submit':
            # get input string
            inputQuery = request.form['query']
            # Prepare a cursor object using cursor() method
            cursor = database.db.cursor()
            # cek apakah query sudah pernah di inputkan
            cursor.execute(
                "SELECT `tbcache`.*, tbpaper.* FROM tbcache LEFT JOIN tbpaper ON tbcache.DocId = tbpaper.DocId WHERE tbcache.Query = '" + inputQuery.lower() + "' AND tbcache.Similiarity != 0 ORDER BY tbcache.Similiarity DESC")
            datacache = cursor.fetchall()
            rowcache = cursor.rowcount
            # jika query sudah pernah diinputkan, tampilkan hasilnya langsung dari tbcache
            if rowcache > 0:
                return render_template("home.html", search=search, Query=inputQuery,
                                       TotalDokumenMirip=rowcache, listDokumenMiripQuery=datacache)
            # jika query belum pernah diinputkan
            else:
                # start time execution
                startTimeSearching = time.time()
                # lakukan perhitungan kemiripan query dengan dokumen
                similiarity.doSimiliarity(inputQuery)
                # setelah dilakukan perhitungan, query pasti sudah ada di tbcache
                cursor.execute(
                    "SELECT `tbcache`.*, tbpaper.* FROM tbcache LEFT JOIN tbpaper ON tbcache.DocId = tbpaper.DocId WHERE tbcache.Query = '" + inputQuery.lower() + "' AND tbcache.Similiarity != 0 ORDER BY tbcache.Similiarity DESC")
                # ambil data cache baru
                newdatacache = cursor.fetchall()
                newrowcache = cursor.rowcount
                # end time execution
                endTimeSearching = time.time()
                cursor.execute("INSERT INTO `tbtime` (`Id`,`Process`,`Time`) VALUES (%s, %s, %s)",
                               ("NULL", "Searching", round(endTimeSearching - startTimeSearching, 0)))
                # commit database
                database.db.commit()
                print("Search Time : ", round(endTimeSearching - startTimeSearching, 0), " Detik")
                # jika query sudah pernah diinputkan dan hasilnya ada > 0 dokumen mirip
                if newrowcache > 0:
                    return render_template("home.html", search=search, Query=inputQuery,
                                           TotalDokumenMirip=newrowcache, listDokumenMiripQuery=newdatacache)
                # jika query sudah pernah diinputkan dan tidak ada dokumen mirip
                else:
                    return render_template("home.html", search=search, Query=inputQuery, TotalDokumenMirip=newrowcache)
    # render template with default viewpage
    return render_template("home.html", search=search)


# admin page
@app.route("/admin")
def page_admin():
    # Get data tabel paper
    datatabelpaper = database.getTabelPaper()
    # Prepare page with data
    return render_template("admin.html", value=datatabelpaper)


# preprocessing page
@app.route("/preprocessing", methods=['POST', 'GET'])
def page_preprocessing():
    factory = StemmerFactory()
    stemmer = factory.create_stemmer()
    # Get tabel preprocessing
    datatabelpreprocessing = database.getTabelPreprocessing()
    # If Any Button Clicked
    if request.method == 'POST':
        # Prepare a cursor object using cursor() method
        cursor = database.db.cursor()
        # If Button "Preprocessing" Clicked
        if request.form['button'] == 'Preprocessing':
            # start time execution
            startTimePreprocessing = time.time()
            # Empty table preprocessing
            cursor.execute("TRUNCATE `tbpreprocessing`")
            # Initiate Variabel to save data after preprocessing
            myList = []
            # get all data from tbpaper
            datapaper = database.getTabelPaper()
            # iterate data from database by row(i)
            for i in datapaper:
                # preprocess judul i=row | [2]=column judul
                judul = preprocess.doPreprocessing(i[2])
                # join string judul after split
                judul = " ".join(judul)
                stemjudul = stemmer.stem(judul)
                # preprocess judul i=row | [5]=column abstrak
                abstrak = preprocess.doPreprocessing(i[5])
                # join string abstrakafter split
                abstrak = " ".join(abstrak)
                stemabstrak = stemmer.stem(abstrak)
                # After preprocess insert id(i[0],judul,abstrak to list
                myList.append([i[0], stemjudul, stemabstrak])
            # insert to table preprocessing
            sqlinsert = "INSERT INTO `tbpreprocessing` (`DocId`,`Judul`,`Abstrak`) VALUES (%s, %s, %s)"
            # execute query
            cursor.executemany(sqlinsert, myList)
            # commit database
            database.db.commit()
            # Get new data after sql execute
            newdatapreprocess = database.getTabelPreprocessing()
            # end time execution
            endTimePreprocessing = time.time()
            cursor.execute("INSERT INTO `tbtime` (`Id`,`Process`,`Time`) VALUES (%s, %s, %s)",
                           ("NULL", "Preprocessing", round(endTimePreprocessing - startTimePreprocessing,0)))
            # commit database
            database.db.commit()
            print("Preprocessing Time : ", round(endTimePreprocessing - startTimePreprocessing,0), " Detik")
            # render template with new data after insert
            return render_template("preprocess.html", list=newdatapreprocess, total=len(newdatapreprocess))
        # If Button "Clear" Clicked
        else:
            # clear data table tbpreprocessing
            cursor.execute("TRUNCATE `tbpreprocessing`")
            # commit changes
            database.db.commit()
            # render template after table truncate
            return render_template("preprocess.html")
    # render template with default data on database
    return render_template("preprocess.html", list=datatabelpreprocessing, total=len(datatabelpreprocessing))


# indexing page
@app.route("/indexing", methods=['POST', 'GET'])
def page_indexing():
    # get data from database
    datatabelindex = database.getTabelIndexing()
    datatabelpreprocessing = database.getTabelPreprocessing()
    datatabelbobot = database.getTabelWeighting()
    # if any button clicked
    if request.method == 'POST':
        # Prepare a cursor object using cursor() method
        cursor = database.db.cursor()
        # if button Indexing clicked
        if request.form['button'] == 'Indexing':
            # start time execution
            startTimeIndexing = time.time()
            # Empty table index
            cursor.execute("TRUNCATE `tbindex`")
            # get all data from tb preprocessing
            cursor.execute("SELECT * FROM `tbpreprocessing`")
            # Get data after sql execute
            datatabelpreprocessing = cursor.fetchall()
            # iterate data by row
            for i in datatabelpreprocessing:
                # get doc id on column[0]
                doc_id = i[0]
                # join judul column[1] and abstrak column[2]
                judulabstrak = i[1] + " " + i[2]
                # do indexing process
                indexing.doIndexing(doc_id, judulabstrak)
            # get new data index after indexing process
            newdataindex = database.getTabelIndexing()
            newdataweight = database.getTabelWeighting()
            # end time execution
            endTimeIndexing = time.time()
            cursor.execute("INSERT INTO `tbtime` (`Id`,`Process`,`Time`) VALUES (%s, %s, %s)",
                           ("NULL", "Indexing", round(endTimeIndexing - startTimeIndexing, 0)))
            # commit database
            database.db.commit()
            print("Indexing Time : ", round(endTimeIndexing - startTimeIndexing, 0), " Detik")
            # render template with new data after insert
            return render_template("indexing.html", list=newdataindex, datapreprocess=len(datatabelpreprocessing),
                                   dataindex=len(newdataindex), dataweight=newdataweight)
        # if buttonWeighting clicked
        elif request.form['button'] == 'Weighting':
            # start time execution
            startTimeWeighting = time.time()
            # do weighting process
            indexing.doWeighting()
            # get new data index after weighting process
            newdataindex = database.getTabelIndexing()
            newdataweight = database.getTabelWeighting()
            # end time execution
            endTimeWeighting = time.time()
            cursor.execute("INSERT INTO `tbtime` (`Id`,`Process`,`Time`) VALUES (%s, %s, %s)",
                           ("NULL", "Weighting", round(endTimeWeighting - startTimeWeighting, 0)))
            # commit database
            database.db.commit()
            print("Weighting Time : ", round(endTimeWeighting - startTimeWeighting, 0), " Detik")
            # render template with new data after insert
            return render_template("indexing.html", list=newdataindex, datapreprocess=len(datatabelpreprocessing),
                                   dataindex=len(newdataindex), dataweight=newdataweight)
        # if button Clear Clicked
        else:
            # clear data on table index
            cursor.execute("TRUNCATE `tbindex`")
            # commit changes
            database.db.commit()
            # render template after table truncate
            return render_template("indexing.html", datapreprocess=len(datatabelpreprocessing), dataweight=0)
    # render template with default data on database
    return render_template("indexing.html", list=datatabelindex, datapreprocess=len(datatabelpreprocessing),
                           dataindex=len(datatabelindex), dataweight=datatabelbobot)


# vektor page
@app.route("/vektor", methods=['POST', 'GET'])
def page_vektor():
    # get data from database
    datatabelvektor = database.getTabelVektor()
    datatabelindex = database.getTabelIndexing()
    # if any button clicked
    if request.method == 'POST':
        # Prepare a cursor object using cursor() method
        cursor = database.db.cursor()
        # if button Vektor clicked
        if request.form['button'] == 'Vektor':
            # start time execution
            startTimeVektor = time.time()
            # Empty table vektor
            cursor.execute("TRUNCATE `tbvektor`")
            # do calculation of vector length
            vektor.doVektor()
            # get new data vector length
            newdatavektor = database.getTabelVektor()
            # end time execution
            endTimeVektor = time.time()
            cursor.execute("INSERT INTO `tbtime` (`Id`,`Process`,`Time`) VALUES (%s, %s, %s)",
                           ("NULL", "Vektor", round(endTimeVektor - startTimeVektor, 0)))
            # commit database
            database.db.commit()
            print("Vector Time : ", round(endTimeVektor - startTimeVektor, 0), " Detik")
            # render template after table insert
            return render_template("vektor.html", list=newdatavektor, dataindex=len(datatabelindex),
                                   datavektor=len(newdatavektor))
        # if button Clear Clicked
        else:
            # clear data table vektor
            cursor.execute("TRUNCATE `tbvektor`")
            # commit changes
            database.db.commit()
            # get new data vector length after truncate
            newdatavektor = database.getTabelVektor()
            # render template after table truncate
            return render_template("vektor.html", dataindex=len(datatabelindex), datavektor=len(newdatavektor))
    # render template with default data on database
    return render_template("vektor.html", list=datatabelvektor, dataindex=len(datatabelindex),
                           datavektor=len(datatabelvektor))


# cache page
@app.route("/cache", methods=['POST', 'GET'])
def page_cache():
    # Prepare a cursor object using cursor() method
    cursor = database.db.cursor()
    # get datacache from database
    cursor.execute(
        "SELECT `tbcache`.*, tbpaper.* FROM tbcache LEFT JOIN tbpaper ON tbcache.DocId = tbpaper.DocId ORDER BY tbcache.Id")
    datacache = cursor.fetchall()
    # if any button clicked
    if request.method == 'POST':
        # if button Clear clicked
        if request.form['button'] == 'Clear':
            # Empty table cache
            cursor.execute("TRUNCATE `tbcache`")
            # commit changes
            database.db.commit()
            # get new data cache
            cursor.execute(
                "SELECT `tbcache`.*, tbpaper.* FROM tbcache LEFT JOIN tbpaper ON tbcache.DocId = tbpaper.DocId ORDER BY tbcache.Id")
            newdatacache = cursor.fetchall()
            # render template after table truncate
            return render_template("cache.html", value=newdatacache)
    # render template with default data on database
    return render_template("cache.html", value=datacache)


# Testing page
@app.route("/pengujian", methods=['POST', 'GET'])
def page_pengujian():
    # Prepare a cursor object using cursor() method
    cursor = database.db.cursor()
    # select distinct query already used
    cursor.execute(
        "SELECT DISTINCT tbcache.Query FROM tbcache ORDER BY tbcache.Id DESC")
    dataquery = cursor.fetchall()
    # if any button clicked
    if request.method == 'POST':
        # if button Submit clicked
        if request.form['button'] == 'Submit':
            # get query selected
            queryselected = request.form.get('listquery')
            # select result of query
            cursor.execute(
                "SELECT tbcache.Query, tbpaper.DocId, tbpaper.Judul, tbpaper.Abstrak, tbcache.Similiarity, tbpaper.Url FROM tbcache INNER JOIN tbpaper ON tbcache.DocId=tbpaper.DocId WHERE tbcache.Query = '" + queryselected +"' ORDER BY tbcache.Similiarity DESC LIMIT 10;")
            datacache = cursor.fetchall()
            # render template after getting result
            return render_template("pengujian.html", dataquery=dataquery, datacache=datacache)
    # render template with default data on database
    return render_template("pengujian.html", dataquery=dataquery)


# demo page
@app.route("/demo", methods=['POST', 'GET'])
def page_demo():
    # if any button clicked
    if request.method == 'POST':
        # if button Submit clicked
        if request.form['button'] == 'Submit':
            # get input string
            inputteks = request.form['inputteks']
            # Do Preprocessing
            teksCaseFolding = preprocess.doLowerCase(inputteks)
            teksRemovePunc = preprocess.doRemovePunctuatuion(teksCaseFolding)
            teksRemoveNum = preprocess.doRemoveNum(teksRemovePunc)
            teksSplit = preprocess.doTokenization(teksRemoveNum)
            teksRemoveStopword = preprocess.doStopwordRemoval(teksSplit)
            # join string after split | and var for render template
            newtext = " ".join(teksRemoveStopword)
            # if string not null
            if newtext:
                # Do doDemoTextProcess
                # get dataindexdemo, newdataindexdemo, vektor from doDemoTextProcess function
                dataindexdemo, newdataindexdemo, vektor = demo.doDemoTextProcess(teksRemoveStopword)
                # render template with all new data
                return render_template("demo.html", teksCaseFolding=teksCaseFolding, teksRemoveNum=teksRemoveNum,
                                       teksRemoveStopword=newtext, dataindexdemo=dataindexdemo,
                                       newdataindexdemo=newdataindexdemo, vektor=vektor)
            # if string is null after textpreprocessing
            else:
                # render error template
                return render_template("demo.html", eror=1)
    # render default template
    return render_template("demo.html")


# error 404 page handling
@app.errorhandler(404)
# inbuilt function which takes error as parameter
def not_found(e):
    # defining function
    return render_template("404.html")


# Let's Play !
if __name__ == "__main__":
    app.run(debug=True, port=5004)
