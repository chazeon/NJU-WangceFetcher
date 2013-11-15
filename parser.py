# coding: utf-8
# python version: 3.0

import sys


if sys.version_info.major != 3:
    print("Require Python 3, Exited.")
    quit()


import html.parser
import re

ProbLi = []

class ChoicesProblem:
    Question = ""
    Choices = []
    Answer = ""

class AnswerProblem:
    Choices = ""
    Question = ""
    Answer = ""

class ParaProblem:
    Choices = ""
    Question = ""
    Answer = ""

class QuestionParser(html.parser.HTMLParser):
    t = ChoicesProblem()
    flag = ["", "", "", ""]
    
    count = 0
    #def __init__(self):
    #    self.flag1 = ""
    #    self.flag2 = ""
    #    self.flag3 = ""

    def handle_starttag(self, tag, attrs):
        if tag == "br":
            #print(tag)
            return
        self.count += 1
        #print("s " + tag + str(self.count))
        if tag == "div" and attrs[0] == ("class", "Body"):
            self.flag[0] = "Body"
        if tag == "div" and attrs[0] == ("class", "QName"):
            self.flag[1] = "QName"
        #if tag == "span":
            #self.flag[2] = "span"

    def handle_endtag(self, tag):
        if tag == "br":
            return
        self.count -= 1
        #if tag == "span":
        #    self.flag[2] = ""
        if tag == "div":
            if self.flag[1] == "QName":
                #print("xx")
                self.flag[1] = "Choices"
            elif self.flag[0] != "":
                self.flag[0] = ""
#        if self.count == 0 and self.t.Question != "":
#            global ProbLi
#            ProbLi.append(self.t)
#            print(self.t.Question)
#            print(self.t.Choices)
#            print(self.t.Answer)
#            self.t.Choices = []
#            self.t.Question = ""
#            self.t.Answer = ""
#        #print("e " + tag + str(self.count))
#        print(self.t.Question)
#        print(self.t.Choices)
#        print(self.t.Answer)
        #self.t.Choices = []
        #self.t.Question = ""
        #self.t.Answer = ""
        #print("e " + tag + str(self.count))

    def handle_data(self, data):
        #print("@TEST: " + data)
        #print(self.flag[1])
        #if self.flag[2] == "span":
            #print(self.flag)
            #return
        #    pass
        if self.flag[1] == "QName" :
            if data[0] == ":" or data[0] == "：":
                self.t.Question = data[1:]
            #print("QNAME " + data[1:])
        try:
            if self.flag[1] == "Choices" and data[1] == ".":
                self.t.Choices.append(data[2:])
        except IndexError:
            pass
            #self.flag[1] = ""
            #print("CHOICES" + data[2:])
        if data[:4] == "正确答案":
            #print(self.t.Question)
            self.t.Answer = data[5:]

            global ProbLi
            ProbLi.append(self.t)
            print(self.t.Question)
            print(self.t.Choices)
            print(self.t.Answer)
            print("")
            self.t.Choices = []
            self.t.Question = ""
            self.t.Answer = ""

#if __name__ == "__main__":
#    t = QuestionParser()
#    t.feed('<a href="google.com" href2="baidu.com">')
    
if __name__ == "__main__":
    fileout = 0
    if fileout == 1:
        fsock = open("log", "w")
        outsave = sys.stdout
        sys.stdout = fsock
    

    fsock = open("testeasy.html")
    s = fsock.read()
    #print(s)
    v = QuestionParser(strict = False)
    v.feed(s)
    v.close()
    
    if fileout == 1:
        sys.stdout = outsave
        fsock.close()
