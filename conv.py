#!/usr/bin/env python
__author__ = "Igor Stroh"
__version__ = "1.0"
import os
import sys
import shutil
from optparse import OptionParser

import pytils.translit
from BeautifulSoup import BeautifulStoneSoup
from BeautifulSoup import NavigableString
from BeautifulSoup import Tag


TEX_REPL = {
    '\\': '\\textbackslash{}',
    '{': '\\{{}',
    '}': '\\}{}',
    '$': '\\${}',
    '^': '\\^{}',
    '_': '\\_{}',
    '%': '\\%{}',
    '~': '\\textasciitilde{}',
    '#': '\\#{}',
    '&': '\\&{}',
}

DEVICE_PAPER_SIZES = {
    'PRS-500' : '90.6mm,122.4mm',
    'PRS-500-landscape' : '122.4mm,90.6mm',
    'JetBook' : '79mm,105mm',
    'JetBook-landscape' : '105mm,79mm',
    'iPhone' : '61mm,115mm',
    'iPhone-landscape' : '115mm,61mm',
}

def tag_text(tag):
    ret = []
    for c in tag.contents:
        if isinstance(c, NavigableString):
            ret.append(unicode(c))
    return u' '.join(ret)

def escape_tex(txt):
    return u''.join([unicode(TEX_REPL.get(i, i)) for i in txt])

class ConvError(Exception):
    pass

class NodeHandler(object):

    def __init__(self, converter):
        self.converter = converter

    def do_strong(self, node):
        if node.nodeType == Node.TEXT_NODE:
            return u'\\textbf{%s}' % escape_tex(node.data)
        return u'\\textbf{' + self.cascade(node) + u'}'


class Fb2TexConverter(object):

    tex_header_path = "header.tex"
    tex_footer_path = "footer.tex"
    tex_commands_path = "commands.tex"
    device = 'PRS-500'

    def __init__(self, fb2_file, workspace, **options):
        self.fb2_file = fb2_file
        self.workspace = workspace
        if 'tex_header_path' in options:
            self.tex_header_path = options['tex_header_path']
        if 'tex_footer_path' in options:
            self.tex_footer_path = options['tex_footer_path']
        if 'tex_commands_path' in options:
            self.tex_commands_path = options['tex_commands_path']
        if 'device' in options:
            if options['device'] not in DEVICE_PAPER_SIZES:
                raise ValueError("Unknown device: '%s'" % options['device'])
            self.device = device

    def _prepare_workspace(self):
        try:
            os.makedirs(self.workspace)
        except OSError, e:
            raise ConvError("Workspace at '%s' already exists!" % self.workspace)
        # copy tex files to workspace 
        shutil.copy(self.tex_header_path, self.workspace)
        shutil.copy(self.tex_footer_path, self.workspace)
        shutil.copy(self.tex_commands_path, self.workspace)

        self.tex_out = open(os.path.join(self.workspace, 'out.tex'), 'w')

    def convert(self):
        fp = self.fb2_file
        if isinstance(self.fb2_file, basestring):
            fp = open(self.fb2_file)
        self.soup = BeautifulStoneSoup(fp)
        self.root = self.soup.find('fictionbook')

        self.process_description()

    def process_description(self):
        desc = self.root.find('description')
        if not desc:
            print "no desc"
            return
        title_info = desc.find('title-info')
        if not title_info:
            print "no ti"
            return
        title = title_info.find('book-title')
        tag_text(title)

    def process_tag(self, tag):
        pass


if __name__ == '__main__':
    usage = "usage: %prog <fb2 input file>"
    parser = OptionParser()
    parser.add_option("-i", "--in", dest="fb2",
        help="Path to FB2 input file", metavar="FB2_FILE")
    parser.add_option("-o", "--out", dest="tex",
        help="Output tex file. If omitted the output will be written to STDOUT")
    parser.add_option("-w", "--workspace", dest="workspace",
        help="Workspace directory. If omitted a temp directory underneath /tmp will be used.")

    (options, args) = parser.parse_args()
    if len(args) != 1:
        print "ERROR: please provide an FB2 file"
        sys.exit(1)
    fb2_file = args[0]
    workspace = options.workspace

    c = Fb2TexConverter(fb2_file, '/tmp/adsf')
    #c.convert()
