try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

import time

class main():
    def __init__(self, input_xml):
        self.tree = ET.ElementTree(file=input_xml)
        self.root = self.tree.getroot()

        for elem in self.tree.iter():
            print(elem.tag, elem.attrib)




if __name__ == '__main__':
    start_time = time.time()
    app = main('Data/pubmed_result.xml')
    elapsed_time = time.time() - start_time
    print(elapsed_time)