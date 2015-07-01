import urllib2
from bs4 import BeautifulSoup

# Load the website and parse it with BeautifulSoup
gameId = "WAS201504060"
contenturl = "http://www.baseball-reference.com/boxes/%s/%s.shtml" % (gameId[0:3], gameId)
soup = BeautifulSoup(urllib2.urlopen(contenturl).read())

# Seek to the play-by-play table
table = soup.find('table', attrs={'id': "play_by_play"})

# Open up the result CSV file
fobj = open(gameId + ".csv", "w")

# First seek to the header listing
headers = [header.text for header in \
	table.find("thead").find("tr").findAll("th")]
fobj.write(", ".join(header.encode("ascii") for header in \
	headers) + "\n")

# Find all the rows in the table
body = table.find("tbody")
for row in table.findAll("tr"):
	# Select only the event rows
	try:
		rowId = row.attrs["id"]
	except KeyError:
		continue
	if not rowId.startswith("event"): continue

	# Select the columns of each row to get the data values
	columns = row.findAll("td")
	values = [column.text.replace(u",", u";") for column in columns]
	# Do some unicode cleanup
	values = [value.replace(u'\xa0', " ").encode("ascii") for value in values]
	fobj.write(", ".join(values) + "\n")

fobj.close()


