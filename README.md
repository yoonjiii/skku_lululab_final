﻿# skku_lulu_final
 
 app.py는 앱에서 전송한 정보를 받아 성분사전매칭을 진행한 뒤 그 결과를 다시 앱으로 전송하는 프로그램입니다.
 app.py와 필요한 파일을 서버에 올린 뒤에 이 파일을 실행시키면 됩니다. 
 ```
 python app.py
 ```
 
 ## Requirements
 app.py를 실행하기 위해 필요한 파일들입니다.
 + ### cosmetic_DB.xlsx
   이미 성분정보가 수집된 화장품들에 대한 정보가 딤긴 파일이자, 화장품 이름과 각 화장품에 포함된 성분들이 정리된 파일입니다.  
   '화장품 이름으로 검색하기' 옵션을 선택했을 때, 화장품 이름이 포함된 이미지에서 OCR로 텍스트를 인식한 뒤, 추출한 텍스트를 이 파일 안에서 찾습니다. 
   만약 찾는다면 이미 성분정보를 수집한 화장품이므로 바로 해당 화장품의 성분정보를 제공합니다. 
   만약 찾지 못한다면 아직 성분정보를 수집하지 못했거나 OCR 인식에서 오류가 있었던 것이므로 'no data'를 반환하고, 화장품 이름이 아닌 화장품 성분표로 다시 검색하도록 합니다.
   
 
