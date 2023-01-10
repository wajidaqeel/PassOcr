from fastapi import FastAPI , File , UploadFile , Form
from datetime import datetime
import mrzscanner
import json
from mrz.checker.td1 import TD1CodeChecker
from mrz.checker.td2 import TD2CodeChecker
from mrz.checker.td3 import TD3CodeChecker
from mrz.checker.mrva import MRVACodeChecker
from mrz.checker.mrvb import MRVBCodeChecker
import cv2
import uuid
import numpy as np


app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

def check(lines):
    try:
        td1_check = TD1CodeChecker(lines)
        if bool(td1_check):
            return "TD1", td1_check.fields()
    except Exception as err:
        pass
    
    try:
        td2_check = TD2CodeChecker(lines)
        if bool(td2_check):
            return "TD2", td2_check.fields()
    except Exception as err:
        pass
    
    try:
        td3_check = TD3CodeChecker(lines)

        if bool(td3_check):
            return "TD3", td3_check.fields()
    except Exception as err:
        pass
    
    try:
        mrva_check = MRVACodeChecker(lines)
        if bool(mrva_check):
            return "MRVA", mrva_check.fields()
    except Exception as err:
        pass
    
    try:
        mrvb_check = MRVBCodeChecker(lines)
        if bool(mrvb_check):
            return "MRVB", mrvb_check.fields()
    except Exception as err:
        pass
    
    return 'No valid MRZ information found'





import cv2 

def get_info(scanner,img):



  image_np=np.frombuffer(img,dtype=np.uint8)
  img_np=cv2.imdecode(image_np,cv2.IMREAD_COLOR)



 
  s=""


  results =  scanner.decodeMat(((img_np)))

  lst1=[]
  lst=[]
  for result in results:
    s += result.text + '\n'
    lst1.append(result.text+ '\n')

  str1=""
  str1=str1.join(lst1[-2:])

  if check(str1[:-1]) == "No valid MRZ information found":
    try:
      ed=(TD3CodeChecker(str1[:-1],check_expiry=False,compute_warnings=True))
      lst.append(ed.fields())
      return lst
    except:
      return []
  else:
    lst.append(check(str1[:-1]))
    return lst



def extract_result(lst):
   x=0
   final_lst=[]
   if type(lst[x])==tuple:
    temp_lst=[]
    surname=lst[x][1][0]
    name=lst[x][1][1]
    country=lst[x][1][2]
    nationality=lst[x][1][3]
    try:

      birth_date=datetime.strptime(lst[x][1][4], '%y%m%d').strftime('%d/%m/%Y')
      expiry_date=datetime.strptime(lst[x][1][5], '%y%m%d').strftime('%d/%m/%Y')
    except:
      birth_date=lst[x][1][4]#datetime.strptime(lst[x][1][4], '%y%m%d').strftime('%d/%m/%Y')
      expiry_date=lst[x][1][5]#datetime.strptime(lst[x][1][5], '%y%m%d').strftime('%d/%m/%Y')
      
    document_type=lst[x][1][7]
    document_number=lst[x][1][8]
    temp_lst.append([surname,name,country,nationality,birth_date,expiry_date,document_type,document_number])
    final_lst.append(temp_lst)

   else:
    temp_lst=[]
    surname=lst[x][0]
    name=lst[x][1]
    country=lst[x][2]
    nationality=lst[x][3]
    try:
      birth_date=datetime.strptime(lst[x][4], '%y%m%d').strftime('%d/%m/%Y')
      expiry_date=datetime.strptime(lst[x][5], '%y%m%d').strftime('%d/%m/%Y')
    except:
       birth_date=lst[x][4]#datetime.strptime(lst[x][4], '%y%m%d').strftime('%d/%m/%Y')
       expiry_date=lst[x][5]#datetime.strptime(lst[x][5], '%y%m%d').strftime('%d/%m/%Y')
    
    document_type=lst[x][7]
    document_number=lst[x][8]
    temp_lst.append([surname,name,country,nationality,birth_date,expiry_date,document_type,document_number])
    final_lst.append(temp_lst)
 



   return temp_lst


def return_df(final_lst):

  columns = ['surname','name','country','nationality','birth_date','expiry_date','document_type','document_number']

  res = {columns[i]: final_lst[0][i] for i in range(len(columns))}
  json_en=json.dumps(res)
 
  return json.loads(json_en)



class encodedImage(BaseModel):
    base64img:str


@app.post('/file')
async def _file_upload(my_file:
    UploadFile = File(...)):

    my_file.filename = f"{uuid.uuid4()}.jpg"
    contents = await my_file.read()  # <-- Important!

    mrzscanner.initLicense("DLS2eyJoYW5kc2hha2VDb2RlIjoiMjAwMDAxLTE2NDk4Mjk3OTI2MzUiLCJvcmdhbml6YXRpb25JRCI6IjIwMDAwMSIsInNlc3Npb25QYXNzd29yZCI6IndTcGR6Vm05WDJrcEQ5YUoifQ==")
    scanner = mrzscanner.createInstance()
    scanner.loadModel(mrzscanner.get_model_path())
    lst=get_info(scanner, contents)
 
    final_lst=extract_result(lst)
    json_file=return_df(final_lst)
    return json_file
        