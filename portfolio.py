# added a header
# author a.j. madison
# class COMP 4581
# author email aj.madison@du.com
import sys
import argparse
import datetime
from collections import defaultdict
from collections import deque
import csv
import time
import logging


def loadFile(inputFilename):
    investments = list()
    with open(inputFilename, 'r') as f:
        sniff = csv.Sniffer()
        if sniff.has_header(f.read(2048)):
            f.seek(0)
            dictReader = csv.DictReader(f)
            ##todo can should this full data collection take place if only columns
            ## is being run?
            fieldNamesList = dictReader.fieldnames
            fieldIndex = 0
            fieldNamesDict = defaultdict()
            for i in fieldNamesList:
                fieldNamesDict[i] = fieldIndex
                fieldIndex = fieldIndex+1
            logging.debug(f"loadFile fieldNamesDict {fieldNamesDict}")
        else:
            f.seek(0)
            #todo add default dict that assumes the previous

        reader = csv.reader(f)
        if fieldNamesDict.get("return") == None:
            logging.info(f"loadfile no return column in csv")
            for line in reader:
                if line[fieldNamesDict["RegionName"]] == "United States":
                    logging.info(f"loadfile skipping RegionName {line[2]}")
                    continue
                else:
                    investments.append([line[fieldNamesDict["RegionName"]],
                                       int(line[fieldNamesDict["Zhvi"]]),
                                       float(line[fieldNamesDict["Zhvi"]]) * \
                                         float(line[fieldNamesDict["10Year"]])])
        else:
            for line in reader:
                if line[fieldNamesDict["RegionName"]] == "United States":
                    logging.info(f"loadfile skipping RegionName {line[2]}")
                    continue
                else:
                    investments.append([line[fieldNamesDict["RegionName"]],
                                       int(line[fieldNamesDict["Zhvi"]]),
                                       float(line[fieldNamesDict["return"]])])
    return investments


def initialize_logging(args):
    if args.log_level is not None:
        logger = logging.getLogger()
        logger.setLevel(args.log_level)
        ts = datetime.datetime.now(tz=None)
        formatter = logging.Formatter(fmt='%(asctime)s %(name)s %(levelname)-8s - %(message)s',
                                      datefmt='%Y-%m-%d %H:%M:%S')
        if args.log_level == logging.DEBUG:
            fh = logging.FileHandler(
                f"log_{sys.argv[0].replace('.py','')}.txt", 'w')
            fh.setFormatter(formatter)
            fh.setLevel(args.log_level)
            logger.addHandler(fh)
        else:
            sh = logging.StreamHandler()
            sh.setFormatter(formatter)
            sh.setLevel(args.log_level)
            logger.addHandler(sh)


def logMatrix(m, name):
    logging.debug(f"matrix {name}")
    for row in m:
        logging.debug(f"{row}")


def printMatrix(m, name):
    print(f"matrix {name}")
    for row in m:
        print(f"{row}")

# mildly rewritten knapsack code produces correct results for the small dataset.
def optimizeInvestments(M, investments):
    n = len(investments)
    logging.info(f"optimizeInvestments length {n}")
    logging.debug(f"optimizeInvestments investments {investments}")
    optimalTable = [[None for x in range(M + 1)] for x in range(n + 1)]
    tracebackTable = [[None for x in range(M + 1)] for x in range(n + 1)]
    zhvi = [0 for x in range(n+2)]
    xReturns = [0 for x in range(n+2)]
    # Build table K[][] in bottom to up manner
    for i in range(n + 1):
        t1 = time.time()
        # create convenience lists that make the code clearer
        if i < n:
            zhvi[i] = investments[i][1]
            xReturns[i] = investments[i][2]
        for w in range(M + 1):
            if (i == 0 or w == 0):
                optimalTable[i][w] = 0
                tracebackTable[i][w] = False
            elif zhvi[i-1] <= w:
                # may be able to buy this house at this investment level
                optimalTable[i][w] = max(xReturns[i-1] + optimalTable[i-1][w-zhvi[i-1]],
                                optimalTable[i-1][w])
                # logging.debug(f"optimizeInvestments i {i} w {w} max {xReturns[i-1] + optimalTable[i-1][w-zhvi[i-1]]} {optimalTable[i-1][w]}")
                if (xReturns[i-1] + optimalTable[i-1][w-zhvi[i-1]]) < (optimalTable[i-1][w]):
                    tracebackTable[i][w] = False
                else:
                    tracebackTable[i][w] = True
            else:
                # cannot buy this house at all at this investment level
                optimalTable[i][w] = optimalTable[i-1][w]
                tracebackTable[i][w] = False
        t2 = time.time()
        logging.info(f"optimizeInvestments i {i} time {round(t2-t1, 3)}")
        logMatrix(optimalTable, f"i {i} optimalTable")
        logMatrix(tracebackTable, f"i {i} tracebackTable")

    tr_i = n
    tr_w = M
    investmentNames = list()
    #need to figure out what to do if n and M of the traceback table is false
    while tr_i > 0 and tr_w > 0:
        logging.debug(f"optimizeInvestments tr_i {tr_i} tr_w {tr_w}")
        if tracebackTable[tr_i][tr_w] == True:
            logging.debug(f"optimizeInvestments tr_i {tr_i} tr_w {tr_w} True")
            logging.debug(f"optimizeInvestments investments[{tr_i-1}][0] {investments[tr_i-1][0]}")
            # save answer
            investmentNames.append(investments[tr_i-1][0])
            # subtract amount invested
            tr_w = tr_w - investments[tr_i-1][1]
            # jump to previous line
            tr_i = tr_i - 1
        elif tr_i > 0:
            # current entry is false, jump to previous line
            tr_i = tr_i - 1


    logMatrix(optimalTable, "zhvi x xReturns")
    return optimalTable[n][M], investmentNames


def main():
    t1 = time.time()
    parser = argparse.ArgumentParser(
        description='analyze data from specified input file.')
    parser.add_argument('-n', '--investments', metavar='<investmentFilename>',
                        dest='investmentFilename',
                        help='investment data to be processed')

    parser.add_argument('-m', '--maxinvestment', metavar='<maxInvestment>',
                        type=int, default=15,
                        dest='maxInvestment',
                        help='maximum amount of money to invest')

    parser.add_argument('-d', '--debug',
                        dest='log_level', action='store_const',
                        const=logging.DEBUG,
                        help='turn on debugging output, default is off')

    parser.add_argument('-i', '--info',
                        dest='log_level', action='store_const',
                        const=logging.INFO,
                        help='turn on info level output, default is off')

    args = parser.parse_args()
    initialize_logging(args)
    logging.info(f"maxInvestment {args.maxInvestment}")

    investments = loadFile(args.investmentFilename)

    print(optimizeInvestments(args.maxInvestment, investments))
    t2 = time.time()
    print(f"time {round(t2-t1, 3)} s")


if __name__ == '__main__':
    main()
