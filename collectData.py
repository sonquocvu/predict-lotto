from bs4 import BeautifulSoup as Soup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
from sqlalchemy.orm import Session
from database import crud, schemas
from pathlib import Path
import re
import logging
import os

Path("log/").mkdir(parents=True, exist_ok=True)


class CollectWonNumbers:

    def __init__(self, Result, Type, db: Session):
        self.__Running = True
        self.Result = Result
        self.Date = []
        self.Type = Type
        self.db = db
        self.is_first_time = False
        self.lottoCrud = crud.Lotto()
        self.Url = {
            "Vietlott655": "https://vietlott.vn/vi/trung-thuong/ket-qua-trung-thuong/winning-number-655#top",
            "Vietlott645": "https://vietlott.vn/vi/trung-thuong/ket-qua-trung-thuong/winning-number-645#top",
            "HCM": "https://www.minhngoc.net.vn/ket-qua-xo-so/mien-nam/tp-hcm.html",
            "Vungtau": "https://www.minhngoc.net.vn/ket-qua-xo-so/xo-so-mien-nam/vung-tau.html",
            "Dongnai": "https://www.minhngoc.net.vn/ket-qua-xo-so/xo-so-mien-nam/dong-nai.html",
            "Tayninh": "https://www.minhngoc.net.vn/ket-qua-xo-so/mien-nam/tay-ninh.html",
            "Binhduong": "https://www.minhngoc.net.vn/ket-qua-xo-so/mien-nam/binh-duong.html",
            "Tiengiang": "https://www.minhngoc.net.vn/ket-qua-xo-so/mien-nam/tien-giang.html"
        }

        logPath = os.getcwd() + "\log"
        file = logPath + "\collect-{}.log".format(self.Type)
        try:
            if Path(file).is_file():
                os.remove(file)
        except PermissionError:
            pass

        formatter = logging.Formatter("%(asctime)s — %(levelname)s — %(funcName)s:%(lineno)d — %(message)s")
        HandlerDebug = logging.FileHandler(file)
        HandlerDebug.setLevel(logging.DEBUG)
        HandlerDebug.setFormatter(formatter)

        self.logger = logging.getLogger('__main__.' + __name__)
        self.logger.addHandler(HandlerDebug)
        self.logger.addHandler(HandlerDebug)
        self.logger.setLevel(logging.DEBUG)

    def Terminate(self):
        self.__Running = False

    def __CollectVietlottPage(self, LottoWebDriver, lastDay):
        is_last_result = True  # The newest result from website
        while self.__Running:
            # Waiting for page loaded successfully
            try:
                ElementPresent = EC.presence_of_element_located((By.ID, "divResultContent"))
                WebDriverWait(LottoWebDriver, 10).until(ElementPresent)
            except TimeoutException:
                self.logger.debug("The loading took much time")
                self.__CollectVietlottPage(LottoWebDriver, lastDay)

            Page = LottoWebDriver.page_source  # Read data into variable
            ParsedPage = Soup(Page, 'html.parser')

            for line in ParsedPage.find_all('tr', ):
                if '<th>' not in str(line):
                    # Looking for the dates
                    Date = re.findall('<td>([0-9]{2}/[0-9]{2}/[0-9]{4})</td>', str(line))[0]

                    # Looking for the results
                    Result = re.findall("\">([0-9]{2})<\/span>", str(line))
                    ResultList = []
                    for res in Result:
                        ResultList.append(int(res))

                    self.updateDb(Date, ResultList, is_last_result)

                    self.logger.info("The raw Result: {}".format(Result))
                    self.logger.info("The date {}: {}".format(Date, ResultList))

                    if datetime.strptime(Date, '%d/%m/%Y') <= lastDay:
                        self.logger.info("The collection reach the last day: {}".format(Date))
                        self.Terminate()
                        break
                    is_last_result = False

            LottoWebDriver.find_element(By.LINK_TEXT, "»").click()
            self.logger.info("Go to the next page.")

        self.logger.info("__CollectVietlottPage end")

    def __CollectTraditionalPage(self, LottoWebDriver, lastDay):
        is_last_result = True  # The newest result from website
        while self.__Running:
            # Waiting for page loaded successfully
            try:
                ElementPresent = EC.presence_of_element_located((By.CLASS_NAME, "waitting"))
                WebDriverWait(LottoWebDriver, 10).until(ElementPresent)
            except TimeoutException:
                logging.debug("The loading took much time")
                self.__CollectTraditionalPage(LottoWebDriver, lastDay)

            Page = LottoWebDriver.page_source  # Read data into variable
            ParsedPage = Soup(Page, 'html.parser')

            try:
                for line in ParsedPage.find_all('div', class_="box_kqxs"):
                    # Looking for the dates
                    Date = re.findall("html\">([0-9]{2}\/[0-9]{2}\/[0-9]{4})<\/a>", str(line))[0]
                    self.logger.info("The Date is: {}".format(Date))

                    # Looking for the results
                    Result = re.findall("data=\"[0-9]{6}\">([0-9]{6})<\/div>", str(line))[0]
                    self.logger.info("The Result is: {}".format(Result))
                    ResultList = []
                    for res in Result:
                        ResultList.append(int(res))

                    self.logger.info("The date {}: {}".format(Date, ResultList))
                    print("The date {}: {}".format(Date, ResultList))

                    #self.updateDb(Date, ResultList, is_last_result)

                    if datetime.strptime(Date, '%d/%m/%Y') <= lastDay:
                        self.logger.info("The collection reach the last day: {}".format(Date))
                        self.Terminate()
                        break
                    is_last_result = False

            except IndexError:
                self.logger.info("Do not crawl the result containing 5 numbers")
                self.Terminate()

            if self.Type == "HCM":
                LottoWebDriver.find_element(By.LINK_TEXT, "<<<").click()
            else:
                LottoWebDriver.find_element(By.LINK_TEXT, "<<").click()
            self.logger.info("Go to the next page.")

        self.logger.info("__CollectTraditionalPage end")

    def updateDb(self, Date, ResultList, is_newest_result):
        date = datetime.strptime(Date, '%d/%m/%Y')
        is_date_exist = self.lottoCrud.get_date(self.db, date, self.Type)
        if not is_date_exist:
            self.logger.info("Update Db for {} - {}".format(date, ResultList))
            if is_newest_result:
                self.lottoCrud.update_last_day(self.db, self.Type)
            res = schemas.LottoCreate(date=date, result=ResultList, is_last_day=is_newest_result)
            self.lottoCrud.create_result(self.db, res, self.Type)
        else:
            self.logger.info("The day is already exists, don't update Db")

    def get_last_day(self):
        lastDay = self.lottoCrud.get_last_day(self.db, self.Type)
        if not lastDay:
            if self.Type == "Vietlott655" or self.Type == "Vietlott645":
                lastDay = datetime(2017, 8, 1)
            else:
                lastDay = datetime(2008, 1, 6)
        else:
            lastDay = lastDay[0]
        return lastDay

    def Start(self):
        option = webdriver.ChromeOptions()
        option.add_argument('headless')
        LottoWebDriver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=option)
        LottoWebDriver.get(self.Url[self.Type])

        self.logger.info("Starting Collecting Data For {}".format(self.Type))
        self.logger.info("****************Please Wait****************")

        lastDay = self.get_last_day()

        if self.Type == "Vietlott655" or self.Type == "Vietlott645":
            self.__CollectVietlottPage(LottoWebDriver, lastDay)
        else:
            self.__CollectTraditionalPage(LottoWebDriver, lastDay)

        self.logger.info("Collect results from Db")
        ResultsFromDb = self.lottoCrud.get_results(self.db, self.Type)
        if ResultsFromDb:
            for res in ResultsFromDb:
                self.Result.append(res[0])
                self.logger.info(res[0])

        self.logger.info("Collect results successfully.")