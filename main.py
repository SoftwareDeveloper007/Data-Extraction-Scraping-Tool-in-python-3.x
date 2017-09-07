import xml.etree.ElementTree as ET
from datetime import date
import csv, time
from openpyxl import Workbook


#--------------- Print and Save all log data --------------------------------------------------------------------------------
class print_logger():
    def __init__(self):
        curDate = date.today()

        #------------- 'already-extracted.csv' ------------------------------------------------------------------------------
        self.alreadyExtracted = open("already-extracted" + ".txt", "a", encoding="utf-16")

        #------------- 'ignore.csv' -----------------------------------------------------------------------------------------
        self.ignore = open("ignore" + ".txt", "a", encoding="utf-16")

        #------------- 'Log_File_.txt' --------------------------------------------------------------------------------------
        self.logFile = open("Log_File_"+str(curDate)+".txt", "w", encoding='utf-16')

        #------------- 'result_.csv' ----------------------------------------------------------------------
        self.csv = open("result_"+str(curDate)+".csv", 'w', encoding='utf-16', newline='')

        self.wb = Workbook()
        self.ws = self.wb.active
        headers = ['Last Name', 'Fore Name', 'Email', 'Article Title', 'Article ID', 'Journal Title', 'Date', 'Keywordlist']

        self.ws.append(headers)

    #------------- Write emails list to 'already_extract.txt' ---------------------------------------------------------------
    def print_alreadyExtracted(self, emails):
        for email in emails:
            self.alreadyExtracted.write(email + '\n')
        self.alreadyExtracted.flush()

    #------------- Write emails list to 'ignore.txt' ------------------------------------------------------------------------
    def print_ignore(self, emails):
        for email in emails:
            self.ignore.write(email + '\n')
        self.ignore.flush()

    #------------- Write log of process to 'Log_File_.txt' ------------------------------------------------------------------
    def print_log(self, logTxt):
        self.logFile.write(logTxt + '\n')
        self.logFile.flush()
        print(logTxt)

    #-------------- Save data to csv file -----------------------------------------------------------------------------------
    def print_xlsx(self, dt):
        curDate = date.today()
        for i, row in enumerate(dt):
            self.ws.append(row)
        self.wb.save("result_"+str(curDate)+".xlsx")

    #-------------- Close all files -----------------------------------------------------------------------------------------
    def close_all(self):
        self.alreadyExtracted.close()
        self.ignore.close()
        self.logFile.close()
        self.csv.close()

class main():
    def __init__(self, xml_file='Data/pubmed_result.xml'):
        # convert xml file to tree
        tree = ET.parse(xml_file)
        # get root of tree
        self.root = tree.getroot()
        self.index_lst = []
        self.email_lst = []
        self.cnt = 0

        # initialize print_logger class
        self.logger = print_logger()

        #
        curDate = date.today()
        logTxt = "------------------------------ Scraping Started! --------------------------------\n" + \
                 "(Current Date: {})\n".format(curDate)
        self.logger.print_log(logTxt)

        # initialize self.alreadyExtracted, self.ignore, self.totalData
        self.alreadyExtracted = []      # store all already extracted emails
        self.ignore = []                # store all ingored emails
        self.totalData = []             # store all extracted data

    #------ checks and finds if there is email using recursing repeation ----------------------------------------------------
    def findEmail(self, root, level=0, tag=None, index=None):
        tag = tag[:] if tag else []
        index = index[:] if index else []
        if len(root) > 0:
            for i, child in enumerate(root):
                #self.logger.print_log(print_adv(child.tag, index, level))
                # if tag name is 'Affiliation', check if there is email.
                # If there is email, append the index into self.index_lst
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

    #------- Extract all necessary data based on the result of email checks --------------------------------------------------
    def extractData(self):
        for i, index in enumerate(self.index_lst):
            try:
                Email = self.email_lst[i].strip('.') #eliminate unnecessary '.' from email
                # eliminate 'email:' or 'Email:' if it is contained in email
                if 'email:' in Email: # if 'email:' is contained in Email, 'email:' is eliminated
                    Email = Email.replace('email:', '')
                if 'Email:' in Email: # if 'Email:' is contained in Email, 'email:' is eliminated
                    Email = Email.replace('Email:', '')
            except:
                Email = ''
                continue

            # check if Email is in self.alreadyExtract or in self.ignore
            # if Email is in self.alreadyExtracted, but not in self.ignore, it is appended into self.ignore and go to next
            if Email in self.alreadyExtracted:
                if Email not in self.ignore:
                    self.ignore.append(Email)
                continue
            else: # if Email is not in self.alreadyExtracted, it is appended into self.alreadyExtracted
                self.alreadyExtracted.append(Email)

            # Last Name
            try:
                LastName = select_elm(self.root, index[:-1]+[0]).text
            except:
                LastName = ''

            # Fore Name
            try:
                ForeName = select_elm(self.root, index[:-1] + [1]).text
            except:
                ForeName = ''

            # Article Title
            try:
                ArticleTitle = select_elm(self.root, index[:-3]+[1]).text
            except:
                ArticleTitle = ''

            # Journal Title
            try:
                JournalTitle = select_elm(self.root, index[:-3]+[0,2]).text
            except:
                JournalTitle = ''

            # Article ID
            ArticleID = ''
            for elm in select_elm(self.root, [index[0]] + [1,2]):
                if elm.attrib['IdType'] == 'doi':
                    ArticleID = elm.text
                    break

            # Year, Month, Day
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

            # Keyword List
            KeywordList = []
            for elm1 in select_elm(self.root, index[0:2]):
                if elm1.tag == 'KeywordList':
                    for elm2 in elm1:
                        KeywordList.append(elm2.text.strip())
                    break

            # print extracted data
            year_month_day = str(date(int(Year),int(Month),int(Day))).split('-')
            yearStr = year_month_day[0]
            monthStr = year_month_day[1]
            dayStr = year_month_day[2]
            pTxt = '\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~' \
                   '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n' \
                   '\nLastName:\t\t{0}\nForeName:\t\t{1}\nEmail:\t\t\t{2}\nArticleTitle:\t\t{3}\nArticleID:\t\t{4}\n' \
                   'JournalTitle:\t\t{5}\nDate:\t\t\t{6}{7}{8}\nKeywordList:\t\t{9}'\
                .format(LastName, ForeName, Email, ArticleTitle, ArticleID, JournalTitle,
                        yearStr, monthStr, dayStr, ', '.join(KeywordList))
            self.logger.print_log(pTxt)

            self.totalData.append([LastName, ForeName, Email, ArticleTitle, ArticleID, JournalTitle,
                                   yearStr+monthStr+dayStr, " , ".join(KeywordList)])

    # Save all relevant emails and process of run, and then close all files.
    def saveData(self):
        self.logger.print_alreadyExtracted(self.alreadyExtracted)
        self.logger.print_ignore(self.ignore)
        self.logger.print_xlsx(self.totalData)
        self.logger.close_all()

# It is used for printing tree structure visually
def print_adv(tag, index, level):
    index_str = ','.join(str(i) for i in index)
    pTxt = "{0}├──{1}({2})".format('\t'*level, tag, index_str)
    return pTxt

# check if it is email or not
def check_email(line):
    line = line.split(' ')
    for elm in line:
        elm = elm.strip()
        if '@' in elm and '.' in elm:
            return elm

    return None

# select element from node by using index list
def select_elm(node, index):
    result = node
    for i in index:
        result = result[i]
    return result

if __name__ == '__main__':
    start_time = time.time()
    app = main()
    app.findEmail(app.root)
    app.extractData()
    app.saveData()

    elapsed_time = time.time() - start_time
    print(elapsed_time)
