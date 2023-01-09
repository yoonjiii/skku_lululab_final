from wordsegment import load, segment
load()
import pandas as pd
from difflib import get_close_matches
import re
import io
import os
import base64
from google.cloud import vision
from symspellpy_ko import KoSymSpell, split_syllables, join_jamos, Verbosity
import pytest
import difflib
from functools import reduce
import numpy as np
from flask import Flask, request, render_template
from flask import Flask
from collections import OrderedDict
from werkzeug.serving import WSGIRequestHandler
WSGIRequestHandler.protocol_version = "HTTP/1.1"

path = "lululab-ocr-b3ae0ebfee0d.json"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = path

app=Flask(__name__)
@app.route('/', methods=['GET','POST'], strict_slashes=False)
def home():
    if request.method == 'POST':
        print(request.is_json)
        params = request.get_json()
        imgdata = base64.b64decode(params['image'])
        lan = params['language']
        option = params['option']

        filename = 'decoded_image.jpg'
        with open(filename, 'wb') as f:
            f.write(imgdata)

        client = vision.ImageAnnotatorClient()
        file_name = os.path.abspath('decoded_image.jpg')

        with io.open(file_name, 'rb') as image_file:
            content = image_file.read()

        image = vision.Image(content=content)

        response = client.text_detection(image=image)
        result = response.text_annotations

        texts = ""
        texts = result[0].description


        # Option is "name"
        if option == '1':
            texts = texts.replace("\n", " ")
            print(texts)

            output_class = []
            output_purpose = []

            filename = 'cosmetic_DB.xlsx'
            df = pd.read_excel(filename, engine='openpyxl')
            ls = list(df['name'])
            ls = list(map(str, ls))
            if(df['name'] == texts).any():
                ingredients = df[df['name'] == texts]['ingredient list'].values.tolist()[0]
                output_class = [ingredients.strip() for ingredients in re.split('[,]', ingredients)]
                length = len(output_class)
                for x in output_class:
                    filename = 'ingre_kor.xlsx'
                    di = pd.read_excel(filename, engine='openpyxl')
                    ls = list(di['kor_name'])
                    ls = list(map(str, ls))
                    if(di['kor_name'] == x).any():
                        list_tmp = di[di['kor_name'] == x]['purpose'].values.tolist()[0]
                        output_purpose.append(list_tmp)
                i = 0;
                output = "["
                while True:
                    if i != 0:
                        output = output + ','
                    output = output + '{"class":"' + output_class[i] + '","purpose":"' + output_purpose[i] + '"}'
                    if i == length - 1:
                        output = output + "]"
                        break
                    i = i+1
                print(output)
                return output
            else :
                message = "no data"
                return message
        

        #Language = English
        if lan == '1':
            print("language is english")

            filename = 'ingre.xlsx'
            df = pd.read_excel(filename, engine='openpyxl')
            ls = list(df['lower'])
            ls = list(map(str, ls))

            output_class = []
            output_purpose = []

            texts = texts.replace("\n", "")
            print(texts)
            # 괄호 안에 있는 문자열 지우기
            texts = re.sub(r'\([^()]*\)', '', texts)
            # 대괄호 안에 있는 문자열 지우기
            texts = re.sub(r'\[[^())]*\]', '', texts)

            l = []
            # 만약 구분자가 ,가 아니라 성분에 ,가 없다면 -로 잘라준다.
            if ',' not in texts:
                l = [text.strip() for text in re.split('[.:;*-]', texts)]
            # ,.:;를 기준으로 잘라준다.
            else:
                l = [text.strip() for text in re.split('[,.:;*]', texts)]

            list_ = l
            # 알파벳을 모두 소문자로 변환하기
            for i in range(len(list_)):
                list_[i] = list_[i].lower()

            i = 0
            while i < len(list_):  # 10초
                word = list_[i]

                # word에 ingredients 또는 all ingredient가 포함되어 있다면 지운다
                if "ingredients" in word:
                    word = word.replace('ingredients', '')

                if "all ingredients" in word:
                    word = word.replace('all ingredients', '')

                if "Ingrédients" in word:
                    word = word.replace('Ingrédients', '')

                if word == 'parfum':
                    output_class.append('fragrance')

                n = 1
                cutoff = 0.75
                close_matches = get_close_matches(word, ls, n, cutoff)
                tem = word
                if i < len(list_) - 1:
                    tem += " " + list_[i + 1]
                    next_ = get_close_matches(tem, ls, n, 0.9)
                    if next_ != []:
                        i += 2
                        list_tmp = df[df['lower'] == next_[0]][['eng_name']].values.tolist()
                        str_tmp = list_tmp[0][0]  # name of the ingredient
                        output_class.append(str_tmp)
                        list_tmp = df[df['lower'] == next_[0]][['purpose']].values.tolist()
                        str_tmp = list_tmp[0][0]  # purpose of the ingredient
                        output_purpose.append(str_tmp)

                    elif close_matches == []:
                        for l in segment(word):
                            cf = 0.8
                            c_m = get_close_matches(l, ls, n, cf)

                            # print(l,c_m,i)
                            if c_m != []:
                                list_tmp = df[df['lower'] == c_m[0]][['eng_name']].values.tolist()
                                str_tmp = list_tmp[0][0]  # name of the ingredient
                                output_class.append(str_tmp)
                                list_tmp = df[df['lower'] == c_m[0]][['purpose']].values.tolist()
                                str_tmp = list_tmp[0][0]  # purpose of the ingredient
                                output_purpose.append(str_tmp)
                        i += 1
                    else:
                        # print(word,close_matches,i)
                        if close_matches != []:
                            list_tmp = df[df['lower'] == close_matches[0]][['eng_name']].values.tolist()
                            str_tmp = list_tmp[0][0]  # name of the ingredient
                            output_class.append(str_tmp)
                            list_tmp = df[df['lower'] == close_matches[0]][['purpose']].values.tolist()
                            str_tmp = list_tmp[0][0]  # purpose of the ingredient
                            output_purpose.append(str_tmp)
                        i += 1
                else:
                    # print(word,close_matches)
                    if close_matches != []:
                        list_tmp = df[df['lower'] == close_matches[0]][['eng_name']].values.tolist()
                        str_tmp = list_tmp[0][0]  # name of the ingredient
                        output_class.append(str_tmp)
                        list_tmp = df[df['lower'] == close_matches[0]][['purpose']].values.tolist()
                        str_tmp = list_tmp[0][0]  # purpose of the ingredient
                        output_purpose.append(str_tmp)
                    i += 1
            output_final_class = []
            [output_final_class.append(x) for x in output_class if x not in output_final_class]
            output_final_purpose = []
            [output_final_purpose.append(x) for x in output_purpose if x not in output_final_purpose]

            print(output_final_class)
            print(output_final_purpose)

            i = 0;
            length = len(output_class)
            print("length is ")
            print(length)
            output = "["
            #[{"class":"AAA","purpose":"aaaaa"},{"class":"BBB","purpose":"bbbbb"}]
            while True :
                if i != 0:
                    output = output + ','
                output = output + '{"class":"' + output_class[i] + '","purpose":"' + output_purpose[i] + '"}'
                if i == length-1:
                    output = output + ']'
                    break
                i = i+1

        elif lan == '2':
            print("language is korean")

            chut = 'ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ#'
            ga = 'ㅏㅐㅑㅒㅓㅔㅕㅖㅗㅘㅙㅚㅛㅜㅝㅞㅟㅠㅡㅢㅣ#'
            ggut = ' ㄱㄲㄳㄴㄵㄶㄷㄹㄺㄻㄼㄽㄾㄿㅀㅁㅂㅄㅅㅆㅇㅈㅊㅋㅌㅍㅎ#'

            BASE = 0xAC00

            query = '췟'

            code = ord(query) - BASE

            jongsung = code % 28
            jungsung = ((code - jongsung) // 28) % 21
            chosung = ((code - jongsung) // 28) // 21

            def segment(ch):
                '''유니코드 글자를 입력받아 초,중,종성에 대한 인덱스를 반환한다'''
                code = ord(ch) - BASE
                jongsung = code % 28

                code = code - jongsung
                jungsung = (code // 28) % 21

                code = code // 28
                chosung = code // 21

                if chosung < 0:
                    chosung = -1
                if 19 < jongsung:
                    jongsung = -1

                return chut[chosung], ga[jungsung], ggut[jongsung]

            def diff(word1, word2):
                '''두 유니코드 단어의 거리를 계산하여 차이를 반환한다'''
                L1 = ''.join(reduce(lambda x1, x2: x1 + x2, map(segment, word1)))
                L2 = ''.join(reduce(lambda x1, x2: x1 + x2, map(segment, word2)))
                differ = difflib.SequenceMatcher(None, L1, L2)
                return differ.ratio()

            filename = 'ingre_kor.xlsx'
            di = pd.read_excel(filename, engine='openpyxl')

            ls = list(di['kor_name'])
            ls = list(map(str, ls))

            dictionary_path = "frequency_dictionary_kor_ingredients.txt"
            sym_spell = KoSymSpell()
            sym_spell.load_dictionary(dictionary_path, 0, 1)

            texts = texts.replace("\n","")
            print(texts)
            # 괄호 안에 있는 문자열 지우기
            texts = re.sub(r'\([^()]*\)', '', texts)
            # 대괄호 안에 있는 문자열 지우기
            texts = re.sub(r'\[[^())]*\]', '', texts)

            # 성분 앞에 붙여진 특수기호 제거
            special_char = '|*#^+$%&()'
            texts = ''.join(c for c in texts if c not in special_char)

            # 콤마 뒤 공백 제거, .,:;* 기준으로 자르기
            word_ = [text.strip() for text in re.split('[,.:;*]', texts)]

            output_ = []

            for s in word_:
                ingre = s

                max_ = 0
                str_ = ""
                typo_ = ""

                edit1_ = []
                edit2_ = []
                space_ = []
                space_matching_ = []
                result_ = []

                if "전성분" in s:
                    s = s.replace('전성분', '')

                if "성분명" in s:
                    s = s.replace('성분명', '')

                if "성분" in s:
                    s = s.replace('성분', '')

                # 일치하는 성분명이 있으면 아래의 과정 거치지 않고 output_에 추가
                if (di['kor_name'] == s).any():
                    output_.append(s)
                    ###output_purpose에 purpose append

                else:
                    # 공백이 포함된 문자열 중 콤마가 검출되지 않은 경우
                    if " " in s:
                        if len(s.split()) == 0:
                            # print("blank")
                            continue

                        item = s
                        space_.append(item)
                        space_ += [n.strip() for n in s.split(" ")]

                        """ 추가글자로 인한 오류를 줄이기 위해 마지막 단어일 경우, 
                        4개 이상의 단어가 나오면 3개까지만 리스트 저장하기 """
                        # if s == word_[len(word_)-1]:
                        #   if len(space_) > 4:
                        #     space_ = space_[0:4]
                        # print(space_)

                        correctness_ = []

                        for i in space_:
                            if len(i.split()) == 0:
                                continue
                            if i.isdigit():
                                continue

                            max_ = 0
                            str_ = ""
                            typo_ = ""
                            edit1_ = []
                            edit2_ = []

                            if len(space_matching_) == 1 and correctness_[0] >= 0.85:
                                result_.append(space_matching_[0])
                                output_.append(space_matching_[0])
                                break

                            if (di['kor_name'] == i).any():
                                max_ = 1
                                correctness_.append(1)
                                space_matching_.append(i)
                                # print(space_matching_)
                                continue

                            for suggestion in sym_spell.lookup(i, Verbosity.ALL):
                                if (suggestion.distance == 1):
                                    tmp_ = suggestion.term
                                    edit1_.append(tmp_)

                                else:
                                    tmp_ = suggestion.term
                                    edit2_.append(tmp_)

                            if edit1_ != []:
                                for e in edit1_:
                                    # print(e)
                                    if diff(i, e) > max_:
                                        max_ = diff(i, e)
                                        str_ = e
                                        typo_ = i

                                correctness_.append(max_)
                                print(str_, typo_, max_)

                                space_matching_.append(str_)

                            elif edit2_ != []:
                                for e in edit2_:
                                    if diff(i, e) > max_:
                                        max_ = diff(i, e)
                                        str_ = e
                                        typo_ = i

                                correctness_.append(max_)
                                print(str_, typo_, max_)

                                space_matching_.append(str_)

                            elif edit1_ == [] and edit2_ == []:
                                for e in ls:
                                    if diff(i, e) > max_:
                                        max_ = diff(i, e)
                                        str_ = e
                                        typo_ = i

                                correctness_.append(max_)
                                print(str_, typo_, max_)

                                space_matching_.append(str_)

                        for i in range(1, len(space_matching_)):
                            if correctness_[0] < correctness_[i]:
                                if correctness_[i] <= 0.5:
                                    result_.append(' ')
                                    output_.append(' ')
                                else:
                                    result_.append(space_matching_[i])
                                    output_.append(space_matching_[i])

                        if len(result_) == 0:
                            # result_.append(space_matching_[0])
                            output_.append(space_matching_[0])
                        print(output_)
                        continue

                    else:

                        if len(s.split()) == 0:
                            # print("blank")
                            continue

                        if s == "1":
                            continue

                        if s == "2-헥산다이올" or s == "2-헥산디올":
                            # print("1,2-헥산다이올")
                            output_.append("1,2-헥산다이올")
                            continue

                        if "피이자" in s:
                            s = s.replace('피이자', '피이자-')

                        # 숫자ppm 같은 경우를 제외시켜주기 위해서 숫자(digit)과 알파벳만 나오는 경우 제외시켜준다.
                        if s.isdigit():
                            continue

                        for suggestion in sym_spell.lookup(s, Verbosity.ALL):
                            if (suggestion.distance == 1):
                                tmp_ = suggestion.term
                                edit1_.append(tmp_)

                            else:
                                tmp_ = suggestion.term
                                edit2_.append(tmp_)

                        if edit1_ != []:
                            for e in edit1_:
                                # print(e)
                                if diff(s, e) > max_:
                                    max_ = diff(s, e)
                                    str_ = e
                                    typo_ = s

                        elif edit2_ != []:
                            for e in edit2_:
                                if diff(s, e) > max_:
                                    max_ = diff(s, e)
                                    str_ = e
                                    typo_ = s

                        elif edit1_ == [] and edit2_ == []:
                            for e in ls:
                                if diff(s, e) > max_:
                                    max_ = diff(s, e)
                                    str_ = e
                                    typo_ = s

                        print(typo_, " ", str_, " ", max_)
                        if max_ > 0.5:
                            output_.append(str_)
                        else:
                            output_.append(' ')
                        print("------------------------")
                # 중복된 성분이 있다면 한번만 출력되도록 한다.
            output_final_ = []
            output_purpose_ = []
            for x in output_:
                if x == ' ':
                    output_final_.append(' ')
                    continue

                if x not in output_final_:
                    output_final_.append(x)
                    purpose = di[di['kor_name'] == x]['purpose'].values.tolist()[0]
                    output_purpose_.append(purpose)
            i = 0;
            length = len(output_final_)
            output = "["
            # [{"class":"AAA","purpose":"aaaaa"},{"class":"BBB","purpose":"bbbbb"}]
            while True:
                if i != 0:
                    output = output + ','
                output = output + '{"class":"' + output_final_[i] + '","purpose":"' + output_purpose_[i] + '"}'
                if i == length - 1:
                    output = output + "]"
                    break
                i = i+1

        print(output)
        return output
    else:
        return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
