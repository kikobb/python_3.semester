#
import re
import sys


class ArgParser:
    @staticmethod
    def arg_count():
        return len(sys.argv) - 1

    @staticmethod
    def arg_parse():
        "parameter je bez nazvu programu a navratova hodnota vracia asoc pole argum alebo false"

        arguments = sys.argv
        del arguments[0]
        table = {'help': False,
                 'format': '',
                 'input': '',
                 'output': '',
                 'br': False,
                 'valid': False}
        if ArgParser.arg_count() == 1 and arguments[0] == "--help":
            table['help'] = True
            table['valid'] = True
            return table

        for args in arguments:
            if re.match(r'--format=.*?', args) is not None:
                table['format'] = args[9:]
            else:
                if re.match(r'--input=.*?', args) is not None:
                    table['input'] = args[8:]
                else:
                    if re.match(r'--output=.*?', args) is not None:
                        table['format'] = args[9:]
                    else:
                        if re.match(r'--br.*?', args) is not None:
                            table['br'] = True
                        else:
                            table['valid'] = False
                            return table
        table['valid'] = True

    @staticmethod
    def dbg_print_tab(tab):
        print('TABULKA:\n')
        print('help:        ')
        if tab['help']:
            print('true\n')
        else:
            print('false\n')

        print('format:      ' + tab['format'] + '\n')
        print('input:       ' + tab['input'] + '\n')
        print('output:      ' + tab['output'] + '\n')

        print('br:        ')
        if tab['br']:
            print('true\n')
        else:
            print('false\n')

        print('valid:        ')
        if tab['valid']:
            print('true\n')
        else:
            print('false\n')
