#!/usr/bin/env python

__author__ = "Peter Somerville"
__email__ = "peterwsomerville@gmail.com"

from Tkinter import *
import os

def is_possible(word1,word2):
    """ check if word1 (containing wildcard chars)
        could possibly be word2 """    
    if len(word1)!=len(word2):
        return False     
    for i in xrange(len(word1)):
        if word1[i] not in "_?*":
            if word1[i] != word2[i]:
                return False
    return True

def containsLetters(subword, word):
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
                        
class Application(Frame):
    def __init__(self, master=None):
                                       
        Frame.__init__(self,master, bg="black")
        
        path = os.getcwd()
        self.pack()
        self.wordList = open(os.path.join(path,"words.txt")).readlines()
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
        self.results.delete(0,END)
        newWords = [w for w in self.wordList if is_possible(word,w.strip())]
        self.results.insert(END,"Found %d possible words" % len(newWords))
        self.results.insert(END,"Matching %s"%word)
        self.results.insert(END,"")
        # if any words, insert each into results 
        for w in newWords:
            self.results.insert(END,w.strip())
    
    def permLookup_a(self,event):
        """ call permLookup, passed event since used keyboard """
        self.permLookup()
               
    def permLookup(self):
        """ update results to show any words possible from the string
            of characters entered by user up to len(word)
        """
        word = self.myString.get().lower()
        self.results.delete(0,END)
        
        newWords = []
        for key in self.histoDict.iterkeys():
            if containsLetters(key, word):
                newWords.extend(self.histoDict[key])
        newWords.sort(key=len)
        newWords.reverse()
        
        self.results.insert(END,"Found %d Words" % len(newWords))
        self.results.insert(END,"From %s [%d]" % (word,len(word)))
        self.results.insert(END,"")
        for w in newWords:
            self.results.insert(END,w.strip()+" [%d]"%len(w))
        
    def checkWord_a(self,event):
        """ helper function for checking word with keyboard
        """
        self.checkWord()
                
    def checkWord(self):
        """ update results to indicate whether users word is in the word list, 
            and therefore a valid crossword """
        
        word = self.myString.get().lower()
        self.results.delete(0,END) 
        wordlist=list(word)
        wordlist.sort()
        letters = "".join(wordlist)
        self.results.insert(END,word)
        if letters in self.histoDict and word in self.histoDict[letters]:
            self.results.insert(END,"IS a valid crossword")
        else:
            self.results.insert(END,"IS NOT a valid crossword")
            
    def quit_a(self,event):
        """ quit from keyboard, don't need the event """
        self.quit()
        
    def createWidgets(self):
        """ initialise and pack all required widgets """
        self.entryFrame = Frame(self,bd=2,bg="black")
        self.buttonFrame = Frame(self,bd=2,bg="black")
        self.resultsFrame = Frame(self,bd=2,bg="black")
       
        self.entryLabel = Label(self.entryFrame,text="Enter Letters and/or Wildcards",bg="black",fg="white")
        self.entryLabel.pack()
        self.myString = Entry(self.entryFrame,width=20)
        self.myString.pack()
        self.myString.focus_set()
       
        self.getPermsBttn = Button(self.buttonFrame,text="Get Perms", command=self.permLookup,width=10,bg="black",fg="white")
        self.getPermsBttn.bind("<Return>", self.permLookup_a)
        self.getPermsBttn.pack()
        self.checkWordBttn = Button(self.buttonFrame,text="Check Word", command=self.checkWord,width=10,bg="black",fg="white")
        self.checkWordBttn.bind("<Return>", self.checkWord_a)
        self.checkWordBttn.pack()
        self.getPossiblesBttn = Button(self.buttonFrame,text="Get Maybes", command=self.getPossible,width=10, bg="black",fg="white")
        self.getPossiblesBttn.bind("<Return>", self.getPossible_a)
        self.getPossiblesBttn.pack()
        self.quitButton = Button (self.buttonFrame, text="Quit",command=self.quit,width=10, bg="red", fg="white")
        self.quitButton.bind("<Return>", self.quit_a)
        self.quitButton.pack()
        
        # self.resultsFrame 
        self.scrollY = Scrollbar(self.resultsFrame,bg="black")
        self.scrollY.pack(side=RIGHT, fill=Y)
        self.results = Listbox(self.resultsFrame,bg="black",fg="white")
        self.results.pack()
      
        # link scrollbar to results 
        self.results.config(yscrollcommand=self.scrollY.set)
        self.scrollY.config(command=self.results.yview)
        
        # pack frames
        self.entryFrame.pack()
        self.buttonFrame.pack()
        self.resultsFrame.pack()
              
def main():                           
   app = Application()
   app.master.title("Check Crosswords") 
                                       
   app.mainloop()

if __name__=="__main__":
   main()
