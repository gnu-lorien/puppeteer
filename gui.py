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

"""
Tk interface for Puppeteer tools
"""


# for the gui
from Tkinter import *
from tkFileDialog import askopenfilename

# for the threading
import time
import Queue
import threading
import sys

class PuppeteerApp(object):
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
        self.thread1= threading.Thread(target=self.do)
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
