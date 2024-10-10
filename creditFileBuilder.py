# Program to build batch credit/void upload files using 1stPay RestGW query.
# File will be created in current directory.
# Kevin Dawson

from urllib.parse import quote_from_bytes
import requests
import gateway


def getMerchantCredentials():

    key = str(input("Please enter your merchant key: "))
    proc = str(input("Please enter your processor Id: "))

    return key, proc


def filterDuplicates():

    duplicates = str(
        input("Would you like to remove duplicate names?: (Y/N) "))

    if duplicates.lower() != "y" and duplicates.lower() != "n":
        print("Please enter Y or N for your response to indicate Yes or No\n")
        duplicates = input("Would you like to remove duplicate names?: (Y/N) ")

    filterDuplicates = False

    if duplicates.lower() == "y":
        filterDuplicates = True

    return filterDuplicates


def getDateAndTime():

    sDate = input("Please enter the start date: (MM/DD/YYYY) ")
    sTime = input("Please enter the start time: (## ## AM/PM) ")
    eDate = input("Please enter the end date: (MM/DD/YYYY) ")
    eTime = input("Please enter the end time: (## ## AM/PM) ")

    s1 = sDate.split("/")
    s2 = sTime.split(" ")
    e1 = eDate.split("/")
    e2 = eTime.split(" ")

    return s1, s2, e1, e2


mc = getMerchantCredentials()
fd = filterDuplicates()
dt = getDateAndTime()

data = {
    "merchantKey": mc[0],
    "processorId": mc[1],
    "queryStartMonth": dt[0][0],
    "queryStartDay": dt[0][1],
    "queryStartYear": dt[0][2],
    "queryStartHour": dt[1][0],
    "queryStartMinute": dt[1][1],
    "queryStartAMPM": dt[1][2],
    "queryEndMonth": dt[2][0],
    "queryEndDay": dt[2][1],
    "queryEndYear": dt[2][2],
    "queryEndHour": dt[3][0],
    "queryEndMinute": dt[3][1],
    "queryEndAMPM": dt[3][2],
    "queryTimeZoneOffset": '-300'  # Convert from UTC to EST
}

gw = gateway.RestGateway(data)

transactionData = gw.query()
# print(transactionData)

f = open("creditFile.txt", "w")

f.write("[version2]\n")

cardNames = []


def writeCredit():

    f.write("cc_credit, ")
    f.write(str(data['processorId']))
    f.write(", ")
    f.write(str(i['referenceNumber']))
    f.write(', ')
    f.write(str(i['orderInfo']['amount']))
    f.write('\n')
    print("ref number written to file")


def writeVoid():

    f.write("cc_void, ")
    f.write(str(data['processorId']))
    f.write(", ")
    f.write(str(i['referenceNumber']))
    f.write('\n')
    print("ref number written to file")


for i in transactionData['data']['orders']:

    # If filter duplicates
    if fd:

        if (i['ccInfo']['nameOnCard']) not in cardNames and (i['orderInfo']['isSuccessful'] == 'True') and (i['orderInfo']['transactionType'] == 'sale'):

            cardNames.append(i['ccInfo']['nameOnCard'])
            # print(i['ccInfo']['nameOnCard'])

            if (i['orderInfo']['settled'] == True):

                writeCredit()

            else:

                writeVoid()

    else:

        if (i['orderInfo']['isSuccessful'] == 'True') and (i['orderInfo']['transactionType'] == 'sale'):

            if (i['orderInfo']['settled'] == True):

                writeCredit()

            else:

                writeVoid()

f.close()
