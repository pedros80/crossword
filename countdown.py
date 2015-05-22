import Tkinter as TK
import random
import os
import urllib2

class Application(TK.Frame):

   def __init__(self, words=None, master=None):


      self.address = 'https://raw.githubusercontent.com/eneko/data-repository/master/data/words.txt'
      self.vowels = set("aeiou")
      self.consonants = set("bcdfghjklmnpqrstvwxyz")
      self.large_numbers = set([25, 50, 75, 100])
      self.small_numbers = [1,1,2,2,3,3,4,4,5,5,6,6,7,7,8,8,9,9,10,10]
      
      self.get_word_list(words)
      self.get_conundrums()
      
      TK.Frame.__init__(self, master, bg="black", width=200)

      self.create_widgets()
      self.pack()


   def create_widgets(self):
      self.entry_frame = TK.Frame(self, bd=2, bg="black")
      self.btn_frame = TK.Frame(self, bd=2, bg="black")
      self.results_frame = TK.Frame(self, bd=2, bg="black")
      self.def_frame = TK.Frame(self, bd=2, bg="black")
      self.entry_frame.pack()
      self.btn_frame.pack()
      self.results_frame.pack()
      self.def_frame.pack()

   def get_conundrums(self):
      self.conundrums = [word for word in self.word_list if len(word) == 9]

   def get_a_conundrum(self):
      conundrum = list(random.choice(self.conundrums))
      print "".join(conundrum)
      random.shuffle(conundrum)
      return "".join(conundrum)

   def get_word_list(self, words):
      if words is None:
         try:
            print "trying to open remote word list at {}".format(self.address)
            request = urllib2.urlopen(self.address)
            self.word_list = request.read().split('\n')
            self.got_remote = True
            print "got remote word list"
         except urllib2.URLError, e:
            if e.getcode() == 404:
               print "remote word list not found"
            elif e.getcode == 409:
               print "opening remote word list timed out"
               words_file_name = os.path.join(os.getcwd(), "words.txt")
               print "trying to open word list {}".format(words_file_name)
      else:
         words_file_name = os.path.join(os.getcwd(), words)
         print "trying to open word list from {}".format(words_file_name)
         try:
            if not self.got_remote:
               with open(words_file_name) as f:
                  self.word_list = [line.rstrip() for line in f]
         except IOError:
            sys.exit("IOError opening file; try again")


def main():
   app = Application()
   app.master.title("Countdown")
   print len(app.word_list)
   print app.get_a_conundrum()
   app.mainloop()

if __name__ == '__main__':
   main()