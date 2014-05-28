#!/usr/bin/python3
# coding:utf-8

import sys
if sys.version_info.major < 3:
    print("Please use Python 3 or above, you are using Python %d.%d.%d\n" % (sys.version_info.major, sys.version_info.minor, sys.version_info.micro))
    quit()

from html.parser import HTMLParser
import re
import http.client
import sys
import os
import urllib.parse
import time, platform, hashlib
import json

__author__ = "Luo Chenxing"
__copyright__ = "Copyright 2014, Luo Chenxing"
__credits__ = ["Luo Chenxing"]
__license__ = "GPLv3"
__version__ = "1.0.0"
__maintainer__ = "Luo Chenxing"
__email__ = "chenxing.luo@gmail.com"
__status__ = "Production"
__githubrepo__ = "chazeon/NJU-WangceFetcher"
__link__ = "https://github.com/chazeon/NJU-WangceFetcher"

fsock = open("conf.json")
settings = json.load(fsock)
fsock.close

li_1 = []
li_2 = []
li_3 = []
li_4 = []
li_5 = []

class MyHTMLParser(HTMLParser):
    ExamBody = False
    spanVerbatim = 0
    divVerbatim = 0
    ExamBody = False
    titleType = False
    questionVerbatim = 0
    enterQuestion = True
    inQuestion = False
    QType = ""
    QuestionPieces = []
    Question = ""
    inBody = ""
    inBodyVerbatim = 0
    questionStart = False
    Answer = ""
    Choices = []
    liQuestion = []
    qNo = False
    pAnswer = False
    pChoice = False
    pQuestion = False
    qNumber = ""
    bigType = ""

    def __init__(self):
        HTMLParser.__init__(self)
        self.ExamBody = False
        self.spanVerbatim = 0
        self.divVerbatim = 0
        self.ExamBody = False
        self.titleType = False
        self.questionVerbatim = 0
        self.enterQuestion = True
        self.inQuestion = False
        self.QType = ""
        self.QuestionPieces = []
        self.Question = ""
        self.inBody = ""
        self.inBodyVerbatim = 0
        self.questionStart = False
        self.Answer = ""
        self.Choices = []
        self.liQuestion = []
        self.qNo = False
        self.pAnswer = False
        self.pChoice = False
        self.qNumber = ""
        self.bigType = ""
    def handle_starttag(self, tag, attrs):
        if tag == "div" and ('class', 'QType') in attrs:
            self.inQuestion = True
        if tag == "div" and self.inQuestion:
            self.divVerbatim += 1
        if tag == "span" and ('id', 'ExamBody') in attrs:
            self.ExamBody = True
        if tag == "span" and self.ExamBody == True:
            self.spanVerbatim += 1
        if tag == "div" and ('class', 'QName') in attrs:
            self.questionVerbatim = True
        if tag == "div" and ('class', 'TypeTitle') in attrs:
            self.titleType = True
        if tag == "input" and self.QType == "Filling" and self.questionStart == False and self.inBody and self.qNo == False and ('type', 'button') not in attrs:
            self.QuestionPieces.append("______")
            # Prob1
        if tag == "div" and ('class', 'Body') in attrs:
            self.inBody = True
            self.inBodyVerbatim = self.divVerbatim
        if tag == "span" and self.inBody == True:
            self.qNo = True
        if tag == "div" and ('class', 'ShowAnswerDiv') in attrs and self.QType == "Para":
            self.pAnswer = True
            #Problem2
        if tag == "strong" and self.QType == "Para":
            self.pChoice = True
        if tag == "p" and self.QType == "Para" and self.pChoice == True:
            self.pChoice = False
            self.pQuestion = True
            
        
    def handle_endtag(self, tag):
        if tag == "span" and self.ExamBody == True:
            self.spanVerbatim -= 1
        if tag == "span" and self.spanVerbatim == 0:
            self.ExamBody = False
        if tag == "span" and self.questionVerbatim == True and self.questionStart == False:
            self.questionStart = True
        if tag == "div" and self.questionStart == True:
            self.questionStart = False
            self.questionVerbatim = False
        if tag == "div" and self.inBody == True and self.divVerbatim == self.inBodyVerbatim:
            self.inBody = False
        if tag == "div" and self.inQuestion:
            self.divVerbatim -= 1
            if self.divVerbatim == 0:
                self.inQuestion = False
                if self.QType == "Filling":
                    self.Question = "".join(self.QuestionPieces)
                self.liQuestion.append((self.QType, self.Question, self.Choices, self.Answer, self.bigType))
                #print(self.qNumber)
                self.QType = ""
                self.Question = ""
                self.QuestionPieces = []
                self.Choices = []
                self.Answer = ""
        if tag == "div" and self.titleType == True:
            self.titleType = False
        if tag == "span" and self.qNo == True:
            self.qNo = False
        if tag == "div" and self.pAnswer == True:
            self.pAnswer = False
        #if tag == "strong" and self.pChoice == True:
        #    self.pChoice = False
        #    self.pQuestion = True
        if tag == "div" and self.QType == "Para" and self.pQuestion == True:
            self.pQuestion = False
        
    def handle_data(self, data):
        if self.questionStart == True and self.titleType == False and self.QType == "Choices":
            self.Question = data[1:]
        if self.titleType == True:
            self.QType = self.getType(data)
            #print(self.QType)
            self.bigType = re.findall("(\d)", data)[0]
            #print(str(self.bigType))
        if self.inBody and self.questionStart == False and self.QType == "Choices" and self.qNo == False:
            self.Choices.append(data)
        if self.inBody and self.questionStart == False and self.QType == "Filling" and self.qNo == False:
            self.QuestionPieces.append(data)
        if re.search('正确答案：', data) != None:
            self.Answer = data.replace('正确答案：', '')
        if self.pAnswer == True and data != "正确答案：":
            self.Answer = data.replace('正确答案：', '')
        if self.pChoice == True and self.QType == "Para":
#            print(data)
            if self.Choices == []:
                self.Choices.append(data)
            else:
                self.Choices[0] += data
        if self.pQuestion == True and self.QType == "Para":
            #print(data)
            self.Question += data
        if self.qNo == True:
            self.qNumber = data

    def getType_old(self, data):
        if data == "第1部分：词汇(每题1分)":
            return "Choices"
        if data == "第2部分：难句(每题1分)":
            return "Choices"
        if data == "第3部分：理解(每题2分)":
            return "Choices"
        if data == "第4部分：填空(每题2分)":
            return "Filling"
        if data == "第5部分：完形填空(每题2分)":
            return "Para"
    def getType(self, data):
        f = re.findall("第(\d)部分", data)
        #print(f)
        if f[0] in ['1', '2', '3']:
            return "Choices"
        elif f[0] == '4':
            return "Filling"
        elif f[0] == '5':
            self.Choices = ['']
            return "Para"

    def close(self):
        HTMLParser.close(self)
        #print(self.liQuestion)
        global li_1, li_2, li_3, li_4, li_5
        counter = 0
        for aQuestion in self.liQuestion:
            if aQuestion[1] not in [i[1] for i in globals()['li_' + aQuestion[4]]]:
                counter += 1
                globals()['li_' + aQuestion[4]].append(aQuestion)
        print(counter)
        print("(%s)" % ",".join(str(len(globals()["li_"+str(i)])) for i in range(1, 6)))
        
def aConnection(url, stdNo):
    conn = http.client.HTTPConnection(globals()['settings']['url'])
    conn.request('GET', '/usercontrol/ajax.aspx?username=%d&pwd=%s&func=Login' % (stdNo, stdNo))
    r0 = conn.getresponse()
    cookie = r0.getheader('Set-Cookie')
    conn = http.client.HTTPConnection(globals()['settings']['url'])
    conn.request('GET', url, headers={'Cookie': cookie})
    r1 = conn.getresponse()
    s = r1.read()
    #fsave = open("save.out", "a")
    #fsave.write(s.decode('utf-8'))
#    print(s.decode('utf-8'))
    parser = MyHTMLParser()
    parser.feed(s.decode('utf-8'))
    parser.close()
    conn = http.client.HTTPConnection(globals()['settings']['url'])
    conn.request('GET', '/usercontrol/ajax.aspx?func=LoginOut', headers={'Cookie': cookie})
    r2 = conn.getresponse()
    s = r2.read()


def aLocal(url):
    fsock = open(url)
    s = fsock.read()
    fsock.close()
    parser = MyHTMLParser()
    parser.feed(s)
    parser.close()

def format_output(length = globals()['settings']["LineLength"], answertype = 0, debug = 0):
    if debug == 0:
        outsave = sys.stdout
        fsock = open("output.txt", "w")
        sys.stdout = fsock
    if debug.__class__ == str:
        outsave = sys.stdout
        fsock = open(debug, "w")
        sys.stdout = fsock
    counter = 0
    print(os.path.splitext(debug)[0])
    print("Updated: " + time.asctime())
    print("")
    facknow = open("acknow")
    acknow = facknow.read()
    facknow.close()
    platform_info = (
        #(" " + " ".join(platform.dist())).rjust(70, "."),
        (" " +__author__).rjust(length - 20, "."),
        (" " +platform.platform().replace("-", " ")).rjust(length - 10, "."),
        (" " + sys.version.replace("\n", "")).rjust(length - 8, "."),
        (" " + time.ctime(os.stat(__file__).st_mtime)).rjust(length - 20, "."),
        (" " +__license__).rjust(length - 17, "."),
        (" " + hashlib.md5(open(__file__).read().encode()).hexdigest()).rjust(length - 18, "."),
        (" " + hashlib.md5(open("conf.json").read().encode()).hexdigest()).rjust(length - 24, "."),
        (" " +__githubrepo__).rjust(length - 19, "."),
        (" " +__link__).rjust(length - 6, ".")
    )
    print(acknow % platform_info)
    print("".ljust(length,"="))
    print(globals()['settings']["SectionNames"][0])
    print("".ljust(length,"-"))
    for j in range(1, 4):
        print("".ljust(length, "-"))
        print("PART", j, globals()['settings']["Section1PartNames"][j - 1])
        print("".ljust(length, "-"))
        for i in globals()["li_" + str(j)]:
            counter += 1
            print("%d. %s" % (counter, i[1]))
            if max([len(c) for c in i[2]]) < int(length / len(i[2])) and (j == 1 or j == 3):
                sys.stdout = outsave
                #if j == 3: print(i, [c for c in i[2]] , int(length / len(i[2])))
                sys.stdout = fsock
                print("".join([c.ljust(int(length / len(i[2]))) for c in i[2]]))
            else:
                for c in i[2]:
                    print(c)
            if answertype == 0:
                print(globals()['settings']["AnswerName"], i[3])
            print("")
    print("".ljust(length,"="))
    print(globals()['settings']["SectionNames"][1])
    print("".ljust(length,"-"))
    for i in li_4:
        counter += 1 
        print("%d. %s" % (counter, i[1]))
        if answertype == 0:
            print(globals()['settings']["AnswerName"], i[3].replace("^", " "))
        print("")
    print("".ljust(length,"="))
    print(globals()['settings']["SectionNames"][2])
    print("".ljust(length,"-"))
    for i in li_5:
        counter += 1
        print("%d. %s" % (counter, i[1]))
#        try:
            #print(i[2][0])
#        except IndexError:
#            print("Index ERROR:" ,i)
        print(i[2][0])
        if answertype == 0:
            print(globals()['settings']["AnswerName"], i[3].replace("^", " "))
        print("")        
    if answertype == 1:
        counter = 0
        print(globals()['settings']["AnswerName"])
        for j in range(1, 4):
            for i in globals()["li_" + str(j)]:
                counter += 1
                print ("%d. %s" % (counter, i[3]))
        for i in li_4:
            counter += 1
            print("%d. %s" % (counter, i[3].replace("^", " ")))
        for i in li_5:
            counter += 1
            print("%s. %s" % (counter, i[3].replace("^", " ")))
    if debug == 0 or debug.__class__ == str:
        sys.stdout = outsave
        fsock.close()


for i in os.listdir():
    if (i[-5:] == ".html" or i [-4:] == ".htm"):
       aLocal(i)

#for i in range(1):
#    aConnection("/Exam/User_Exam_Single.aspx?wkey=SJ&planid=180&planname=%E5%B1%82%E6%AC%A13%E7%AC%AC%E4%B8%80%E5%AD%A6%E6%9C%9F%E7%BB%83%E4%B9%A0unit1%20&time=100&point=100&passpoint=60&module=%E5%8D%95%E5%8D%B7&pid=136&examkey=&isanswer=%E6%98%BE%E7%A4%BA&return=User_Test_Query.aspx", 131140045)
#format_output(80, 1, "u1_end.txt")
#format_output(80, 0, "u1_inline.txt")
li_1 = []
li_2 = []
li_3 = []
li_4 = []
li_5 = []

#for i in range(40):
#    aConnection("/Exam/" + joinExam(clientid, wkey, planid, planname, time, point, passpoint, module, pid, examkey, isanswer), 131190114)
#print(li_5)
#format_output(80, 1, "u4_end.txt")
#format_output(80, 0, "u4_inline.txt")
#li_1 = []
#li_2 = []
#li_3 = []
#li_4 = []
#li_5 = []




#for i in os.listdir():
#    if (i [-4:] == ".out"):
#        print(i)
#        aLocal(i)
#        format_output(80, 1, i[:2]+"_end.txt")
#        format_output(80, 0, i[:2]+"_inline.txt")
#        li_1 = []
#        li_2 = []
#        li_3 = []
#        li_4 = []
#        li_5 = []


def joinExam(clientid, wkey, planid, planname, time, point, passpoint, module, pid, examkey, isanswer):
    if module == "整卷": url="User_Exam.aspx"
    if module == "单卷": url="User_Exam_Single.aspx"
    dUrl = {    "wkey" : wkey,
        "planid": planid,
        "planname": planname,
        "time": time,
        "point": point,
        "passpoint": passpoint,
        "module": module,
        "pid": pid,
        "examkey": examkey,
        "isanswer": isanswer,
        "return": "User_Exam_Query.aspx",
    }
    return url + "?" + urllib.parse.urlencode(dUrl)
    
class ExamDirFecher(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.inManageList = False
        self.inItem = False
        self.title = ""
        self.liParseResult = []
        self.recTitle = False
        self.liTest = []
    def handle_starttag(self, tag, attrs):
        if tag == "div" and ("class", "ManageList") in attrs:
            self.inManageList = True
        if tag == "ul" and ("onmouseover", "this.style.backgroundColor='#f4fbf8'") in attrs and ("onmouseout", "this.style.backgroundColor='#ffffff'") in attrs:
            self.inItem = True
        if tag == "input" and ("value", "参加练习") in attrs:
            dFunction = dict(attrs)
            s = dFunction["onclick"]
            pattern = "joinExam\('([^,']*)','([^,']*)','([^,']*)','([^,']*)','([^,']*)','([^,']*)','([^,']*)','([^,']*)','([^,']*)','([^,']*)','([^,']*)'\);"
            t = re.findall(pattern, s)
            self.liParseResult = list(t[0])
            
        if tag == "li" and ("style", "width: auto;") in attrs and self.inItem == True:
            self.recTitle = True

    def handle_endtag(self, tag):
        if tag == "div" and self.inManageList == False:
            self.inManageList = False
        if tag == "li" and self.recTitle == True and self.inItem == True:
            self.recTitle = False
        if tag == "ul" and self.inItem == True:       
            self.inItem = False
            self.liTest.append((self.title.strip(), self.liParseResult))
            self.title = ""
            self.liParseResult = []
    def handle_data(self, data):
        if self.recTitle == True:
            self.title = data
    def close(self):
        HTMLParser.close(self)
        return self.liTest

def CommandUI():
    print("A Nanjing University English Only Test System Parser\n")
    print('''Copyright (C) 2014 Luo Chenxing
License GPLv3: GNU GPL version 3 <http://gnu.org/licenses/gpl.html>
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.
''')
    if globals()["settings"]["StudentNumber"] == 0:
        print("Please input number before Student Number:")
        stdNo_str = sys.stdin.readline().replace("\n", "")
        if stdNo_str == "":
            quit()
        stdNo = int(stdNo_str)
    else:
        stdNo = globals()["settings"]["StudentNumber"]
    conn = http.client.HTTPConnection(globals()['settings']['url'])
    conn.request('GET', '/usercontrol/ajax.aspx?username=%d&pwd=%s&func=Login' % (stdNo, stdNo))
    r0 = conn.getresponse()
    cookie = r0.getheader('Set-Cookie')
    conn = http.client.HTTPConnection(globals()['settings']['url'])
    conn.request('GET', '/Exam/User_Test_Query.aspx', headers={'Cookie': cookie})
    r1 = conn.getresponse()
    s = r1.read()
#    print(s.decode('utf-8'))
    parser = ExamDirFecher()
    parser.feed(s.decode('utf-8'))
    liTest = parser.close()
#    print(liTest)
    counter = 0
    for i in liTest:
        counter += 1
        print(str("[" + str(counter) + "]").ljust(3), i[0])
    if globals()["settings"]["DownloadPart"] == "":
        print("Please input number before title, seperate with a SPACE\n, (or 'a' for all) then ENTER:")
        inputChoice = input().replace('\n', '')
    else:
        inputChoice = globals()["settings"]["DownloadPart"]
    if inputChoice == "a":
        choice = range(len(liTest))
    else:
        choice = inputChoice.split()
        try:
            choice = [int(i) - 1 for i in choice]
        except ValueError:
            print("Input False")
            return
#    print(liTest)
    for i in choice:
        t1 = time.clock()
        for j in range(globals()["settings"]["RoundsOfFetch"]):
            #print(liTest[i][1])
#            print("/Exam/" + joinExam(*liTest[i][1]))
            aConnection("/Exam/" + joinExam(*liTest[i][1]), stdNo)
        format_output(80, 1, liTest[i][0] + "_end.txt")
        format_output(80, 0, liTest[i][0] + "_inline.txt")
        global li_1, li_2, li_3, li_4, li_5
        li_1 = []
        li_2 = []
        li_3 = []
        li_4 = []
        li_5 = []
        t2 = time.clock()

CommandUI()
