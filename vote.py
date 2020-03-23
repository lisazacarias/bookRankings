from csv import reader
from collections import defaultdict
from six import next
from typing import Dict, List

DATE_COL = 0
ROUND_STR_FORMATTER = "\n----ROUND {N}----\n"


class Response:

    def __init__(self, fileRow, fileHeader):
        self.title2rank = {}
        self.rank2title = {}

        for idx, rank in enumerate(fileRow):

            self.title2rank[fileHeader[idx]] = int(rank)
            self.rank2title[int(rank)] = fileHeader[idx]


class TallyObj:

    def __init__(self, val, tally, isMajority):
        self.val = val
        self.tally = tally
        self.isMajority = isMajority


def getRankTally(rank: int, responses: List[Response]):
    counter = defaultdict(int)

    for response in responses:
        counter[response.rank2title[rank]] += 1

    res = max(counter)
    tally = counter[res]

    return TallyObj(val=res, tally=tally,
                    isMajority=(tally / len(responses) > 0.5))


def adjustResults(lastPlace, responses):
    loser = getRankTally(lastPlace, responses).val
    print("LOSER IS: {LOSER}".format(LOSER=loser))

    for response in responses:

        loserRank = response.title2rank[loser]
        response.title2rank.pop(loser)
        response.rank2title.pop(loserRank)

        if loserRank != lastPlace:
            for i in range(loserRank, lastPlace):
                titleToMoveUp = response.rank2title[i + 1]

                response.title2rank[titleToMoveUp] = i
                response.rank2title[i] = titleToMoveUp

            response.rank2title.pop(lastPlace)


def vote():

    with open("rankings.csv") as rankFile:

        resultReader = reader(rankFile)

        header = next(resultReader)

        # Date column is unnecessary
        header.pop(DATE_COL)

        responses = []

        for row in resultReader:

            # Discarding date column again
            row.pop(DATE_COL)

            responses.append(Response(row, header))

        votingRound = 1

        winner = getRankTally(1, responses)
        if winner.isMajority:
            return winner.val

        lastPlace = 27

        while lastPlace > 1:
            print(ROUND_STR_FORMATTER.format(N=votingRound))
            adjustResults(lastPlace, responses)
            lastPlace -= 1
            votingRound += 1
            winner = getRankTally(1, responses)

        return winner.val


if __name__ == "__main__":
    print("\nWINNER IS: {WINNER}\n".format(WINNER=vote()))