from hbasepull import RVIHBaseTable

table = RVIHBaseTable()
historic_data = table.query_by_date('354676050295509', '1', '2')
print historic_data
