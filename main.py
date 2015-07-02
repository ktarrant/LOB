import download
from progressbar import Percentage, Bar, RotatingMarker, ETA, FileTransferSpeed, ProgressBar

def makeProgressBar(label, maximum):
	widgets = [label + ": ", Percentage(), ' ', Bar(marker=RotatingMarker()),
	           ' ', ETA(), ' ']
	pbar = ProgressBar(widgets=widgets, maxval=maximum).start()
	return pbar

year = 2015
print "Loading list of game date URLs for %d" % year
dateurls = download.getGameIds(year)
print "Found %d game date URLs!" % len(dateurls)
print "Loading the play-by-play URL lists for each game day"
pbar = makeProgressBar("Play-by-Play", len(dateurls))
boxurls = []
for i in range(len(dateurls)):
	boxurls += download.getBoxUrls(dateurls[i])
	pbar.update(i)
print "Found %d play-by-play URLs!" % len(boxurls)