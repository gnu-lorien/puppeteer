#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#   Andrew Sayman Copyright 2010

from __future__ import with_statement

#TODO Properly merge influences into backgrounds

# Communicate with the web
import urllib2
import urllib

# Read Grapevine XML GEX file
from xml.sax.saxutils import quoteattr, unescape
from xml.sax import make_parser
from xml.sax.handler import feature_namespaces, property_lexical_handler
from xml.sax import ContentHandler
from xml.sax.saxutils import unescape, escape

# for the gui
from Tkinter import *
from tkFileDialog import askopenfilename

import time
import Queue
import threading
import sys

class PuppetPoster():
    traitlist_conversion = {
            'Physical': 'PhysicalTrait',
            'Social': 'SocialTrait',
            'Mental': 'MentalTrait',
            'Negative Physical': 'NegativePhysicalTrait',
            'Negative Social': 'NegativeSocialTrait',
            'Negative Mental': 'NegativeMentalTrait',
            'Disciplines': 'Discipline',
            'Abilities': 'Ability',
            'Backgrounds': 'Background',
            'Influences': 'Background',
            'Status': 'Status',
            'Derangements': 'Derangement',
            'Merits': 'Merit',
            'Flaws': 'Flaw',
            'Rituals': 'Ritual',
            'Bonds': 'Viniculum',
    }

    def __init__(self, username, password):
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
        urllib2.install_opener(self.opener)

        values = {'login': username,
                  'password': password,
                  'remember_me': '0'}

        self.post('http://puppetprince.com/account/login', values)

        self.character_id = None

    def post(self, url, values):
        params = urllib.urlencode(values)
        f = self.opener.open(url, params)
        data = f.read()
        f.close()

        with open('result.html', 'w') as writefile:
            writefile.write(data)

        return f

    def post_new_character(self, name):
        values = {'met_character[name]': name,
                  'met_character[type]': 'MetVampire'}
        f = self.post('http://puppetprince.com/met_characters/', values)
        self.character_id = f.geturl().split('/')[-2]

    def post_note(self, notes):
        pass
        #values = {'met_character[notes]': notes}
        #self.post('http://puppetprince.com/met_characters/' + self.character_id, values)

    def post_trait(self, attrs, traitlist):
        print "Posting into traitlist", traitlist
        # Convert traitlist name to 
        if 'val' in attrs:
            value = attrs['val']
        else:
            value = "1"
        values = {'type': PuppetPoster.traitlist_conversion[traitlist],
                  'trait[name]': attrs['name'],
                  'trait[quantity]': value}
        print "Posting trait", values
        self.post('http://puppetprince.com/met_characters/' + self.character_id + '/traits', values)

    def is_supported_traitlist(self, traitlist):
        return traitlist in PuppetPoster.traitlist_conversion


class PuppetLoader(ContentHandler):
    def __init__(self, poster, print_status):
        self.in_cdata = False
        self.fogliks = ''
        self.in_vampire = False
        self.current_traitlist = None
        self.poster = poster
        self.reading_note = False
        self.current_note = ''

        self.print_status = print_status

    def startElement(self, name, attrs):
        if name == 'vampire':
            self.in_vampire = True
            self.print_status('Creating new character', attrs['name'])
            self.poster.post_new_character(attrs['name'])

        if not self.in_vampire:
            return

        if name == 'notes':
            self.reading_note = True
            self.current_note = ''

        if name == 'traitlist':
            n = attrs['name']
            if self.poster.is_supported_traitlist(n):
                self.print_status('Reading traitlist', n)
                self.current_traitlist = n
            else:
                self.print_status('Skipping traitlist', n, '... not supported by Puppet Prince')

        if self.current_traitlist is None:
            return

        if name == 'trait':
            self.print_status("Reading trait", attrs['name'])
            self.poster.post_trait(attrs, self.current_traitlist)

    def endElement(self, name):
        if name == 'vampire':
            self.in_vampire = False
        if name == 'traitlist':
            self.current_traitlist = None
        if name == 'notes':
            self.poster.post_note(self.current_note)
            self.reading_note = False
            self.current_note = ''

    def characters(self, ch):
        if self.reading_note and self.in_cdata:
            self.current_note += ch
    def ignorableWhitespace(self, space):
        pass
    def startCDATA(self):
        self.in_cdata = True
    def endCDATA(self):
        self.in_cdata = False

    def startDTD(self):
        pass
    def endDTD(self):
        pass
    def comment(self, text):
        pass

    def error(self, exception):
        print 'Error'
        raise exception
    def fatalError(self, exception):
        print 'Fatal Error'
        raise exception
    def warning(self, exception):
        print 'Warning'
        raise exception


class mywidgets:
    def __init__(self,root):
        self.queue = Queue.Queue()
        self.root = root

        frame=Frame(root)

        self.username_label = Label(frame, text="Username")
        self.username_label.grid(row=1, column=0)
        self.username = Entry(frame)
        self.username.grid(row=1, column=1)

        self.password_label = Label(frame, text="Password")
        self.password_label.grid(row=2, column=0)
        self.password = Entry(frame, show="*")
        self.password.grid(row=2, column=1)

        self.browse_button = Button(frame, text="Browse for file", command=self.browse_for_file)
        self.browse_button.grid(row=3, column=0)
        self.filetext = Entry(frame)
        self.filetext.grid(row=3, column=1)

        self.innerFrame = Frame(frame)
        self.scrollbar = Scrollbar(self.innerFrame)
        self.status = Text(self.innerFrame, height=10, width=30, yscrollcommand=self.scrollbar.set)
        self.status.pack(side=LEFT)
        self.scrollbar.config(command=self.status.yview)
        self.scrollbar.pack(side=RIGHT, fill=BOTH, expand=1)
        self.innerFrame.grid(row=4, column=0, columnspan=2)

        self.quit_button = Button(frame, text="Quit", command=self.megadie)
        self.quit_button.grid(row=5, column=0)
        self.upload_button = Button(frame, text="Upload", command=self.upload)
        self.upload_button.grid(row=5, column=1)

        frame.grid()
        return

    def megadie(self):
        print "In megadie"
        sys.exit(0)

    def browse_for_file(self):
        filename = askopenfilename(filetypes=[("allfiles","*"),("Grapevine XML Gex Files","*.gex")])
        self.filetext.delete(0, END)
        self.filetext.insert(0, filename)

    def print_status(self, *args, **kwargs):
        self.queue.put((args, kwargs))

    def print_queued(self):
        while self.queue.qsize():
            try:
                args, kwargs = self.queue.get(0)
                for arg in args:
                    self.status.insert(CURRENT, str(arg))
                    self.status.insert(CURRENT, kwargs.get('sep', ' '))
                self.status.insert(CURRENT, kwargs.get('end', '\n'))
                self.status.see(CURRENT)
            except Queue.Empty:
                pass

    def upload(self):
        self.running = 1
        self.thread1= threading.Thread(target=self.do_upload)
        self.thread1.daemon = True
        self.thread1.start()
        self.upload_button.configure(state=DISABLED)

        self.periodicFlush()

    def periodicFlush(self):
        self.print_queued()
        if self.running:
            self.root.after(100, self.periodicFlush)
        else:
            self.upload_button.configure(state=ENABLED)

    def do_upload(self):
        try:
            poster = PuppetPoster(self.username.get(), self.password.get())
            loader = PuppetLoader(poster, self.print_status)
            parser = make_parser()
            parser.setContentHandler(loader)
            parser.setProperty(property_lexical_handler, loader)
            parser.parse(self.filetext.get())
        except:
            self.print_status("Caught an exception")
            import traceback
            self.print_status(traceback.format_exc())

if __name__ == '__main__':

    root = Tk()
    app = mywidgets(root)
    root.title('GXGPPU')
    root.mainloop()
