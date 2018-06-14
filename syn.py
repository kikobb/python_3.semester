import os
import re
import sys
import errorModule
import codecs
from classFormatFile import FormatFile


def arg_count():
    return len(sys.argv)


def arg_parse():
    arguments = sys.argv
    del arguments[0]
    table = {'help': False,
             'format': '',
             'input': '',
             'output': '',
             'br': False,
             'valid': False}
    if arg_count() == 1 and arguments[0] == "--help":
        table['help'] = True
        table['valid'] = True
        return table

    for args in arguments:
        if re.match(r'--format=.*?', args) is not None:
            if table['format'] != '':
                table['valid'] = False
                return table
            table['format'] = args[9:]
        else:
            if re.match(r'--input=.*?', args) is not None:
                if table['input'] != '':
                    table['valid'] = False
                    return table
                table['input'] = args[8:]
            else:
                if re.match(r'--output=.*?', args) is not None:
                    if table['output'] != '':
                        table['valid'] = False
                        return table
                    table['output'] = args[9:]
                else:
                    if re.match(r'--br.*?', args) is not None:
                        if table['br']:
                            table['valid'] = False
                            return table
                        table['br'] = True
                    else:
                        table['valid'] = False
                        return table
    table['valid'] = True
    return table


def print_help():
 print("""
                IPP: projekt_2 SYN
                Autor: Kristian Barna
                Login: xbarna02

 -----------------------------------------------------------
| --help = vypis napovedy                                   |
 -----------------------------------------------------------
| --input = soubor: vstupny \"soubor\"                      |
| --output = soubor: vystupny \"soubor\"                    |
| --dormat = soubor: vstupny formatovaci \"soubor\"         |
 -----------------------------------------------------------
| --br: za kazdy riadok dat < br / >                        |
 -----------------------------------------------------------
""")


def main():
    table = arg_parse()
    if table["valid"] == False:
        exit(1)
    # todo table['valid'] false
    if table['help']:
        print_help()

    else:

        # nacitanie formatovacieho suboru po ridkoch do pola

        # nacitanie vstupneho suboru
        input_file_arr = []

        if table["input"] == "":
            for riadok in sys.stdin:
                input_file_arr += list(riadok)
        else:
            if not os.path.isfile(table["input"]):
                exit(2)
            with open(table["input"]) as my_file:
                input_file_arr = my_file.read()
        out = ''.join(input_file_arr)

        if table["format"] != "":
            format_line_string_arr = []
            if not os.path.isfile(table["format"]):
                exit(2)
            with open(table["format"]) as my_file:
                for line in my_file:
                    line = line.strip()
                    format_line_string_arr.append(line)

            # rozparsovanie formatovacieho suboru
            format_line_obj_arr = []
            for line in format_line_string_arr:
                if line == '':
                    continue
                try:
                    format_line_obj_arr.append(FormatFile(line))
                except ValueError:
                    exit(4)

            # nahradenie
            open_tg = dict()
            close_tg = dict()
            for line in format_line_obj_arr:
                try:
                    reg = re.compile(line.get_regex())
                except re.error:
                    exit(4)
                for occure in reg.finditer(''.join(input_file_arr)):
                    if occure.group() != "":
                        bgn = occure.start()
                        end_tgs = occure.end()
                        if bgn in open_tg:
                            open_tg[bgn] += line.get_command()[0]
                        else:
                            open_tg[bgn] = line.get_command()[0]

                        if end_tgs in close_tg:
                            close_tg[end_tgs] += line.get_command()[1]
                        else:
                            close_tg[end_tgs] = line.get_command()[1]

            i = 0
            out = ''
            for c in input_file_arr:
                if i in open_tg:
                    out += open_tg[i]
                out += c
                if i + 1 in close_tg:
                    out += close_tg[i + 1]
                i += 1

        if table["br"]:
            out = re.sub('\\n', '<br />\n', out)

        if table["output"] != "":
            if re.search('/', table['output']) is not None:
                cesta = table['output'].split('/')
                cesta = cesta[:-1]
                cesta = '/'.join(cesta)
                if not os.path.isdir(cesta):
                    exit(3)
            write_file = open(table["output"], 'w')
            write_file.write(out)

main()