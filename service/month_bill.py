from datetime import date
import yaml
from pathlib import Path

from data.datasource import FolderBillDatasource


class Bill:
    def __init__(self, bill_database):
        assert bill_database is not None, 'bill数据源不能为空'
        self.bill_database = bill_database

    def get_month_bill(self, year, month, pure_bills=False):
        """
            `pure_bills`默认为`False`，返回的是这个月账单的全部信息，
            如果为`True`，仅返回整个月的账单信息
        """
        assert year is not None, 'year不能为空'
        assert month is not None, 'month不能为空'

        bill_txt, ok = self.search_bill(year, month)
        if not ok:
            raise NoBillException(year, month)

        bill_dict = self.to_dict(bill_txt, year, month)

        if pure_bills:
            return self.get_all_bills(bill_dict)

        return bill_dict

    def search_bill(self, year, month):
        return self.bill_database.search_bill(year, month)

    def get_all_bills(self, month_bill: list) -> list:
        """
            获取这个月的全部账单
        """
        day_bills = []
        for bill in month_bill:
            bill_data = {
                'date': bill['date'],
                'items': bill['items'],
            }
            day_bills.append(bill_data)
        return day_bills

    def to_dict(self, txt, year, month):
        """
            手机备忘录上的账单转成dict格式;
            必须是某一个月的全部账单;
            格式
            {
                date: str,
                total: float,
                remarks: str,
                items: list[list[item, money]],
            }
        """
        assert type(txt) is str
        assert txt != ''
        assert year is not None
        assert month is not None

        dicts_data = []

        data = txt.strip().split('\n\n')

        for item in data:
            item_list = item.strip().split('\n')
            item_list = [item.strip() for item in item_list]
            day_data = {
                # 因为这里的格式是`6.20(100)``
                'date': f"{year}-{month}-{int(item_list[0].split('.')[1].split('(')[0])}",
                'total': 0.0,
                'remarks': '',
                'items': self.items_split(item_list[1:]),
            }
            day_data['total'] = self.compute_all_money(day_data['items'])

            dicts_data.append(day_data)

        return dicts_data

    def items_split(self, items):
        """
            @items: [
                'item money',
            ]
            将每日的账单分割成项目和金额
            分割前: `item money`
            分割后: [item: str, money: int]
        """
        assert type(items) is list, '`items` 必须是list'
        res = []
        for item in items:
            item = item.split(' ')
            res.append([
                item[0],
                # 防止某些条目金额漏掉了
                float(item[1] if len(item) == 2 else 0),
            ])
        return res

    def compute_all_money(self, items):
        total = 0
        for item in items:
            total += float(item[1])
        return total

    def get_bills(self, bills, year, month):
        dicts = self.to_dict(bills, year, month)
        all_bills = self.get_all_bills(dicts)
        meta_data_file = Path('../config/config.yaml')
        meta_data = yaml.load(meta_data_file.open(
            'r', encoding='utf-8'), Loader=yaml.FullLoader)

        item_names_dicts: dict = meta_data['item_name']
        total_items = {}
        for bill in all_bills:
            bill_name = bill[0]
            bill_money = bill[1]
            total_items.setdefault(bill_name, 0)
            total_items[bill_name] += bill_money

        class_total = {item: 0 for item in item_names_dicts.keys()}
        class_total['其他'] = 0

        all_total_item_name = []
        for value in item_names_dicts.values():
            all_total_item_name.extend(value)

        other_item_names = []
        for item in total_items.items():
            if item[0] in all_total_item_name:
                for first_name in item_names_dicts.keys():
                    if item[0] in item_names_dicts[first_name]:
                        class_total[first_name] += item[1]
            else:
                class_total['其他'] += item[1]
                other_item_names.append(item[0])

        other_items = {item_name: total_items[item_name]
                       for item_name in other_item_names}
        return self.compute_all_money(all_bills), class_total, other_items


class NoBillException(Exception):
    def __init__(self, year, month):
        self.year = year
        self.month = month

    def __str__(self):
        print(f'不存在{self.year}年{self.month}月的账单。')


if __name__ == '__main__':
    bills_path = '../bills'
    datasource = FolderBillDatasource(bills_path)
    bill = Bill(datasource)
    data = bill.get_month_bill(2021, 7)
