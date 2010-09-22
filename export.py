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
Utilities for exporting data from Puppet Prince
"""

from __future__ import with_statement

# Communicate with the web
import urllib2
import urllib

# for the parsing
from BeautifulSoup import BeautifulSoup

# gui
from gui import PuppeteerApp
from tkFileDialog import asksaveasfilename
from Tkinter import END


web_page_to_grapevine = {
        'physical_traits': 'Physical',
        'negative_physical_traits': 'Negative Physical',
        'social_traits': 'Social',
        'negative_social_traits': 'Negative Social',
        'mental_traits': 'Mental',
        'negative_mental_traits': 'Negative Mental',
        'disciplines':  'Disciplines',
        'abilities':    'Abilities',
        'backgrounds':  'Backgrounds',
        'influences':   'Influences',
        'statuses':     'Status',
        'derangements': 'Derangements',
        'merits':       'Merits',
        'flaws':        'Flaws',
        'rituals':      'Rituals',
        'ritae':        'Rituals',
        'viniculums':   'Bonds',
        'healths':      'Health Levels',
}

valueless = ['derangements', 'rituals', 'ritae']


grapevine_traitlist_defaults = {
        "Physical": { 'abc':"yes",'display':"1"},
        "Social": { 'abc':"yes",'display':"1"},
        "Mental": { 'abc':"yes",'display':"1"},
        "Negative Physical": { 'abc':"yes",'negative':"yes","display":"1"},
        "Negative Social": { 'abc':"yes",'negative':"yes","display":"1"},
        "Negative Mental": { 'abc':"yes",'negative':"yes","display":"1"},
        "Status": { 'abc':"yes",'display':"1"},
        "Abilities": { 'abc':"yes",'display':"1"},
        "Influences": { 'abc':"yes",'display':"1"},
        "Backgrounds": { 'abc':"yes",'display':"1"},
        "Health Levels": { 'abc':"no",'display':"1"},
        "Bonds": { 'abc':"yes",'display':"1"},
        "Miscellaneous": { 'abc':"no",'display':"1"},
        "Derangements": { 'abc':"yes",'atomic':"yes","negative":"yes","display":"5"},
        "Disciplines": { 'abc':"no",'atomic':"yes","display":"5"},
        "Rituals": { 'abc':"no",'atomic':"yes","display":"5"},
        "Merits": { 'abc':"yes",'atomic':"yes","display":"4"},
        "Flaws": { 'abc':"yes",'atomic':"yes","negative":"yes","display":"4"},
        "Equipment": { 'abc':"yes",'display':"1"},
        "Locations": { 'abc':"yes",'atomic':"yes","display":"5"},
}

class PuppetUrlReader(object):
    def __init__(self, username, password):
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
        urllib2.install_opener(self.opener)

        values = {'login': username,
                  'password': password,
                  'remember_me': '0'}

        self.post('http://puppetprince.com/account/login', values)

    def post(self, url, values):
        params = urllib.urlencode(values)
        f = self.opener.open(url, params)
        data = f.read()
        f.close()

        with open('result.html', 'w') as writefile:
            writefile.write(data)

        return f

    def open(self, url):
        return self.opener.open(url)

def parse_page(soup, lines):
    from pprint import pprint, pformat
    def read_span(the_tag, contentsMatch):
        if contentsMatch in the_tag.contents:
            quantity = the_tag.findNextSibling('span', 'quantity')
            if len(quantity.contents) > 0:
                return quantity.contents[0]
            else:
                return ''
        else:
            return None
    simple_tag_list=['clan', 'sect', 'blood', 'willpower', 'nature', 'demeanor', 'conscience', 'courage']
    complicated_tag_list={'Humanity':'path', 'Self Control': 'selfcontrol'}
    tag_results = {}
    for span_tag in soup.findAll('span'):
        for t in simple_tag_list:
            tmp_result = read_span(span_tag, t.title())
            if tmp_result is not None:
                tag_results[t] = tmp_result
        for key, value in complicated_tag_list.iteritems():
            tmp_result = read_span(span_tag, key)
            if tmp_result is not None:
                tag_results[value] = tmp_result
        # Generation is also a background, so they conflict
        if 'Generation' in span_tag.contents:
            quantity = span_tag.findNextSibling('span', 'quantity')
            try:
                if span_tag.parent['id'].startswith('background'):
                    continue
            except:
                pass
            if len(quantity.contents) > 0:
                tmp_result = quantity.contents[0]
            else:
                tmp_result = ''
            tag_results['generation'] = tmp_result
    pprint(tag_results)
    name = soup.find('h1', id='character_name').contents[0]
    attributes = " ".join(["{}=\"{}\"".format(*v) for v in tag_results.iteritems()])
    pprint(attributes)
    lines.append("<vampire name=\"{}\" {}>".format(name, attributes))
    #print web_page_to_grapevine.keys()
    for target_id in web_page_to_grapevine.keys():
        traits = []
        tdiv = soup.find('div', id=target_id)
        if tdiv is None:
            #print "Could not find traitlist", target_id
            continue
        span_list = tdiv.findAll('p')
        for tspans in soup.find('div', id=target_id).findAll('p'):
            n = tspans.find('span', attrs={'class': 'name'}).contents
            v = tspans.find('span', attrs={'class':'quantity'}).contents
            if target_id in valueless:
                realv = '1'
            else:
                realv = v[0]
            #from pprint import pprint
            #pprint((n, realv))
            traits.append((n[0], realv))
        gn = web_page_to_grapevine[target_id]
        r = "  <traitlist name=\"{}\" abc=\"{}\" atomic=\"{}\" negative=\"{}\" display=\"{}\">".format(
                gn,
                grapevine_traitlist_defaults[gn].get('abc', 'yes'),
                grapevine_traitlist_defaults[gn].get('atomic', 'no'),
                grapevine_traitlist_defaults[gn].get('negative', 'no'),
                grapevine_traitlist_defaults[gn].get('display', '1'))
        lines.append(r)
        #from pprint import pprint
        #pprint(traits)
        lines.append("\n".join(["    <trait name=\"{}\" val=\"{}\"/>".format(*t) for t in traits]))
        lines.append("  </traitlist>")
                
    lines.append("</vampire>")
    return lines


class Exporter(PuppeteerApp):
    def __init__(self, root):
        super(Exporter, self).__init__(root)
        self.upload_button.configure(text="Export")

    def browse_for_file(self):
        filename = asksaveasfilename(filetypes=[("allfiles","*"),("Grapevine XML Gex Files","*.gex")])
        self.filetext.delete(0, END)
        self.filetext.insert(0, filename)

    def do(self):
        from pprint import pprint
        urlreader = PuppetUrlReader(self.username.get(), self.password.get())
        f = urlreader.open('http://puppetprince.com/met_characters')
        #f = open('Characters.htm', 'r')
        characters = {}
        try:
            soup = BeautifulSoup(f)
            for div in soup.findAll('div', 'met_character'):
                n = div.findNext('a')
                characters[n.contents[0]] = n['href'].split('/')[-1]
            pprint(characters)
        finally:
            f.close()

        self.print_status("Detected", len(characters), "characters")
        for key in characters.iterkeys():
            self.print_status(key)

        lines = []
        lines.append("<?xml version=\"1.0\"?>")
        lines.append("<grapevine version=\"3\">")

        for key, value in characters.iteritems():
            self.print_status("Reading", key)
            f = urlreader.open('http://puppetprince.com/met_characters/' + value)
            try:
                soup = BeautifulSoup(f)
                parse_page(soup, lines)
            finally:
                f.close()

        lines.append("</grapevine>")
        self.print_status("Writing", self.filetext.get())
        with open(self.filetext.get(), 'w') as outf:
            outf.writelines("\n".join(lines))
        self.print_status("Done")

if __name__ == '__main__':
    from Tkinter import Tk
    root = Tk()
    app = Exporter(root)
    root.title('Puppeteer Exporter')
    root.mainloop()
