#!/usr/bin/env python3

import re
import requests
import configparser
import hashlib
from pathlib import Path
import copy

# Read local file `config.ini`.
config = configparser.ConfigParser()
config.read('config.ini')
url = config['SETTINGS']['URL']
user, password = config['SETTINGS']['USER'], config['SETTINGS']['PASSWORD'] 
remote_xml = config['SETTINGS']['REMOTE_XML']
local_xml = config['SETTINGS']['LOCAL_XML']

#check md5sum file
def check_md5():
  file_name = "vc.vcf"
  md5_file = "vc.md5"
  md5_hash = hashlib.md5()
  a_file = open("vc.vcf", "rb")
  content = a_file.read()
  md5_hash.update(content)
  vcf_hash = md5_hash.hexdigest()
  
  for i in(file_name, md5_file):
    fle = Path(i)
    fle.touch(exist_ok=True)

  if Path(file_name).stat().st_size == 0:
    return

  f = open(md5_file, 'r')
  md5sum = f.read()
  if md5sum == vcf_hash:
    f.close()
    exit()

  f = open(md5_file, 'w')
  f.write(vcf_hash)
  f.close()


resp = requests.get(url, auth=(user, password))
open("vc.vcf", "wb").write(resp.content)

check_md5()

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
    elif len(line.split()) == 2:
      line = line.split()
      line = str(f"{line[1]} {line[0]}")
      card[vcard_id - 1].append(line)
    else:
      card[vcard_id - 1].append(line)
  if re.search('^TEL;', line):
    line = line.strip()[line.find(":") +1:]
    line = re.sub(r"\(|\)|-", "", line)
    line = re.sub(r" ", "", line)
    line = re.sub(r"\+7", "8", line)
    card[vcard_id - 1].append(line)
vcf.close

card.sort()

card_yealink = copy.deepcopy(card)


f = open(remote_xml, 'w')

f.write("<YeastarIPPhoneDirectory>\n")

for en in card:
  if len(en) > 1:
    f.write("   <DirectoryEntry>\n")
    f.write(f'      <Name>{en.pop(0)}</Name>\n')
    for i in en:
      f.write(f'        <Telephone>{i}</Telephone>\n')
    f.write("   </DirectoryEntry>\n")

f.write("</YeastarIPPhoneDirectory>\n")

f.close()

"""
Template YEALINK local
<root_contact>
<contact display_name="Name Name" office_number="" mobile_number="" other_number="" line="0" ring="" group_id_name="All Contacts" />
</root_contact>
"""
def nums(num1="", num2="", num3="", *del_nums):
    f.write(f'office_number=\"{num1}\" ')
    f.write(f'mobile_number=\"{num2}\" ')
    f.write(f'other_number=\"{num3}\" ')

f = open(local_xml, 'w')

f.write("<root_contact>\n")

for en in card_yealink:
  if len(en) > 1:
    f.write("   <contact")
    f.write(f' display_name=\"{en.pop(0)}\" ')

    nums(*en)
    f.write("line=\"0\" ring=\"\" group_id_name=\"All Contacts\" />\n")

f.write("</root_contact>\n")

f.close()
