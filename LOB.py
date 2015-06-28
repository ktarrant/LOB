import re

scoreRe = re.compile("; (.+) Scores")

def extractTotals(fobj):
    for line in fobj:
        fields = line.split(",")

        if fields[0] == "Inn":
            headers = fields
            curHalfInning = ""
            halfInning = []
            innings = {}

        elif fields[0].startswith("t") or fields[0].startswith("b"):
            # Construct the entry dict
            entry = {key.strip(): value.strip() for (key, value) in zip(headers, fields)}

            # Load into a new half inning if necessary
            if curHalfInning != entry["Inn"]:
                if curHalfInning != "":
                    innings[curHalfInning] = halfInning
                curHalfInning = entry["Inn"]
                halfInning = []

            halfInning += [entry]

    playerTotals = {}
    for halfInning in innings:
        batters = []
        singles = []
        runs = []
        

        for entry in innings[halfInning]:
            # Add the current batter to the player totals and
            # batters list
            newBatter = "(" + entry["@Bat"] + ") " + entry["Batter"]
            batters += [newBatter]
            if not newBatter in playerTotals:
                playerTotals[newBatter] = {"1B": 0, "2B": 0, "3B": 0, "R": 0}

            # Check to see if anyone scores on this play.
            # Note that in the case of the home run, the batter is not considered
            # a run because he was never on base.
            matches = scoreRe.findall(entry["Play Description"])
            bmatch = [batter for batter in batters for match in matches if match in batter]
            if len(bmatch) != len(matches):
                raise Exception("Failed to match batter(s) scored: " + str(matches))
            runs += bmatch

        for batter in batters:
            playerTotals[batter]["1B"] = batters.count(batter)
            playerTotals[batter]["R"] = runs.count(batter)

    return playerTotals


if __name__ == "__main__":
    with open("boxes_WAS_WAS201506250_play_by_play.csv") as fobj:
        playerTotals = extractTotals(fobj)
        for player in playerTotals:
            print "%-24s : %s" % (player, playerTotals[player])