from hbasepull import RVIHBaseTable

table = RVIHBaseTable()

time1 = table.max_date('354676050295509')
print time1

time2 = table.max_date('354676050185981')
print time2

time3 = table.max_date('354676050293629')
print time3
