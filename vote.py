from csv import reader
from collections import defaultdict
from six import next

DATE_COL = 0
ROUND_STR_FORMATTER = "\n----ELIMINATION ROUND {N}----\n"
# INPUT_FILE = "rankings.csv"
INPUT_FILE = "/Users/zacarias/Downloads/rankingsUSingers.csv"

TALLIES = {}


class Response:

    def __init__(self, fileRow, fileHeader):
        self.title2rank = {}
        self.rank2title = {}

        for idx, rank in enumerate(fileRow):
            TALLIES[fileHeader[idx]][int(rank)] += 1

            self.title2rank[fileHeader[idx]] = int(rank)
            self.rank2title[int(rank)] = fileHeader[idx]


class TallyObj:

    def __init__(self, val, tallies):
        self.val = val
        self.tallies = tallies

    def __gt__(self, other):

        def compareTallies(lastPlace, scoreSelf, scoreOther):
            while True:
                scoreSelf += self.tallies[lastPlace]
                scoreOther += other.tallies[lastPlace]

                if scoreSelf != scoreOther:
                    return scoreSelf > scoreOther

                lastPlace -= 1

        if not isinstance(other, TallyObj):
            return False

        lastPlaceSelf = max(self.tallies, key=int)
        lastPlaceOther = max(other.tallies, key=int)

        if lastPlaceSelf != lastPlaceOther:
            return lastPlaceSelf > lastPlaceOther

        scoreSelf = self.tallies[lastPlaceSelf]
        scoreOther = other.tallies[lastPlaceOther]

        lastPlaceSelf -= 1

        return compareTallies(lastPlaceSelf, scoreSelf, scoreOther)


def vote():

    with open(INPUT_FILE) as rankFile:

        resultReader = reader(rankFile)

        header = next(resultReader)

        # Date column is unnecessary
        header.pop(DATE_COL)

        for title in header:
            TALLIES[title] = defaultdict(int)

        responses = []

        for row in resultReader:

            # Discarding date column again
            row.pop(DATE_COL)

            responses.append(Response(row, header))

        tallyObjs = []

        for title, tallies in TALLIES.items():
            tallyObjs.append(TallyObj(title, tallies))

        tallyObjs = sorted(tallyObjs)
        tallyObjs.reverse()

        n = 1

        while tallyObjs:
            print("BOOK {N}:".format(N=n))
            print("\t{TITLE}\n".format(TITLE=tallyObjs.pop().val)
                  .replace("(", "").replace(")", ""))
            n += 1


if __name__ == "__main__":
    vote()
