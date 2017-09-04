import xml.etree.ElementTree as ET
from datetime import date
import csv, time


class print_logger():
    def __init__(self):
        curDate = date.today()
        self.alreadyExtracted = open("already-extracted" + "_" + str(curDate) + ".txt", "w", encoding="utf-16")
        self.ignore = open("ignore" + "_" + str(curDate) + ".txt", "w", encoding="utf-16")
        self.logFile = open("Log_File_"+str(curDate)+".txt", "w", encoding='utf-16')

        self.csv = open("result_"+str(curDate)+".csv", 'w', encoding='utf-8', newline='')
        self.writer = csv.writer(self.csv)
        headers = ['Last Name', 'Fore Name', 'Email', 'Article Title', 'Article ID', 'Journal Title', 'Date', 'Keywordlist']

        self.writer.writerow(headers)

    def print_alreadyExtracted(self, emails):
        for email in emails:
            self.alreadyExtracted.write(email + '\n')
        self.alreadyExtracted.flush()

    def print_ignore(self, emails):
        for email in emails:
            self.ignore.write(email + '\n')
        self.ignore.flush()

    def print_log(self, logTxt):
        self.logFile.write(logTxt + '\n')
        self.logFile.flush()
        print(logTxt)

    def print_csv(self, dt):
        for i, row in enumerate(dt):
            self.writer.writerow(row)

    def close_all(self):
        self.alreadyExtracted.close()
        self.ignore.close()
        self.logFile.close()
        self.csv.close()

class xml2tree():
    def __init__(self, xml_file='D:/9_Github/5_Taaniel_Git/Data/pubmed_result2.xml'):
        tree = ET.parse(xml_file)
        self.root = tree.getroot()
        self.index_lst = []
        self.email_lst = []
        self.cnt = 0

        self.logger = print_logger()

        curDate = date.today()
        logTxt = "------------------------------ Scraping Started! --------------------------------\n" + \
                 "(Current Date: {})\n".format(curDate)
        self.logger.print_log(logTxt)

        self.alreadyExtracted = []
        self.ignore = []
        self.totalData = []

    def findEmail(self, root, level=0, tag=None, index=None):
        tag = tag[:] if tag else []
        index = index[:] if index else []
        if len(root) > 0:
            for i, child in enumerate(root):
                #self.logger.print_log(print_adv(child.tag, index, level))
                if child.tag == 'Affiliation':
                    rtrn = check_email(child.text)
                    if rtrn is not None:
                        self.index_lst.append(index)
                        self.email_lst.append(rtrn)
                        self.cnt += 1
                self.findEmail(child, level + 1, tag + [child.tag], index + [i])
        else:
            #self.logger.print_log(print_adv(root.text, index, level))
            pass

    def extractData(self):
        for i, index in enumerate(self.index_lst):
            try:
                Email = self.email_lst[i].strip('.')
                if 'email:' in Email:
                    Email = Email.replace('email:', '')
                if 'Email:' in Email:
                    Email = Email.replace('Email:', '')
            except:
                Email = ''
                continue


            if Email in self.alreadyExtracted:
                self.ignore.append(Email)
                continue
            else:
                self.alreadyExtracted.append(Email)

            try:
                LastName = select_elm(self.root, index[:-1]+[0]).text
            except:
                LastName = ''
            try:
                ForeName = select_elm(self.root, index[:-1] + [1]).text
            except:
                ForeName = ''
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
                   'JournalTitle:\t\t{5}\nDate:\t\t\t{6}\nKeywordList:\t\t{7}'\
                .format(LastName, ForeName, Email, ArticleTitle, ArticleID, JournalTitle,
                        str(date(int(Year),int(Month),int(Day))), ' , '.join(KeywordList))
            self.logger.print_log(pTxt)

            self.totalData.append([LastName, ForeName, Email, ArticleTitle, ArticleID, JournalTitle,
                                   str(date(int(Year),int(Month),int(Day))), " , ".join(KeywordList)])


    def saveData(self):
        self.logger.print_alreadyExtracted(self.alreadyExtracted)
        self.logger.print_ignore(self.ignore)
        self.logger.print_csv(self.totalData)
        self.logger.close_all()

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
    start_time = time.time()
    app = xml2tree()
    app.findEmail(app.root)
    app.extractData()
    app.saveData()

    elapsed_time = time.time() - start_time
    print(elapsed_time)
