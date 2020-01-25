# coding: utf-8
# Created on Fri Jul 19 22:47:11 2019
# @author: wahidari

import string
import database


# ubah string ke huruf kecil
def doLowerCase(MyString):
    return MyString.lower()


# hilangkan tanda baca
def doRemovePunctuatuion(MyString):
    for i in string.punctuation:
        MyString = MyString.replace(i, ' ')
    return MyString


# hilangkan angka
def doRemoveNum(MyString):
    for i in range(10):
        MyString = MyString.replace(str(i), '')
    return MyString


# pisahkan kalimat berdasarkan kata
def doTokenization(MyString):
    return MyString.split()


# hapus stopword
def doStopwordRemoval(MyString):
    # Prepare a cursor object using cursor() method
    cursor = database.db.cursor()
    # ambil data stopword
    cursor.execute("SELECT * FROM `tbstopword`")
    # simpan data stopword
    rowvalue = cursor.fetchall()
    # Initial Variabel to Save Stopword from Database as List
    stopwordlist = []
    # Iterate each row From Database
    for i in rowvalue:
        # Save Stopword from Database as List
        # rowvalue(i[1]) / stopword column
        stopwordlist.append(i[1])
    # Initial Variabel to Save String no stopword
    newString = []
    # cek kata di kalimat bukanlah stopword
    for word in MyString:
        # jika kata bukan stopword
        if word not in stopwordlist:
            # simpan kata tersebut di newString
            newString.append(word)
    return newString


# Do all preprocessing process
def doPreprocessing(myString):
    stringLower = doLowerCase(myString)
    stringRemovePunc = doRemovePunctuatuion(stringLower)
    stringNoNum = doRemoveNum(stringRemovePunc)
    stringSplit = doTokenization(stringNoNum)
    stringNoStopword = doStopwordRemoval(stringSplit)
    return stringNoStopword
