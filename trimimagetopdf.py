#!/usr/bin/env python
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Trim the image and creates a PDF with the same size.

import argparse
import Image
from reportlab.pdfgen.canvas import Canvas
from PIL import Image, ImageChops, ImageFilter

PROGNAME = 'TrimImagetoPDF'
VERSION = '0.20171225'


def export_pdf(imgname, autotm, default_dpi, outfile, tformat, tleft, ttop, twidth, theight):
    """Trim the image and creates a PDF with the same size."""
    if outfile == '':
        outfile = '%s.pdf' % (imgname)
    outtrim = '%s-trim.' % (outfile)
    outtrim = outtrim + tformat
    pdf = Canvas(outfile, pageCompression=1)
    dpi = default_dpi
    im = Image.open(imgname)
    w, h = im.size
    width = round(w * 72.0 / dpi, 3)
    height = round(h * 72.0 / dpi, 3)
    pdf.setPageSize((width, height))
    if ((tleft < 0) or (ttop < 0) or (twidth < 0) or (theight < 0)):
        if autotm:
            trimbox = autocrop(im, 255)
        else:
            if im.mode == 'RGB':
                trimbox = trim(im, (255, 255, 255))
            else:
                trimbox = trim(im, 255)
    else:
        trimbox = (tleft, ttop, (tleft + twidth), (ttop + theight))
    if trimbox:
        print trimbox
        x1, y1, x2, y2 = trimbox
        wt = round((x2 - x1) * 72.0 / dpi, 3)
        ht = round((y2 - y1) * 72.0 / dpi, 3)
        x = round(x1 * 72.0 / dpi, 3)
        y = height - round(y2 * 72.0 / dpi, 3)
        trimim = im.crop(trimbox)
        trimim.save(outtrim)
        pdf.drawImage(outtrim, x, y, width=wt, height=ht)
    else:
        # found no content
        raise ValueError('cannot trim; image was empty')
    pdf.showPage()
    pdf.save()


def trim(im, border):
    bg = Image.new(im.mode, im.size, border)
    diff = ImageChops.difference(im, bg)
    bbox = diff.getbbox()
    return bbox


def autocrop(im, border):
    bw = im.convert('1')
    bw = bw.filter(ImageFilter.MedianFilter)
    bg = Image.new('1', im.size, border)
    diff = ImageChops.difference(bw, bg)
    bbox = diff.getbbox()
    return bbox


def print_version():
    print PROGNAME
    print VERSION


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Trim the image and creates a PDF with the same size')
    parser.add_argument(
        '-a',
        '--auto',
        action='store_true',
        default=False,
        help='autotrim, bw mode, default False')
    parser.add_argument(
        '-d',
        '--dpi',
        metavar='dpi',
        type=int,
        default=300,
        help='dpi for pdf output, default is 300')
    parser.add_argument(
        '-o',
        '--outfile',
        metavar='outfile',
        type=str,
        default='',
        help='output pdf name, default imgname.pdf')
    parser.add_argument(
        '-f',
        '--format',
        metavar='format',
        type=str,
        default='png',
        help='format trim image, default png')
    parser.add_argument(
        '-l',
        '--left',
        metavar='left',
        type=int,
        default=-1,
        help='use left, complit -ltwz, defaul -1')
    parser.add_argument(
        '-t',
        '--top',
        metavar='top',
        type=int,
        default=-1,
        help='use top, complit -ltwz, defaul -1')
    parser.add_argument(
        '-w',
        '--width',
        metavar='width',
        type=int,
        default=-1,
        help='use width, complit -ltwz, defaul -1')
    parser.add_argument(
        '-z',
        '--height',
        metavar='height',
        type=int,
        default=-1,
        help='use height, complit -ltwz, defaul -1')
    parser.add_argument(
        '-v',
        '--version',
        action='version',
        version=print_version())
    parser.add_argument('imgname', help='image file name')
    args = parser.parse_args()
    export_pdf(args.imgname, args.auto, args.dpi, args.outfile, args.format, args.left, args.top, args.width, args.height)
