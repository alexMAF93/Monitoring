#!/usr/bin/env python


from datetime import datetime


def script_description():
    return """
This is a script that does nothing

Usage:
    {} -h trololol 
    {}

WARNING when 2 > 3.
""".format(__file__, datetime.now())


def main():
    print(1)


if __name__ == "__main__":
    main()
