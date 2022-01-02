from datetime import datetime
import time
import requests
from bs4 import BeautifulSoup
from decimal import Decimal

import os

delayStatic = 300

def clearConsole():
    command = 'clear'
    if os.name in ('nt', 'dos'):  # If Machine is running on Windows, use cls
        command = 'cls'
    os.system(command)


def get_real_value(value):
    val = ""
    value = str(value)
    for character in value:
        if character.isdigit() or character == '.':
            val += character
    return val

def read_data(pathc):
    lines = []
    if os.path.isfile(pathc):
        f = open(pathc, 'r+')
        lines = f.readlines()[3:]
        f.close()
    return lines

def get_time():
    da = datetime.now()
    da = str(da).split(".")[0].split(" ")
    date = da[0].split("-")
    time = da[1].split(":")
    time = time[0]+":"+time[1]
    date = date[2]+"/"+date[1]+"/"+date[0]
    return str(date + " " + time)

class Crypto:
    def __init__(self, name, url, invested_at):
        self.name = name
        self.url = url
        self.invested_at = invested_at
        raw_data = requests.get(self.url)
        bs = BeautifulSoup(raw_data.text, 'html.parser')
        self.latest_value = Decimal(get_real_value(bs.select(".priceValue")[0].text))
        self.profits = 0

    def do_check(self):
        raw_data = requests.get(self.url)
        bs = BeautifulSoup(raw_data.text, 'html.parser')
        self.latest_value = Decimal(get_real_value(bs.select(".priceValue")[0].text))
        real_v_shiba_s = Decimal(get_real_value(self.invested_at))
        self.profits = Decimal((self.latest_value-real_v_shiba_s))

        data = read_data("C:\\Programs\\cryptoChecker\\crypto_data_" + self.name + ".txt")

        f = open("C:\\Programs\\cryptoChecker\\crypto_data_" + self.name + ".txt", "w")
        stxS = "STATUS: LOSS\t" + str(self.profits)
        if self.profits > 0:
            stxS = "STATUS: PROFIT!\t" + str(self.profits)

        f.write(stxS + '\n\nVALUED AT\tDATE\n')
        for line in data:
            f.write(line)
        f.write("\n")

        timeT = get_time()

        line = "$"+str(self.latest_value) + "\t\t" + str(timeT)

        if len(str(self.latest_value)) > 6:
            line = "$"+str(self.latest_value) + "\t" + str(timeT)

        f.write(line)
        f.close()
        return [self.name, self.latest_value, self.profits]

def getEqualLengthStrings(toRet, toCount):
    times = len(toCount) - len(toRet)
    strx = ""
    for i in range(times+1):
        strx+=" "
    return strx+toRet

def getRowLength(length):
    x = ''
    for i in range(0,length):
        x += '='
    return x

def run(cryptos):
    while True:
        checks = list()
        for crypto in cryptos:
            checks.append(crypto.do_check())
        clearConsole()
        for i in range(0, len(cryptos)):
            check = checks[i]
            os.system('echo \033[1m' + check[0] + '\033[0m')
            print("Current: " + str(check[1]))
            txt = ""
            if check[2] > 0:
                check[2] = "+" + str(check[2])
                txt = "echo \033[32mPROFIT: " + getEqualLengthStrings(str(check[2]), str(check[1])) + '\033[0m'
            else:
                txt = "echo \033[31mLOSS  : " + getEqualLengthStrings(str(check[2]), str(check[1])) + '\033[0m'
            os.system(txt)
            os.system('echo.')

        timeD = get_time()
        print('\033[1m' + getRowLength(len(timeD)) + '\n' + timeD + '\n' + getRowLength(len(timeD)) + '\n\033[0m')
        time.sleep(delayStatic)

if __name__ == '__main__':

    cryptos = list()
    if os.path.isfile("C:\\Programs\\cryptoChecker\\cryptos.csv") == False:
        cryptos_csv = open("C:\\Programs\\cryptoChecker\\cryptos.csv",'w')
        cryptos_csv.write('300\nBTC,https://coinmarketcap.com/currencies/bitcoin/,57021.55,\n')
        cryptos_csv.close()

    cryptos_csv = open("C:\\Programs\\cryptoChecker\\cryptos.csv")
    lines_crypto = cryptos_csv.readlines()
    if len(lines_crypto) != 0 and len(lines_crypto[0].split(",")) == 1:
        delayStatic = int(lines_crypto[0])
        lines_crypto = lines_crypto[1:]
    elif len(lines_crypto) != 0:
        delayStatic = int(input('Please enter the interval in seconds in which you want a check to be done,\n150 means that there would be 2 minutes and 30 seconds between checks\nInput value here, only digits:'))
        cryptos_csv = open("C:\\Programs\\cryptoChecker\\cryptos.csv", "w")
        cryptos_csv.write(str(delayStatic) + '\n')
        for crypto in cryptos:
            cryptos_csv.write(crypto.name + "," + crypto.url + "," + get_real_value(crypto.invested_at) + ",\n")
        cryptos_csv.close()

    for line in lines_crypto:
        datacells = line.split(",")
        cryptos.append(Crypto(datacells[0], datacells[1], datacells[2]))
    cryptos_csv.close()

    print("Press enter if you want to run the program.")
    print("Or, press 2 and enter if you want to input a new crypto to check for.")
    choice = input()
    if choice == "2":
        addMore = True
        while addMore:
            print("INPUT NAME")
            name = input()
            print("INPUT URL (must be from coinmarketcap.com)")
            url = input()
            if url.startswith("https://coinmarketcap.com/currencies/") == False :
                print("ERROR, NOT VALID URL!\nSTARTING AGAIN.")
            print("INPUT PRICE YOU INVESTED AT")
            invested_at = input()
            cryptos.append(Crypto(name, url, invested_at))
            cryptos_csv = open("C:\\Programs\\cryptoChecker\\cryptos.csv", "w")
            cryptos_csv.write(str(delayStatic) + '\n')
            for crypto in cryptos:
                cryptos_csv.write(crypto.name + "," + crypto.url + "," + get_real_value(crypto.invested_at) + ",\n")
            cryptos_csv.close()
            print("Inputted crypto and saved it under the name " + name)
            print("Press 1 and enter if you want to add more cryptos\nElse, press 2 and enter")
            choice2 = input()
            if choice2.strip() == "2":
                addMore = False

    for i in range(0, len(cryptos)):
        for j in range(0, len(cryptos)-i-1):
            if cryptos[j].name > cryptos[j+1].name:
                temp = cryptos[j]
                cryptos[j] = cryptos[j+1]
                cryptos[j+1] = temp
    run(cryptos)