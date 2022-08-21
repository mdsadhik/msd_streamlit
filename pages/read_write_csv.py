import pandas

df = pandas.read_csv(
	'ROLLOVER_DATA.csv'
)

df.to_csv('ROLLOVER_DATA_UPD.csv')

