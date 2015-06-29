import re
import logging

log = logging.getLogger(__name__)

moveRe = re.compile("(.+) to ([1-3])B")
scoreRe = re.compile("(.+) Scores")
forceoutRe = re.compile("Forceout at ([1-3])B")

# Where does the batter up for each type of plate event?
PLATE_EVENTS = {
    "Single": 		0,
    "Walk": 		0,
    "Hit By Pitch": 0,
    "Double": 		1,
    "Triple": 		2,
    "Reached on ": 	0,
}

class PlayParser(object):

	def __init__(self):
		self.playerTotals = {}
		self.reset()

	def reset(self):
		self.baseState = [ None ] * 3

	def getPlayerFromMention(self, menu, mention):
		playerMatches = [player for player in menu if mention in player]
		if len(playerMatches) == 0:
			# The mentioned player could not be matched in the meny
			return None
		elif len(playerMatches) > 1:
			# We have matched with multiple players in the menu
			# This is a serious error since it potentially corrupts data so raise an Exception
			raise Exception("Matched multiple players for scored player: " + mention + \
		    	", matched players: " + str(playerMatches))
		else:
		    # Normal happening - we matched one player to the player who scored
		    return playerMatches[0]

	def parsePlay(self, play, batter):
		# Find all the events in this play
		events = [event.strip() for event in play.split(";")]

		# Initialize the next baseState
		nextState = [ None ] * 3

		# Initialize the scored runners list
		scoredRunners = []

		# Intialize the outer runners list
		outedRunners = []

		# Flag for whether this play contains a strikeout (special case)
		isStrikeout = False

		# Add the batter to the tallies if necessary
		if not batter in self.playerTotals:
			# Initialize the base totals
			self.playerTotals[batter] = { key: 0 for key in \
				["1B", "2B", "3B", "R", "Kob"] }

		# Process each event in the play
		for event in events:
			# Check if this a plate event
			plateMatches = [ plateEvent for plateEvent in PLATE_EVENTS \
				if event.startswith(plateEvent) ]
			if len(plateMatches) > 0:
				# Update the next state with the batter
				nextState[PLATE_EVENTS[plateMatches[0]]] = batter
				continue

			if event.startswith("Strikeout"):
				# Indicate this play contains a strikeout (special case)
				isStrikeout = True

			# Check if this is a runner moved event
			movedMatches = moveRe.findall(event)
			for (runner, base) in movedMatches:
				# Find the full ID of the runner
				player = self.getPlayerFromMention( \
					[manOnBase for manOnBase in self.baseState if manOnBase != None], \
					runner)
				if player == None:
					# The player was not on base before - could it be the batter?
					player = self.getPlayerFromMention( \
						[ batter ],
						runner)
					if player == None:
						# Still couldn't match, throw the error
						raise Exception("Could not match runner to player ID: " + runner)
					else:
						# Need to remove the batter from his current position
						# in the nextState
						nextState = [ None if manOnBase == player else manOnBase \
							for manOnBase in nextState ]

				# Update for the next state
				nextState[int(base) - 1] = player


			# Check if this is a runner scored
			scoreMatches = scoreRe.findall(event)
			for runner in scoreMatches:
				# Find the full ID of the runner
				player = self.getPlayerFromMention( \
					[manOnBase for manOnBase in self.baseState if manOnBase != None], \
					runner)

				# Add the runner to the scored runners list
				scoredRunners += [ player ]

			# Check if there were any special forceouts
			forceoutMatches = forceoutRe.findall(event)
			for base in forceoutMatches:
				# Forceout not at 1B means batter takes over at 1B
				nextState[0] = batter
				# Forceout means we this player needs to go away
				outedRunners += [ self.baseState[int(base) - 2] ]
				if base == "3":
					# Forceout at 3B - runner coming into 2B
					nextState[1] = self.baseState[0]
				# TODO: FIGURE OUT FORCEOUT AT HOME

			#TODO: FIGURE OUT GIDP/TRIPLE PLAY

		# Add in batters whose state did not change
		for i in range(3):
			player = self.baseState[i]
			if player != None and \
				player not in nextState and \
				player not in scoredRunners and \
				player not in outedRunners:

				# Add the player back to his original base
				nextState[i] = player

		# BEFORE WE SET THE STATE TO THE NEXT STATE,
		# UPDATE THE PLAYER TOTALS WITH ANYTHING THAT HAS HAPPENED

		if isStrikeout:
			for player in self.baseState:
				if player != None:
					self.playerTotals[player]["Kob"] += 1

		# TODO: FIGURE OUT 1B/2B/3B ETC.

		# Update the base state for next time
		self.baseState = nextState

