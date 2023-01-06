from wordsegment import load, segment
load()
import pandas as pd
from difflib import get_close_matches
import re
import json
import io # 파일을 읽고 쓰기 위한 모듈
import os
import base64
from collections import OrderedDict

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "lululab-ocr-b3ae0ebfee0d.json"

from google.cloud import vision


file = open('output_156.txt', 'r')
json_string = file.read()
json_string = json_string.replace("\n","")
img_string = json_string.replace(" ","")
#print(img_string)
file.close()

filename = 'decoded_image_156.jpg'
imgdata = base64.b64decode(img_string)
with open(filename, 'wb') as f:
  f.write(imgdata)

client = vision.ImageAnnotatorClient()
file_name = os.path.abspath('decoded_image_156.jpg')

with io.open(file_name, 'rb') as image_file:
    content = image_file.read()

image = vision.Image(content=content)

response = client.text_detection(image=image)
result = response.text_annotations

texts = ""
texts = result[0].description

texts = texts.replace("\n","")

json_object = {}
filename = 'ingre.xlsx'
df = pd.read_excel(filename, engine='openpyxl')
ls = list(df['lower'])
ls = list(map(str, ls))


json_object = {}
l = []
l.append(re.split('[,.]',texts))
print(l)

list_ = sum(l, [])

for i in range(len(list_)):
    list_[i] = list_[i].lower()

json_result = ""
i = 0
while i < len(list_):  # 10초
    word = list_[i]
    #print(word)
    n = 1
    cutoff = 0.75
    close_matches = get_close_matches(word, ls, n, cutoff)
    tem = word
    if i < len(list_) - 1:
        tem += " " + list_[i + 1]
        next_ = get_close_matches(tem, ls, n, 0.9)
        if next_ != []:
            i += 2
            # print(tem,next_,i)
            name_list = df[df['lower'] == next_[0]][['eng_name']].values.tolist()
            name_str = name_list[0][0]
            json_object['class'] = name_str
            name_list = df[df['lower'] == next_[0]][['purpose']].values.tolist()
            name_str = name_list[0][0]
            json_object['purpose'] = name_str
            json_string = json.dumps(json_object, indent=4)
            if json_result == "":
                json_result = json_string
            else:
                json_result = json_result+","+json_string

            #print(df[df['lower'] == next_[0]][['eng_name']])

        elif close_matches == []:
            for l in segment(word):
                cf = 0.8
                c_m = get_close_matches(l, ls, n, cf)

                # print(l,c_m,i)
                if c_m != []:
                    name_list = df[df['lower'] == c_m[0]][['eng_name']].values.tolist()
                    name_str = name_list[0][0]
                    json_object['class'] = name_str
                    name_list = df[df['lower'] == c_m[0]][['purpose']].values.tolist()
                    name_str = name_list[0][0]
                    json_object['purpose'] = name_str
                    json_string = json.dumps(json_object, indent=4)
                    if json_result == "":
                        json_result = json_string
                    else:
                        json_result = json_result + "," + json_string
                    #print(df[df['lower'] == c_m[0]][['kor_name', 'eng_name', 'purpose']])
            i += 1
        else:
            # print(word,close_matches,i)
            if close_matches != []:
                name_list = df[df['lower'] == close_matches[0]][['eng_name']].values.tolist()
                name_str = name_list[0][0]
                json_object['class'] = name_str

                name_list = df[df['lower'] ==close_matches[0]][['purpose']].values.tolist()
                name_str = name_list[0][0]
                json_object['purpose'] = name_str

                json_string = json.dumps(json_object, indent=4)
                if json_result == "":
                    json_result = json_string
                else:
                    json_result = json_result + "," + json_string
                #print(df[df['lower'] == close_matches[0]][['kor_name', 'eng_name', 'purpose']])
            i += 1
    else:
        # print(word,close_matches)
        if close_matches != []:
            name_list = df[df['lower'] == close_matches[0]][['eng_name']].values.tolist()
            name_str = name_list[0][0]
            json_object['class'] = name_str
            name_list = df[df['lower'] == close_matches[0]][['purpose']].values.tolist()
            name_str = name_list[0][0]
            json_object['purpose'] = name_str
            json_string = json.dumps(json_object, indent=4)
            if json_result == "":
                json_result = json_string
            else:
                json_result = json_result + "," + json_string
            #print(df[df['lower'] == close_matches[0]][['kor_name', 'eng_name', 'purpose']])
        i += 1
json_result = "["+json_result+"]"
json_final = json.loads(json_result)
print(json_result)

with open('server_result.json', 'w', encoding="utf-8") as f:
    json.dump(json_final, f, indent="\t",ensure_ascii=False)
