#!/usr/bin/env python3

import re
import requests
import configparser


# Read local file `config.ini`.
config = configparser.ConfigParser()
config.read('config.ini')


url = config['SETTINGS']['URL']
user, password = config['SETTINGS']['USER'], config['SETTINGS']['PASSWORD'] 
resp = requests.get(url, auth=(user, password))
open("vc.vcf", "wb").write(resp.content)


vcf = open("vc.vcf", "r")
lines = vcf.readlines()
vcard_id = 0

card = []

for line in lines:
  if re.search('BEGIN', line):
    vcard_id += 1
    card.append([])
  if re.search('^FN:', line):

    line = line.replace("FN:", "").replace(";", " ").strip()
    if len(line.split()) == 3:
      line = line.split()
      line = str(f"{line[2]} {line[0]} {line[1]}")

      card[vcard_id - 1].append(line)
    else:
      card[vcard_id - 1].append(line)
  if re.search('^TEL;', line):
    line = line.strip()[line.find(":") +1:]
    line = re.sub(r"\(|\)|-", "", line)
    line = re.sub(r" ", "", line)
    line = re.sub(r"\+7", "8", line)
    if len(line) == 6:
      card[vcard_id - 1].append(line)
    else:
      card[vcard_id - 1].append(line)
vcf.close

card.sort()

print("<YeastarIPPhoneDirectory>")

for en in card:
  if len(en) > 1:
    print("   <DirectoryEntry>")
    print(f'      <Name>{en.pop(0)}</Name>')
    for i in en:
      print(f'        <Telephone>{i}</Telephone>')
    print("   </DirectoryEntry>")

print("</YeastarIPPhoneDirectory>")

