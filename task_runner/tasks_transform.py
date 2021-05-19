import luigi
from luigi.contrib import postgres

from tasks_load import LoadData
from tasks_load import today_hash
from task_templates import PostgresQueryWithCredentials


class UpdateSkuTable(PostgresQueryWithCredentials):
    def requires(self):
        return LoadData()

    def output(self):
        id_postfix = today_hash()
        return postgres.PostgresTarget(self.host, self.database, self.user, self.password,
                                       self.table, update_id=f'{self.__class__.__name__}__{id_postfix}')
    table = 'sku'
    query = """ insert into sku
    select id, description
    from tmp
    where id not in (select distinct id from sku)"""


class UpdatePriceTable(PostgresQueryWithCredentials):
    def requires(self):
        return UpdateSkuTable()

    def output(self):
        id_postfix = today_hash()
        return postgres.PostgresTarget(self.host, self.database, self.user, self.password,
                                       self.table, update_id=f'{self.__class__.__name__}__{id_postfix}')

    table = 'price'
    query = """insert into price
    select id, price, load_date from tmp"""


class CleanTmp(PostgresQueryWithCredentials):
    def requires(self):
        yield UpdateSkuTable()
        yield UpdatePriceTable()

    def output(self):
        id_postfix = today_hash()
        return postgres.PostgresTarget(self.host, self.database, self.user, self.password,
                                       self.table, update_id=f'{self.__class__.__name__}__{id_postfix}')

    query = 'delete from tmp'


class TransformData(luigi.WrapperTask):
    def requires(self):
        return CleanTmp()
