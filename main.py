import xml.etree.ElementTree as ET
from datetime import date

class xml2tree():
    def __init__(self, xml_file='Data/pubmed_result.xml'):
        tree = ET.parse(xml_file)
        self.root = tree.getroot()
        self.index_lst = []
        self.email_lst = []
        self.cnt = 0

        curDate = date.today()
        self.logFile = open("Log_File_"+str(curDate)+".txt", "w", encoding='utf-16')
        logTxt = "------------------------------ Scraping Started! --------------------------------\n" + \
                 "(Current Date: {})\n".format(curDate)
        self.print_log(logTxt)

    def print_log(self, logTxt):
        print(logTxt + '\n')
        self.logFile.write(logTxt + '\n')
        self.logFile.flush()

    def parse(self, root, level=0, tag=None, index=None):
        tag = tag[:] if tag else []
        index = index[:] if index else []
        if len(root) > 0:
            for i, child in enumerate(root):
                self.print_log(print_adv(child.tag, index, level))
                if child.tag == 'Affiliation':
                    rtrn = check_email(child.text)
                    if rtrn is not None:
                        self.index_lst.append(index)
                        self.email_lst.append(rtrn)
                        self.cnt += 1
                self.parse(child, level + 1, tag + [child.tag], index + [i])
        else:
            self.print_log(print_adv(root.text, index, level))
            pass

    def save_csv(self):
        for i, index in enumerate(self.index_lst):
            try:
                LastName = select_elm(self.root, index[:-1]+[0]).text
            except:
                LastName = ''
            try:
                ForeName = select_elm(self.root, index[:-1] + [1]).text
            except:
                ForeName = ''
            try:
                Email = self.email_lst[i].strip('.')
            except:
                Email = ''
            try:
                ArticleTitle = select_elm(self.root, index[:-3]+[1]).text
            except:
                ArticleTitle = ''
            try:
                JournalTitle = select_elm(self.root, index[:-3]+[0,2]).text
            except:
                JournalTitle = ''

            ArticleID = ''
            for elm in select_elm(self.root, [index[0]] + [1,2]):
                if elm.attrib['IdType'] == 'doi':
                    ArticleID = elm.text
                    break

            for elm in select_elm(self.root, [index[0]]+[1,0]):
                if elm.attrib['PubStatus'] == 'pubmed':
                    try:
                        Year = elm[0].text
                    except:
                        Year = ''
                    try:
                        Month = elm[1].text
                    except:
                        Month = ''
                    try:
                        Day = elm[2].text
                    except:
                        Day = ''
                    break

            KeywordList = []
            for elm1 in select_elm(self.root, index[0:2]):
                if elm1.tag == 'KeywordList':
                    for elm2 in elm1:
                        KeywordList.append(elm2.text.strip())
                    break


            pTxt = '\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~' \
                   '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n' \
                   '\nLastName:\t\t{0}\nForeName:\t\t{1}\nEmail:\t\t\t{2}\nArticleTitle:\t\t{3}\nArticleID:\t\t{4}\n' \
                   'JournalTitle:\t\t{5}\nYear:\t\t\t{6}\nMonth:\t\t\t{7}\nDay:\t\t\t{8}\nKeywordList:\t\t{9}'\
                .format(LastName, ForeName, Email, ArticleTitle, ArticleID, JournalTitle, Year, Month, Day, ' | '.join(KeywordList))
            self.print_log(pTxt)


def print_adv(tag, index, level):
    index_str = ','.join(str(i) for i in index)
    pTxt = "{0}├──{1}({2})".format('\t'*level, tag, index_str)
    return pTxt

def check_email(line):
    line = line.split(' ')
    for elm in line:
        elm = elm.strip()
        if '@' in elm and '.' in elm:
            return elm

    return None

def select_elm(node, index):
    result = node
    for i in index:
        result = result[i]
    return result

if __name__ == '__main__':
    app = xml2tree()
    app.parse(app.root)
    app.save_csv()
