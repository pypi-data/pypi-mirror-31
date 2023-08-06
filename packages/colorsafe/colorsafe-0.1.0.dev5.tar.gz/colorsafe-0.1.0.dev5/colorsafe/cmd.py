#!/usr/bin/python

from csdecoder import ColorSafeDecoder
from csencoder import ColorSafeEncoder
import argparse

def encode(args):
    ColorSafeEncoder(args.filename, args.colorDepth, args.pageHeight, args.pageWidth, args.borderTop, args.borderBottom,
                     args.borderLeft, args.borderRight, args.dotFillPixels, args.pixelsPerDot, args.printerDpi,
                     args.saveImages)

def decode(args):
    ColorSafeDecoder(args.filenames, args.colorDepth, args.outfile, args.saveMetadata)

def main():
    parser = argparse.ArgumentParser(description='A colorized data storage scheme for printing and scanning.')

    subparser = parser.add_subparsers()

    encoder_parser = subparser.add_parser('encode', \
                                help='Encode an input file, creates an output ColorSafe pdf file')

    encoder_parser.add_argument('filename', \
                                help='Input filename, supports any filetype')
    encoder_parser.add_argument('-c', '--colorDepth', type=int, default=1, choices=[1,2,3], \
                                help='Color depth')
    encoder_parser.add_argument('-df', '--dotFillPixels', type=int, default=3, \
                                help='Pixels per dot to be colored in')
    encoder_parser.add_argument('-pd', '--pixelsPerDot', type=int, default=4, \
                                help='Pixels per dot total')
    encoder_parser.add_argument('-di', '--printerDpi', type=int, default=100, \
                                help='Printed dots per inch')
    encoder_parser.add_argument('-ph', '--pageHeight', type=float, default=11, \
                                help='Height of output pages (in)')
    encoder_parser.add_argument('-pw', '--pageWidth', type=float, default=8.5, \
                                help='Height of output pages (in)')
    encoder_parser.add_argument('-bt', '--borderTop', type=float, default=0.2, \
                                help='Top border of output pages (in)')
    encoder_parser.add_argument('-bb', '--borderBottom', type=float, default=0.1, \
                                help='Bottom border of output pages (in)')
    encoder_parser.add_argument('-bl', '--borderLeft', type=float, default=0.1, \
                                help='Left border of output pages (in)')
    encoder_parser.add_argument('-br', '--borderRight', type=float, default=0.1, \
                                help='Right border of output pages (in)')
    encoder_parser.add_argument('--saveImages', action='store_true', default=False, \
                                help='Also output the individual png files')

    encoder_parser.set_defaults(func=encode)

    decoder_parser = subparser.add_parser('decode', \
                                           help='Decode a scanned ColorSafe image file')

    decoder_parser.add_argument('filenames', nargs='+', \
                                help='Input filenames, one or more scanned ColorSafe images')
    decoder_parser.add_argument('-c', '--colorDepth', type=int, default=1, choices=[1], \
                                help='Color depth')
    decoder_parser.add_argument('--outfile', type=str, default="outfile.txt", \
                                help='Output filename of data file')
    decoder_parser.add_argument('--saveMetadata', action='store_true', default=False, \
                                help='If specified, will save metadata')

    decoder_parser.set_defaults(func=decode)

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()

