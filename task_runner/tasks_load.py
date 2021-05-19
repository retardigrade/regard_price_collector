import os
from datetime import date
import hashlib

import requests
import pandas as pd

import luigi
from luigi.contrib import postgres

from task_templates import PostgresCopyToTableWithCredentials, PostgresQueryWithCredentials

PRICELIST_URL = 'https://www.regard.ru/price/regard_priceList.xlsx'
DATA_DIR = 'data_files'
XLSX_PATH = os.path.join(DATA_DIR, 'pricelist.xlsx')
CSV_PATH = os.path.join(DATA_DIR, 'pricelist.csv')


def today_hash() -> str:
    date_byte = str(date.today()).encode('utf-8')
    hash_obj = hashlib.sha1(date_byte)
    hash_obj.update(date_byte)
    return hash_obj.hexdigest()


def files_missing(file_paths: list) -> bool:
    return all(not os.path.exists(file_path) for file_path in file_paths)


# TASKS
class CheckDir(luigi.Task):
    def output(self):
        return luigi.LocalTarget(DATA_DIR)

    def run(self):
        if DATA_DIR not in os.listdir('.'):
            os.mkdir(DATA_DIR)


class DownloadFile(luigi.Task):
    def requires(self):
        return CheckDir()

    def output(self):
        return luigi.LocalTarget(XLSX_PATH)

    def run(self):
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ' +
                                 'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.72 Safari/537.36'}
        session = requests.Session()
        pricelist_file = session.get(PRICELIST_URL, headers=headers)
        with open(XLSX_PATH, 'wb') as outfile:
            outfile.write(pricelist_file.content)


class ConvertFile(luigi.Task):
    def requires(self):
        return DownloadFile()

    def output(self):
        return luigi.LocalTarget(CSV_PATH)

    def run(self):
        df = pd.read_excel(XLSX_PATH, engine='openpyxl')
        df = df.iloc[16:, :].drop(columns=['Unnamed: 2', 'Unnamed: 4'])  # delete table header and useless columns
        df = df[df['Unnamed: 1'].notna()]  # select only goods rows
        df.iloc[:, 1] = df.iloc[:, 1].apply(lambda x: x.replace('"', ''))
        df.to_csv(CSV_PATH, index=False, header=False, sep='\t')


class LoadToDB(PostgresCopyToTableWithCredentials):
    def requires(self):
        return ConvertFile()

    def output(self):
        id_postfix = today_hash()
        return postgres.PostgresTarget(self.host, self.database, self.user, self.password,
                                       self.table, update_id=f'{self.__class__.__name__}__{id_postfix}')

    table = 'tmp'
    columns = [('id', 'INT'),
               ('description', 'TEXT'),
               ('price', 'INT')]

    def rows(self):
        with open(CSV_PATH, 'r', encoding='utf-8') as data:
            for line in data:
                yield list(line.strip('\n').split('\t'))


class WriteLoadDate(PostgresQueryWithCredentials):
    def requires(self):
        return LoadToDB()

    def output(self):
        id_postfix = today_hash()
        return postgres.PostgresTarget(self.host, self.database, self.user, self.password,
                                       self.table, update_id=f'{self.__class__.__name__}__{id_postfix}')

    query = f"UPDATE public.tmp SET load_date = '{date.today()}'"


class CleanUp(luigi.Task):
    def requires(self):
        return WriteLoadDate()

    def complete(self):
        return all([self.requires().complete(), files_missing(file_paths=[XLSX_PATH, CSV_PATH])])

    def run(self):
        try:
            os.remove(XLSX_PATH)
            os.remove(CSV_PATH)
        except FileNotFoundError:
            pass


class LoadData(luigi.WrapperTask):
    def requires(self):
        yield CleanUp()
