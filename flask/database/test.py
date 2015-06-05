from hbasepull import RVIHBaseTable

table = RVIHBaseTable()

time1 = table.max_date('512423')
print time1

time2 = table.max_date('423132')
print time2

time3 = table.max_date('354676')
print time3
