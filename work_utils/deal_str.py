import re


def deal_str(txt):
    if txt:
        string = re.sub("\n|\r|\s|\t", "", txt)
    else:
        string = ''
    return string
