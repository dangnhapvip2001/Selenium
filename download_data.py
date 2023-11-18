import undetected_chromedriver.v2 as uc
from selenium.webdriver.common.action_chains import ActionChains
import random
import time 
import os 
from glob import glob
import pandas as pd 
import chromedriver_autoinstaller as chromedriver
from bs4 import BeautifulSoup
chromedriver.install()
chrome_version = chromedriver.get_chrome_version().split('.')[0]

class Bot:
    def __init__(self, url, headless=True, credential=None):
        self.url = url
        self._create_folder()
        self.driver = self._init_driver(headless)
        self.credential = credential
        self.files = []

    def _create_folder(self):
        folder_name = self.url.split('/profile/')[-1]
        self.folder = folder_name.split('/')[0]
        if not os.path.exists(self.folder):
            os.makedirs(self.folder)
    
    def login(self, credential):
        url = 'https://www.researchgate.net/login'
        self.driver.get(url)
        time.sleep(random.randint(2,3))
        # Email
        self.driver.find_element('xpath', '//input[@id="input-login"]').send_keys(credential['email'])
        # Password
        self.driver.find_element('xpath', '//input[@id="input-password"]').send_keys(credential['password'])
        # btn login
        btn_login = self.driver.find_element('xpath', '//button[@data-testid="loginCta"]')
        ActionChains(self.driver).click(btn_login).perform()
        if 'login' in self.driver.current_url:
            return False 
        return True 

    def _init_driver(self, headless):
        options = uc.ChromeOptions()
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--start-maximized")
        options.add_argument("--incognito")
        if headless:
            options.add_argument("--headless")
        driver = uc.Chrome(options= options, version_main=chrome_version)
        params = {
            "behavior": "allow",
            "downloadPath": os.path.join(os.getcwd(), self.folder)
        }
        driver.execute_cdp_cmd("Page.setDownloadBehavior", params)
        return driver
        self.driver.get(self.url)
        a_elements = self.driver.find_elements('xpath', '//div[@class="nova-legacy-o-stack__item"]/div/a')
        category_urls = [a.get_attribute('href') for a in a_elements]
        with open('category.txt', 'w') as f:
            f.writelines([url.split('/')[-2] +'\n' for url in category_urls])
        for url in category_urls:
            self.crawl_page_by_category(url)

    def scroll_down(self):
        try:
            # Get scroll height
            last_height = self.driver.execute_script("return document.body.scrollHeight")

            while True:
                # Scroll down to bottom
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

                # Wait to load page
                time.sleep(random.randint(2,3))

                # Calculate new scroll height and compare with last scroll height
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
        except:
            pass

    def get_filename(self):
        pdf_files = glob(f'{self.folder}/*.pdf')
        for file in pdf_files:
            if file not in self.files:
                self.files.append(file)
                return file 
        return None 
    
    def extract_title_and_abstract(self):
        title = ''
        abstract = ''
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        strings = []
        # Preprocessing
        for string in soup.strings:
            string = string.replace('\n', '')
            string = string.strip()
            if string:
                strings.append(string)
        # Title
        for string in strings:
            if 'PDF' in string:
                title = string 
                break 
        for i in range(len(strings)):
            if 'Descriptions' in strings[i]:
                continue
            if 'Abstract' in strings[i] or 'Description' in strings[i]:
                abstract = strings[i+1]
                break 
        return title, abstract 

    def download_paper(self, paper_url):
        result = {'status': False, 'title': '', 'abstract': '', 'file': ''}
        self.driver.get(paper_url)
        titles = self.driver.find_elements('xpath', '//div[contains(@class, "nova-legacy-e-text--size-xl")]')
        if len(titles):
            result['title'] = titles[0].text
        try:
            result['abstract'] =  self.driver.find_element('xpath', '//div[@itemprop="description"]').text
        except Exception as ex:
            result['title'], result['abstract'] = self.extract_title_and_abstract()
            text = BeautifulSoup(self.driver.page_source, 'html.parser').text 
            if 'Request full-text' in text:
                result['file'] = 'Request full-text'
                print(f'{result["title"]} FAILURE (contact with authors to download)')
                return result
        

        papers = self.driver.find_elements('xpath', '//a[contains(@href, ".pdf")]')
        if len(papers) == 0:
            print(f'{paper_url.split("/")[-1]} FAILURE (contact with authors to download)')
            return result
        # Click download
        ActionChains(self.driver).click(papers[0]).perform()
        time.sleep(random.randint(2,3))
        filename = self.get_filename()
        retry = 0
        while not filename:
            if retry == 15:
                break
            filename = self.get_filename()
            print('Wating download . . . . . . . . . . . .')
            time.sleep(2)
            retry += 1
        result['file'] = filename
        result['status'] = True if filename else False 
        print(f'{result["title"]} {result["status"]}')
        return result 
    
    def run(self):
        if credential:
            if not self.login(credential):
                print('Login Fail')
                return False 
            else:
                research_url = os.path.join(self.url, 'research')
                self.driver.get(research_url)
                self.scroll_down()
        else:
            self.driver.get(self.url)
        # Get all paper url
        a_elements = self.driver.find_elements('xpath', '//div[@class="nova-legacy-v-publication-item__stack-item"]/div/a')
        paper_urls = [a.get_attribute('href') for a in a_elements if type(a.get_attribute('href')) == str and '/publication/' in a.get_attribute('href')]
        data = {'title': [], 'abstract': [],  'filename': []}
        print('Starting crawler . . . . . . . . . .')
        # Download paper
        for paper_url in set(paper_urls):
            result = self.download_paper(paper_url)
            data['title'].append(result['title'])
            data['abstract'].append(result['abstract'])
            data['filename'].append(result['file'])
        df = pd.DataFrame(data)
        return df.to_csv(f'{self.folder}_papers.csv', index=False)   

def crawl_papers(url, credential):
    print('Inting crawler . . . . . . . . . . . . . . . . . . .')
    bot = Bot(url=url, credential=credential, headless=False)
    bot.run()
    bot.driver.quit()

if __name__ == '__main__':
    credential = {
        'email': 'thanh.lk195917@sis.hust.edu.vn',
        'password': 'sieunhan1234'
    }
    crawl_papers(url='https://www.researchgate.net/profile/Vijender-Solanki', credential=credential)