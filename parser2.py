#coding:utf-8
from html.parser import HTMLParser
import re
import http.client
import sys
import os

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
            self.Answer = data[5:]
        if self.pAnswer == True and data != "正确答案：":
            self.Answer = data[5:]
        if self.pChoice == True and self.QType == "Para":
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
    conn = http.client.HTTPConnection('172.25.54.72:8088')
    conn.request('GET', '/usercontrol/ajax.aspx?username=%d&pwd=%s&func=Login' % (stdNo, stdNo))
    r0 = conn.getresponse()
    cookie = r0.getheader('Set-Cookie')
    conn = http.client.HTTPConnection('172.25.54.72:8088')
    conn.request('GET', url, headers={'Cookie': cookie})
    r1 = conn.getresponse()
    s = r1.read()
    fsave = open("save.out", "a")
    fsave.write(s.decode('utf-8'))
    #print(s.decode('utf-8'))
    parser = MyHTMLParser()
    parser.feed(s.decode('utf-8'))
    parser.close()

def aLocal(url):
    fsock = open(url)
    s = fsock.read()
    fsock.close()
    parser = MyHTMLParser()
    parser.feed(s)
    parser.close()

def format_output(length = 80, answertype = 0, debug = 0):
    if debug == 0:
        outsave = sys.stdout
        fsock = open("output.txt", "w")
        sys.stdout = fsock
    if debug.__class__ == str:
        outsave = sys.stdout
        fsock = open(debug, "w")
        sys.stdout = fsock
    counter = 0
    print("".ljust(length,"="))
    print("I. 选择题：")
    print("".ljust(length,"-"))
    for j in range(1, 4):
        print("".ljust(length, "-"))
        print("PART", j)
        print("".ljust(length, "-"))
        for i in globals()["li_" + str(j)]:
            counter += 1
            print("%d. %s" % (counter, i[1]))
            if max([len(c) for c in i[2]]) < int(length / len(i[2])) and j == 1 or j == 3:
                print("".join([c.ljust(int(length / len(i[2]))) for c in i[2]]))
            else:
                for c in i[2]:
                    print(c)
            if answertype == 0:
                print("答案：", i[3])
            print("")
    print("".ljust(length,"="))
    print("II. 填空题：")
    print("".ljust(length,"-"))
    for i in li_4:
        counter += 1 
        print("%d. %s" % (counter, i[1]))
        if answertype == 0:
            print("答案：", i[3].replace("^", " "))
        print("")
    print("".ljust(length,"="))
    print("III. 完形：")
    print("".ljust(length,"-"))
    for i in li_5:
        counter += 1
        print("%d. %s" % (counter, i[1]))
        print(i[2][0])
        if answertype == 0:
            print("答案：", i[3].replace("^", " "))
        print("")
    if answertype == 1:
        counter = 0
        print("答案")
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


#for i in os.listdir():
#    if (i[-5:] == ".html" or i [-4:] == ".htm"):
#       aLocal(i)

for i in range(20):
    aConnection("http://172.25.54.72:8088/Exam/User_Exam_Single.aspx?wkey=SJ&planid=176&planname=%E5%A4%A7%E5%AD%A6%E8%8B%B1%E8%AF%AD%E5%B1%82%E6%AC%A1%EF%BC%92%E7%AC%AC%E4%B8%80%E5%AD%A6%E6%9C%9F%E7%BB%83%E4%B9%A0unit1%20&time=100&point=100&passpoint=60&module=%E5%8D%95%E5%8D%B7&pid=117&examkey=&isanswer=%E6%98%BE%E7%A4%BA&return=User_Test_Query.aspx", 000000000)
format_output(80, 1, "output.txt")

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
