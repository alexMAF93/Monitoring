#!/usr/bin/env python3


from optparse import OptionParser
import sys


def main():
    parser = OptionParser()
    parser.add_option("-r", "--read", dest = "to_read", help = "read from a file")
    parser.add_option("-w", "--write", dest = "to_write", help = "write to a file")
    (options, args) = parser.parse_args(sys.argv)
    if options.to_read:
        print('o sa citim')
    
    if options.to_write:
        print('o sa scriem')
    print(options, args)   


if __name__ == "__main__":
    main()

