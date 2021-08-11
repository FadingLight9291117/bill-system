from pathlib import Path
import abc


class BillDataSource(abc.ABC):
    @abc.abstractmethod
    def search_bill(self, year, month):
        ...


def _data_transform(data):
    return data


class FolderBillDatasource(BillDataSource):
    def __init__(self, bills_dir):
        self.bills_dir = bills_dir

    def search_bill(self, year, month):
        bill_file = Path(self.bills_dir) / f'{year}.{month}.txt'
        try:
            with bill_file.open('r', encoding='utf-8') as f:
                data = f.read()
            data = _data_transform(data)
            return data, True
        except IOError:
            return None, False
