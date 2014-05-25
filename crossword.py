#!/usr/bin/env python
"""
crossword.py

- Check if a word is a word.
- Get words, sub-words and anagrams from a word or collection of letters.
- Get possible solutions if your potential solution has letters missing.
- for example "he__o"

Copyright (C) 2010-2014 Peter Somerville

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""

__author__ = "Peter Somerville"
__email__ = "peterwsomerville@gmail.com"

import os
import sys
import Tkinter as TK
import urllib2

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

class Application(TK.Frame):
    def __init__(self, words=None, master=None):

        self.api_key = "6c9c44d6-7216-4bfa-bdd8-ee1d3f8583fa" # ADD YOUR API KEY HERE 
        self.def_url = "http://www.dictionaryapi.com/api/v1/references/collegiate/xml/{0}?key={1}"
        self.got_remote = False
        if words is None:
            try:
                address = 'http://red2.sunderland.ac.uk/py/words.txt'
                print "trying to open remote word list at {}".format(address)
                request = urllib2.urlopen(address)
                self.word_list = request.read().split(' ')
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

        TK.Frame.__init__(self, master, bg="black", width=200)

        self.pack()
        self.histo_dict = self.get_histos()
        self.create_widgets()

    def get_histos(self):
        """ sort word list into a dictionary of histograms
            with all anagrams, stored in same key
        """

        histo_dict = dict()
        for word in self.word_list:
            letters = ''.join(sorted(word))
            if letters in histo_dict:
                histo_dict[letters].append(word)
            else:
                histo_dict[letters] = [word]
        return histo_dict

    def get_possible_a(self, event):
        self.get_possible()

    def get_possible(self):
        """update results to display any possible matches for user's string
            of characters and wildcard symbols
        """

        word = self.my_string.get().lower()
        self.clear_widget(self.results)
        if not word.strip():
            self.results.insert(TK.END, "Enter a possible...")
        else:
            new_words = [w for w in self.word_list if self.is_possible(word, w)]
            self.results.insert(TK.END,
                                "Found {} possible words".format(len(new_words)))
            self.results.insert(TK.END,
                                "Matching {}".format(word))
            self.results.insert(TK.END, "")
            # if any words, insert each into results
            for w in new_words:
                self.results.insert(TK.END, w)

    def is_possible(self, word1, word2):
        """ check if word1 (containing wildcard chars)
            could possibly be word2
        """

        if len(word1) != len(word2):
            return False
        for i, char in enumerate(word1):
            if char not in "_?*":
                if char != word2[i]:
                    return False
        return True


    def check_definitions(self, event):
        if self.api_key:
            selected = int(self.results.curselection()[0])
            if selected > 2:
                val = self.results.get(selected)
                if len(val.strip()) > 0 and len(val.split(" ")) == 1:
                    self.clear_widget(self.definitions)
                    try:
                        def_xml = urllib2.urlopen(self.def_url.format(val, self.api_key))
                        def_xml = ET.parse(def_xml)
                        entry_list = def_xml.getroot()
                        if entry_list[0].tag == 'suggestion':
                            tag_type = "suggestion(s)"
                            suggestions = True
                        else:
                            tag_type = 'matche(s)'
                            suggestions = False
                        header = "Found {0} {1} for {2}".format(len(entry_list), tag_type, val)
                        self.definitions.insert(TK.END, header)
                        for entry in entry_list:
                            if suggestions:
                                self.definitions.insert(TK.END, entry.text)
                            else:         
                                ew = entry.find('ew').text # word from def
                                fl = entry.find('fl').text
                                self.definitions.insert(TK.END, " ")
                                self.definitions.insert(TK.END, "{0} <{1}>".format(ew, fl))
                                self.definitions.insert(TK.END, " ")
                                entry_def = entry.find('def')
                                for dt in entry_def.iter('dt'):
                                    if dt.text.strip(":").strip():
                                        self.definitions.insert(TK.END, dt.text)
                    except urllib2.URLError, e:
                        self.clear_widget(self.definitions)
                        self.definitions.insert(TK.END, "{} error connecting to internet".format(e.getcode()))
        else:
            self.clear(self.definitions)
            self.definitions.insert(TK.END, "No dictionaryapi.com key: see README.MD")

    def clear_widget(self, widget):
        widget.delete(0, TK.END)

    def clear_entry(self):
        self.clear_widget(self.my_string)

    def clear_entry_a(self, event):
        self.clear_entry()

    def perm_lookup_a(self, event):
        self.perm_lookup()

    def perm_lookup(self):
        """ update results to show any words possible from the string
            of characters entered by user up to len(word)
        """

        word = self.my_string.get().lower()
        self.clear_widget(self.results)

        if not word.strip():
            self.results.insert(TK.END, "Enter some letters...")
        else:
            new_words = []
            for key in self.histo_dict.iterkeys():
                if self.contains_letters(key, word):
                    new_words.extend(self.histo_dict[key])
            new_words.sort(key=len)
            new_words.reverse()

            self.results.insert(TK.END,
                                "Found {} Words".format(len(new_words)))
            self.results.insert(TK.END,
                                "From {0} [{1}]".format(word, len(word)))
            self.results.insert(TK.END, "")
            for w in new_words:
                self.results.insert(TK.END,
                                    "{0} [{1}]".format(w.strip(), len(w)))

    def contains_letters(self, subword, word):
        """ check if subword is wholly contained in word """
        if len(subword) > len(word):
            return False
        word = list(word)
        for c in subword:
            try:
                i = word.index(c)
            except ValueError:
                return False
            word.pop(i)
        return True

    def check_word_a(self, event):
        """ helper function for checking word with keyboard """
        self.check_word()

    def check_word(self):
        """ update results to indicate whether users word is in the word list,
            and therefore a valid crossword """
        word = self.my_string.get().lower()
        is_word = False
        self.clear_widget(self.results)
        if not word.strip():
            self.results.insert(TK.END, "Enter a possible...")
        else:
            letters = "".join(sorted(word))

            if letters in self.histo_dict and word in self.histo_dict[letters]:
                result_str = "Yes {} IS a valid crossword".format(word)
                is_word = True
            else:
                result_str = "No {} IS NOT a valid crossword".format(word)
            self.results.insert(TK.END, result_str)
            if is_word:
                self.results.insert(TK.END, "\n")
                self.results.insert(TK.END, "\n")
                self.results.insert(TK.END, word)

    def quit_a(self, event):
        """ quit from keyboard, don't need the event """
        self.quit()

    def create_widgets(self):
        """ initialise and pack all required widgets """
        self.entry_frame = TK.Frame(self, bd=2, bg="black")
        self.btn_frame = TK.Frame(self, bd=2, bg="black")
        self.results_frame = TK.Frame(self, bd=2, bg="black")
        self.def_frame = TK.Frame(self, bd=2, bg="black")

        self.entry_lbl = TK.Label(self.entry_frame,
                                  text="Enter Letters and/or Wildcards",
                                  bg="black", fg="white")
        self.entry_lbl.pack()
        self.my_string = TK.Entry(self.entry_frame, width=40)
        self.my_string.pack()
        self.my_string.focus_set()

        self.get_perms_btn = TK.Button(self.btn_frame, text="Get Perms",
                                       command=self.perm_lookup, width=20,
                                       bg="black", fg="white")
        self.get_perms_btn.bind("<Return>", self.perm_lookup_a)
        self.get_perms_btn.pack()

        self.check_word_btn = TK.Button(self.btn_frame, text="Check Word",
                                        command=self.check_word, width=20,
                                        bg="black", fg="white")
        self.check_word_btn.bind("<Return>", self.check_word_a)
        self.check_word_btn.pack()

        self.get_poss_btn = TK.Button(self.btn_frame, text="Get Maybes",
                                      command=self.get_possible, width=20,
                                      bg="black", fg="white")
        self.get_poss_btn.bind("<Return>", self.get_possible_a)
        self.get_poss_btn.pack()

        self.clear_btn = TK.Button(self.btn_frame, text="Clear Entry",
                                   command=self.clear_entry, width=20,
                                   bg="black", fg="white")
        self.clear_btn.bind("<Return>", self.clear_entry_a)
        self.clear_btn.pack()


        self.quit_btn = TK.Button(self.btn_frame, text="Quit",
                                  command=self.quit, width=20,
                                  bg="red", fg="white")
        self.quit_btn.bind("<Return>", self.quit_a)
        self.quit_btn.pack()

        # self.results_frame
        self.scroll_y = TK.Scrollbar(self.results_frame, bg="black")
        self.scroll_y.pack(side=TK.RIGHT, fill=TK.Y)
        self.results = TK.Listbox(self.results_frame, bg="black", fg="white", width=80)
        self.results.bind("<<ListboxSelect>>", self.check_definitions)
        self.results.pack()

        self.scroll_def_y = TK.Scrollbar(self.def_frame, bg="black")
        self.scroll_def_y.pack(side=TK.RIGHT, fill=TK.Y)
        self.definitions = TK.Listbox(self.def_frame, bg="black", fg="white", width=80)
        self.definitions.pack()

        # link scrollbar to results
        self.results.config(yscrollcommand=self.scroll_y.set)
        self.scroll_y.config(command=self.results.yview)

        self.definitions.config(yscrollcommand=self.scroll_def_y.set)
        self.scroll_def_y.config(command=self.definitions.yview)


        # pack frames
        self.entry_frame.pack()
        self.btn_frame.pack()
        self.results_frame.pack()
        self.def_frame.pack()


def main():
    if len(sys.argv) == 1:
        app = Application()
    else:
        app = Application(sys.argv[1])
    app.master.title("Check Crosswords")
    app.mainloop()

if __name__ == "__main__":
    main()
