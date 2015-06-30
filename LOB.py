import re
import logging
import play_parse

log = logging.getLogger(__name__)

bbref_url = "http://www.baseball-reference.com/boxes/2015.shtml"

moveRe = re.compile("([^;]+) to ([1-3]B)")
scoreRe = re.compile("([^;]+) Scores")

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

    parser = play_parse.PlayParser()
    for halfInning in innings:
        for entry in innings[halfInning]:
            for i in range(3):
                if entry["RoB"][i] == "-" and \
                    parser.baseState[i] != None:
                    raise Exception("Unexpected baserunner at %dB" % (i + 1))
                elif entry["RoB"][i] != "-" and \
                    parser.baseState[i] == None:
                    raise Exception("Missing a baserunner at %dB" % (i + 1))

            # Get an ID for the current batter
            batter = "(" + entry["@Bat"] + ") " + entry["Batter"]

            # Get the play description
            desc = entry["Play Description"]

            # Parse the play
            parser.parsePlay(desc, batter)

        parser.endInning()

    return parser.playerTotals


if __name__ == "__main__":
    with open("boxes_PHI_PHI201506282_play_by_play.csv") as fobj:
    # with open("boxes_WAS_WAS201506250_play_by_play.csv") as fobj:
        playerTotals = extractTotals(fobj)
        for player in playerTotals:
            print "%-24s : %s" % (player, playerTotals[player])