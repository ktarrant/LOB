import urllib2
from bs4 import BeautifulSoup

bbrefurl = "http://www.baseball-reference.com"

def getGameIds(year):
	# Get all the Date URL's from a Year
	contenturl = bbrefurl + "/boxes/%d.shtml" % year
	soup = BeautifulSoup(urllib2.urlopen(contenturl).read())

	# Seek to the month table
	tables = soup.findAll('table', attrs={"class": "calendar hcm-table"})
	# Collect the link to the play-by-play lists for each date. These links
	# will contain links to each game for that day.
	url_list = []
	for table in tables:
		for td in table.findAll("td"):
			link = td.find("a")
			if link == None: continue
			dateurl = bbrefurl + link.attrs["href"]
			url_list += [dateurl.encode("ascii")]
	return url_list

def getBoxUrls(dateurl):
	# Get all the games in the given dateurl
	# Download the page for this date
	soup = BeautifulSoup(urllib2.urlopen(dateurl).read())
	# Get all the links in this page
	links = soup.findAll("a")
	boxurls = []
	for link in links:
		# Only select links for play-by-play pages
		if not link.attrs["href"].startswith("/boxes"): continue

		box_url = bbrefurl + link.attrs["href"]
		boxurls += [box_url]
	return boxurls


def downloadPlayByPlay(contenturl, filename):
	# Scrape the play-by-play information from bbref and save it to a CSV
	soup = BeautifulSoup(urllib2.urlopen(contenturl).read())

	# Seek to the play-by-play table
	table = soup.find('table', attrs={'id': "play_by_play"})

	# Open up the result CSV file
	fobj = open(filename, "w")

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
	return filename

if __name__ == "__main__":
	# gameId = "WAS201504060"
	# contenturl = "http://www.baseball-reference.com/boxes/%s/%s.shtml" % (gameId[0:3], gameId)
	# filename = gameId + ".csv"
	getGameIds(2015)

	# testurl = "http://www.baseball-reference.com/play-index/st.cgi?date=2015-04-15"
	# urllib2.urlopen(testurl).read()
	
