import re
import errorModule


class FormatFile:
    __origin_regex = ''
    __trans_regex = ''
    __format_commands = []

    def __init__(self, string_command):
        try:
            result = self.__parse_command(string_command)
        except ValueError:
            raise ValueError
        else:
            try:
                self.__origin_regex = result["regex"]
            except ValueError:
                raise ValueError('Invalid format of regex')
            else:
                self.__trans_regex = self.__translate_regex(result["regex"])
                try:
                    self.__format_commands = self.__parse_format_commands(self, result["format_commands"])
                except ValueError:
                    raise ValueError('Invalid format of format commands')

    @staticmethod
    def __translate_regex(regex):
        # todo skontroluj potencialne nevhodne znaky v stringu

        regex = re.sub(r"\\", r'\\\\', regex)

        if re.search(r'[^%]\.[\*\+\|\)]', regex):
            raise ValueError

        ## . ktora spaja 2 regexi sa vymaze A.B => AB
        regex = re.sub(r'(?<!%)((%%)*)(\.)', '\1', regex)

        ## !
        regex = re.sub(r'([^%])!(\([\s\S]*?[^%]\))', r'\1[^\2]', regex)
        regex = re.sub(r'^!(\([\s\S]*?[^%]\))', r'[^\1]', regex)
        # osetrenie nevhodneho pouzitia ! (%a lebo sa meni na .)
        if re.match(r'(?<!%)((%%)*)(!(?=[.|!*+)]|%a))', regex) is not None:
            errorModule.error_regex()

        # nahradenie validneho negovania
        regex = re.sub(r'!%s', r'\S', regex)
        # regex = re.sub(r'!%a', r'[^.]', regex)
        # negacia iba s parnym poctom % (%! je znak ! nie negacia)
        regex = re.sub(r'(?<!%)((%%)*)(!%d)', r'\1[^\d]', regex)
        regex = re.sub(r'(?<!%)((%%)*)(!%l)', r'\1[^a-z]', regex)
        regex = re.sub(r'(?<!%)((%%)*)(!%L)', r'\1[^A-Z]', regex)
        regex = re.sub(r'(?<!%)((%%)*)(!%w)', r'\1[^a-zA-Z]', regex)
        regex = re.sub(r'(?<!%)((%%)*)(!%W)', r'\1[^\w]', regex)
        regex = re.sub(r'(?<!%)((%%)*)(!%t)', r'\1[^\t]', regex)
        regex = re.sub(r'(?<!%)((%%)*)(!%n)', r'\1[^\n]', regex)
        # negovanie 1 pismena
        regex = re.sub(r'(?<!%)((%%)*)!(.)', r'\1[^\3]', regex)

        # %s: \s == \t\n\r\f, potom vertical tab \v a stare \r\n
        # (?<!%)((%%)*) => matchuje len ak je parny pocet % pred znakom
        # \1 vracia ten string %
        regex = re.sub(r'(?<!%)((%%)*)%s', r'\1(\s|\r\n|\v)', regex)
        regex = re.sub(r'(?<!%)((%%)*)%a', r'\1.', regex)
        regex = re.sub(r'(?<!%)((%%)*)%d', r'\1[\d]', regex)
        regex = re.sub(r'(?<!%)((%%)*)%l', r'\1[a-z]', regex)
        regex = re.sub(r'(?<!%)((%%)*)%L', r'\1[A-Z]', regex)
        regex = re.sub(r'(?<!%)((%%)*)%w', r'\1[a-zA-Z]', regex)
        regex = re.sub(r'(?<!%)((%%)*)%W', r'\1\w', regex)
        regex = re.sub(r'(?<!%)((%%)*)%t', r'\1\t', regex)
        regex = re.sub(r'(?<!%)((%%)*)%n', r'\1\n', regex)
        # nahradenie komentarov specialnych znakov
        regex = re.sub(r'(?<!%)((%%)*)%([.|!*+()])', r'\1\\\3', regex)
        # speci nahradenie zakomentovaneho % tj. %%
        regex = re.sub(r'%%', r'%', regex)

        return regex

    @staticmethod
    def __parse_command(str_cmd):
        pom = ""
        output = {"regex": "", "format_commands": ""}
        # pom = re.match(r'\S*(?=\s+)', str_cmd)
        pom = str_cmd.partition("\t")
        if pom[0] != "":
            output["regex"] = pom[0]
        else:
            raise ValueError('Invalid format of regex')

        if pom[2] != "":
            output["format_commands"] = pom[2]
        else:
            raise ValueError('of format commands')

        return output

    @staticmethod
    def __parse_format_commands(self, format_cmd):

        open_out = ""
        close_out = ""

        for cmd in re.findall(r"[^\s,]+", format_cmd):
            if re.search(r"^bold$", cmd):
                open_out += "<b>"
                close_out = "</b>" + close_out
            elif re.search(r"^italic$", cmd):
                open_out += "<i>"
                close_out = "</i>" + close_out
            elif re.search(r"^underline$", cmd):
                open_out += "<u>"
                close_out = "</u>" + close_out
            elif re.search(r"^teletype$", cmd):
                open_out += "<tt>"
                close_out = "</tt>" + close_out
            elif re.search(r"^size:(\d+)$", cmd):
                open_out += "<font size=" + re.search(r'\d+', cmd).group() + ">"
                close_out = "</font>" + close_out
            elif re.search(r"^color:([a-fA-F0-9]+)$", cmd):
                open_out += "<font color=#" + re.search(r'color:([a-fA-F0-9]+)', cmd).group(1) + ">"
                close_out = "</font>" + close_out
            else:
                raise ValueError
        # poradie
        # output = self.__sort(format_cmd, output)

        return [open_out, close_out]

    @staticmethod
    def __validate_cmd(format_cmd, output):

        for key, value in output.iteritems():
            if key == "bold" and value:
                format_cmd = re.sub(r"bold(,[\t| ]*)?", "", format_cmd)
            if key == "italic" and value:
                format_cmd = re.sub(r"italic(,[\t| ]*)?", "", format_cmd)
            if key == "underline" and value:
                format_cmd = re.sub(r"underline(,[\t| ]*)?", "", format_cmd)
            if key == "teletype" and value:
                format_cmd = re.sub(r"teletype(,[\t| ]*)?", "", format_cmd)
            if key == "size" and value != "":
                format_cmd = re.sub(r"size:\[" + value + r"\](,[\t| ]*)?", "", format_cmd)
            if key == "color" and value != "":
                format_cmd = re.sub(r"color:\[" + value + r"\](,[\t| ]*)?", "", format_cmd)
        format_cmd = re.sub(r"[\t| ]*", "", format_cmd)
        format_cmd = re.sub(r"\n", "", format_cmd)
        if format_cmd != "":
            return False
        return True

    def get_regex(self):
        return self.__trans_regex

    def get_command(self):
        return self.__format_commands
