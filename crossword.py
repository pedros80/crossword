#!/usr/bin/env python

__author__ = "Peter Somerville"
__email__ = "peterwsomerville@gmail.com"

import os
import sys

import Tkinter as TK
                        
class Application(TK.Frame):
    def __init__(self, words=None, master=None):
                                 
        if words is None:
            words_file_name = os.path.join(os.getcwd(), "words.txt")
        else:
            words_file_name = os.path.join(os.getcwd(), words)
        try:
            with open(words_file_name) as f:
               self.wordList = f.readlines()
        except IOError:
            print "IOError opening file; try again"
            sys.exit(1)

        TK.Frame.__init__(self,master, bg="black")
        
        self.pack()
        self.histoDict = self.getHistos()
        self.createWidgets()
         
    def getHistos(self):
        """ sort word list into a dictionary of histograms
            with all anagrams, stored in same key """
        histoDict = dict()
        for word in self.wordList:
            word = word.rstrip()
            temp = list(word)
            temp.sort()
            letters = ''.join(temp)
            if letters in histoDict:
                histoDict[letters].append(word)
            else:
                histoDict[letters] = [word]
        return histoDict
        
    def getPossible_a(self,event):
        """ just calls self.getPossible(), throw away event
            passed from keyboard """
        self.getPossible()
    
    def getPossible(self):
        """update results to display any possible matches for user's string
            of characters and wildcard symbols"""
            
        word = self.myString.get().lower() 
        self.results.delete(0, TK.END)
        newWords = [w for w in self.wordList if self.is_possible(word, w.strip())]
        self.results.insert(TK.END, "Found %d possible words" % len(newWords))
        self.results.insert(TK.END, "Matching %s"%word)
        self.results.insert(TK.END, "")
        # if any words, insert each into results 
        for w in newWords:
            self.results.insert(TK.END, w.strip())
    
    def is_possible(self, word1, word2):
        """ check if word1 (containing wildcard chars)
            could possibly be word2 """    
        if len(word1) != len(word2):
            return False     
        for i in xrange(len(word1)):
            if word1[i] not in "_?*":
                if word1[i] != word2[i]:
                    return False
        return True

    def permLookup_a(self,event):
        """ call permLookup, passed event since used keyboard """
        self.permLookup()
               
    def permLookup(self):
        """ update results to show any words possible from the string
            of characters entered by user up to len(word)
        """
        word = self.myString.get().lower()
        self.results.delete(0, TK.END)
        
        newWords = []
        for key in self.histoDict.iterkeys():
            if self.containsLetters(key, word):
                newWords.extend(self.histoDict[key])
        newWords.sort(key=len)
        newWords.reverse()
        
        self.results.insert(TK.END,"Found %d Words" % len(newWords))
        self.results.insert(TK.END,"From %s [%d]" % (word,len(word)))
        self.results.insert(TK.END,"")
        for w in newWords:
            self.results.insert(TK.END, w.strip() + " [%d]" % len(w))

    def containsLetters(self, subword, word):
        """ check if subword is wholly contained in word """
        if len(subword) > len(word):
            return False
        word = list(word)
        for c in subword:
            try:
                index = word.index(c)
            except ValueError:
                return False
            word.pop(index)
        return True


    def checkWord_a(self,event):
        """ helper function for checking word with keyboard
        """
        self.checkWord()
                
    def checkWord(self):
        """ update results to indicate whether users word is in the word list, 
            and therefore a valid crossword """
        
        word = self.myString.get().lower()
        self.results.delete(0, TK.END) 
        wordlist=list(word)
        wordlist.sort()
        letters = "".join(wordlist)
        self.results.insert(TK.END, word)
        if letters in self.histoDict and word in self.histoDict[letters]:
            self.results.insert(TK.END, "IS a valid crossword")
        else:
            self.results.insert(TK.END, "IS NOT a valid crossword")
            
    def quit_a(self,event):
        """ quit from keyboard, don't need the event """
        self.quit()
        
    def createWidgets(self):
        """ initialise and pack all required widgets """
        self.entryFrame = TK.Frame(self, bd=2, bg="black")
        self.buttonFrame = TK.Frame(self, bd=2, bg="black")
        self.resultsFrame = TK.Frame(self, bd=2, bg="black")
       
        self.entryLabel = TK.Label(self.entryFrame, text="Enter Letters and/or Wildcards", bg="black", fg="white")
        self.entryLabel.pack()
        self.myString = TK.Entry(self.entryFrame, width=20)
        self.myString.pack()
        self.myString.focus_set()
       
        self.getPermsBttn = TK.Button(self.buttonFrame, text="Get Perms", command=self.permLookup, width=10, bg="black", fg="white")
        self.getPermsBttn.bind("<Return>", self.permLookup_a)
        self.getPermsBttn.pack()
        self.checkWordBttn = TK.Button(self.buttonFrame, text="Check Word", command=self.checkWord, width=10, bg="black", fg="white")
        self.checkWordBttn.bind("<Return>", self.checkWord_a)
        self.checkWordBttn.pack()
        self.getPossiblesBttn = TK.Button(self.buttonFrame, text="Get Maybes", command=self.getPossible, width=10, bg="black", fg="white")
        self.getPossiblesBttn.bind("<Return>", self.getPossible_a)
        self.getPossiblesBttn.pack()
        self.quitButton = TK.Button (self.buttonFrame, text="Quit",command=self.quit, width=10, bg="red", fg="white")
        self.quitButton.bind("<Return>", self.quit_a)
        self.quitButton.pack()
        
        # self.resultsFrame 
        self.scrollY = TK.Scrollbar(self.resultsFrame, bg="black")
        self.scrollY.pack(side=TK.RIGHT, fill=TK.Y)
        self.results = TK.Listbox(self.resultsFrame, bg="black", fg="white")
        self.results.pack()
      
        # link scrollbar to results 
        self.results.config(yscrollcommand=self.scrollY.set)
        self.scrollY.config(command=self.results.yview)
        
        # pack frames
        self.entryFrame.pack()
        self.buttonFrame.pack()
        self.resultsFrame.pack()
              
def main():
    if len(sys.argv) < 2:
        app = Application()
    else:
        app = Application(sys.argv[1])
    app.master.title("Check Crosswords")
    app.mainloop()

if __name__=="__main__":
    main()