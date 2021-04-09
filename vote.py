from csv import reader
from collections import defaultdict
from six import next
from argparse import ArgumentParser


class BookRanker:

    def __init__(self, inputFile, colsToDelete, question):
        self.tallies = {}
        self.inputFile = inputFile
        self.colsToDelete = colsToDelete
        self.question = question

    class TallyObj:

        def __init__(self, title, tallies):
            self.title = title
            self.tallies = tallies

        def __gt__(self, other):

            def compareTallies(lastPlace, scoreSelf, scoreOther):

                while lastPlace > 1:
                    # Kind of treating rank as "displeasure points". Not quite
                    # sure if that works perfectly, but it works well enough
                    scoreSelf += self.tallies[lastPlace]
                    scoreOther += other.tallies[lastPlace]

                    if scoreSelf != scoreOther:
                        return scoreSelf > scoreOther

                    lastPlace -= 1

                # If their scores are equal, just go alphabetically
                return self.title > other.title

            if not isinstance(other, type(self)):
                return False

            lastPlaceSelf = max(self.tallies, key=int)
            lastPlaceOther = max(other.tallies, key=int)

            # The idea is to pick books that everyone can tolerate reasonably
            # well, so the "loser" is the book that's most hated by anyone
            if lastPlaceSelf != lastPlaceOther:
                return lastPlaceSelf > lastPlaceOther

            startingScoreSelf = self.tallies[lastPlaceSelf]
            startingScoreOther = other.tallies[lastPlaceOther]

            return compareTallies(lastPlaceSelf - 1, startingScoreSelf,
                                  startingScoreOther)

    def vote(self):

        with open(self.inputFile) as rankFile:

            resultReader = reader(rankFile)

            header = next(resultReader)

            # Date column is unnecessary
            for col in self.colsToDelete:
                header.pop(col)

            for title in header:
                self.tallies[title] = defaultdict(int)

            for row in resultReader:

                # Discarding date column again
                for col in self.colsToDelete:
                    row.pop(col)

                # Keeps track of how many nth place votes each title has, of the
                # form {title: {n: tally}} where n is some rank (like 1 for first
                # place)
                for idx, rank in enumerate(row):
                    self.tallies[header[idx]][int(rank)] += 1

            tallyObjs = []

            for title, tallyDict in self.tallies.items():
                # Get rid of Microsoft Form question title which shows up in every
                # entry for some reason...
                tallyObjs.append(self.TallyObj(title.replace(self.question, ""),
                                               tallyDict))

            # Abuse the overloaded operator to figure out the ordering
            tallyObjs = sorted(tallyObjs)
            tallyObjs.reverse()

            n = 1

            while tallyObjs:
                print("BOOK {N}:".format(N=n))
                print("\t{TITLE}\n".format(TITLE=tallyObjs.pop().title)
                      .replace("[", "").replace("]", ""))
                n += 1


if __name__ == "__main__":
    parser = ArgumentParser(description="This is a script to order book club "
                                        "books given a CSV of ranked choice "
                                        "votes per participant")

    parser.add_argument('-i', '--input',
                        help='Input CSV (will be rankings.csv by default)',
                        default="rankings.csv")

    parser.add_argument('-c', '--columns',
                        help='Column indices to ignore in input file (will be 0 by default)',
                        type=int, nargs='+', default=[0])
    
    parser.add_argument('-q', '--question',
                        help='Question string from the form to delete from titles'
                             ' (will be \'Please rank your choices \' by default)',
                        default="Please rank your choices ")

    args = parser.parse_args()

    BookRanker(inputFile=args.input, colsToDelete=args.columns,
               question=args.question).vote()
