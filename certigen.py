import cv2
import pytesseract
import imutils
from flask import Flask, render_template, request, jsonify, app
from werkzeug import secure_filename
from imutils.object_detection import non_max_suppression
import numpy as np
import argparse
import pandas as pd
from datetime import datetime
from PIL import Image
import sqlite3

from readtext import get_string



# conn = (sqlite3.connect('db.sqlite'))
# curr= conn.cursor()
# conn.close()


name = ['confer', 'presented', 'conferred', 'certify', 'certified','recognizes','given to']
course = ['course', 'degree', 'field', 'completion','performance in','completing']
day = ['date', 'day', 'date of issue','issued','issued on','issue']
month = ['month']
year = ['year', 'in the year']

dict = {}
dict['name'] = name
dict['course'] = course
dict['day'] = day
dict['month'] = month
dict['year'] = year


def align(sx,ex,l):
    return int(((ex-sx)-(17*l))/2)


def find_field(str):
    # str = "This is to certify that"
    str = str.lower()

    # print(dict)

    for field in dict:
        # print(field)
        list = dict[field]
        if any(word in str for word in list):
            return field


font = cv2.FONT_HERSHEY_SIMPLEX
# flask routing begins
app = Flask(__name__)

def Reverse(lst):
    return [ele for ele in reversed(lst)]

#image to text
# def get_string(img_path):
#     # Read image with opencv
#     img = cv2.imread(img_path)
#
#     # Convert to gray
#     img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#
#     # Apply dilation and erosion to remove some noise
#     kernel = np.ones((1, 1), np.uint8)
#     img = cv2.dilate(img, kernel, iterations=1)
#     img = cv2.erode(img, kernel, iterations=1)
#
#     # Write image after removed noise
#     cv2.imwrite( "removed_noise.png", img)
#
#     #  Apply threshold to get image with only black and white
#     #img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 2)
#
#     # Write the image after apply opencv to do some ...
#     cv2.imwrite( "thres.png", img)
#
#     # Recognize text with tesseract for python
#     result = pytesseract.image_to_string(Image.open( "thres.png"))
#
#     # Remove template file
#     #os.remove(temp)
#
#     return result
#




@app.route('/sampleupload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        f = request.files['file']
        i = request.files['image']
        # m= request.files['mail']
        # t = request.form['temp']
        f.save(secure_filename(f.filename))
        i.save(secure_filename(i.filename))
        # m.save(secure_filename(m.filename))

    image = cv2.imread(i.filename)
    width = int(image.shape[1] )
    height = int(image.shape[0])
    # print(width,height)

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5,5), 0)
    thresh = cv2.adaptiveThreshold(blur,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV,11,30)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (9,9))
    dilate = cv2.dilate(thresh, kernel, iterations=4)

    cnts = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]

    ROI_number = 0
    points = []
    text=[]
    info = {}
    for c in cnts:
        area = cv2.contourArea(c)
        if area > 2000 and area<70000 :
            x,y,w,h = cv2.boundingRect(c)
            cv2.rectangle(image, (x, y), (x + w, y + h), (12,255,32), 3)
            point = [x,y,x+w,y+h]
            points.append(point)
            ROI = image[y:y+h, x:x+w]
            picname = 'ROI_'+str(ROI_number)+'.jpg'
            cv2.imwrite(picname, ROI)
            # print('ROI_'+str(ROI_number)+'.jpg')
            ROI_number += 1

            # print(get_string(picname))
            text_block=get_string(picname)
            if text_block != '':
                text.append(get_string(picname))
            # print(text)
            # find the field
            stmt = get_string(picname)
            field = find_field(stmt)
            if field=='day' :
                info[field] = [x, y  , x + w, y ]
                continue

            info[field] = [x, y+ 2*h, x+w, y+ 2*h]

    data = pd.read_excel(r'C:\Users\admin\.PyCharmCE2019.1\config\scratches\entries.xlsx')
    # print(data)

    info['course'][0]=int(image.shape[1]/2)-100
    info['name'][0]=int(image.shape[1]/2)-100
    c = 0

    g=len(i.filename)
    t=i.filename[:g-4]

    # print((info['month']))
    # if info['month'] and info[year]

    # print(info['day'])
    for row in data.itertuples():
        img = cv2.imread(t + '.jpg')
        s = t + "_certi_"

        for i in range(1, data.shape[1] + 1):
            if data.columns[i-1] == 'month' or data.columns[i-1]=="year":
                continue

            if 'month' not in info.keys() and 'year' not in info.keys() and data.columns[i - 1]=='day' :
                date=str(row[i])+'-'+str(row[i+1])+'-'+str(row[i+2])
                # sx=info[data.columns[i - 1]][0]
                # ex=info[data.columns[i - 1]][2]
                # l=len(date)
                cv2.putText(img, date, (info[data.columns[i - 1]][0], info[data.columns[i - 1]][1]), font, 1,(0, 0, 0), 2, cv2.LINE_AA)
                continue

            # sx = info[data.columns[i - 1]][0]
            # ex = info[data.columns[i - 1]][2]
            # l = len(str(row[i]))
            cv2.putText(img, str(row[i]),(info[data.columns[i - 1]][0],info[data.columns[i - 1]][1]), font,1, (0, 0, 0), 2, cv2.LINE_AA)
            # print(info[data.columns[i - 1]][0],info[data.columns[i - 1]][1])

        now = datetime.now()
        dt_string = now.strftime("%d%m%Y%H%M%S") + str(c)
        cv2.putText(img, str(dt_string),(int(width/2-50),height-20)  , font, 1, (0, 0, 0),2, cv2.LINE_AA)
        # conn = (sqlite3.connect('db.sqlite'))
        # curr = conn.cursor()
        # curr.execute('INSERT into verify (student,code) VALUES (?,?)',(row[1],dt_string))
        # conn.close()

        s = s + str(c) + ".jpg"
        cv2.imwrite(s, img)
        c = c + 1


    return "File Uploaded Successfully"




@app.route('/uploader', methods=['GET', 'POST'])
def upload_excel():
    if request.method == 'POST':
        f = request.files['file']
        t = request.form['temp']
        f.save(secure_filename(f.filename))

        print(t)

        df = pd.read_excel(r'C:\Users\admin\.PyCharmCE2019.1\config\scratches\sample1.xlsx')
        # print(df)
        tempname = t

        record = {}

        for row in df.itertuples():
            # print(row)
            # print(row[0])
            if (row[1] == tempname):
                for i in range(1, df.shape[1]):
                    # print(row[i])
                    if (not isinstance(row[i], float)):
                        s = row[i]
                        # print(str)
                        # print(df.columns[i - 1])
                        field = df.columns[i - 1]
                        if (field == 'template'):
                            continue
                        # str = row[i+1]
                        list = s.split(" ")
                        # sx = list[0]
                        # sy = list[1]
                        # ex = list[2]
                        # ey = list[3]

                        record[field] = list
                        print(record)
                        # print(list)

        data = pd.read_excel(r'C:\Users\admin\.PyCharmCE2019.1\config\scratches\entries.xlsx')
        # print(data)
        # mail_flag = False
        #
        # if 'email' in data.columns:
        #     mail_flag = True
        #     email = data['email']
        #     # print(email)
        #     data = data.drop(['email'], axis=1)

        c = 0

        for row in data.itertuples():
            img = cv2.imread(t+'.jpg')
            width = int(img.shape[1])
            height = int(img.shape[0])
            s = t+"_certi_"

            for i in range(1, data.shape[1] + 1):
                # writefunc(row[i], record[data.columns[i-1]])
                cv2.putText(img, str(row[i]),
                            (int(record[data.columns[i - 1]][0]), int(record[data.columns[i - 1]][1])), font, float(record[data.columns[i - 1]][4]),(0, 0, 0), 1, cv2.LINE_AA)
                # print(float(record[data.columns[i - 1]][4]))
                # print(str(row[i]),  float(record[data.columns[i - 1]][3]))

            now = datetime.now()
            dt_string = now.strftime("%d%m%Y%H%M%S") + str(c)
            cv2.putText(img, str(dt_string), (int(width / 2 - 50), height - 20), font, .5, (0, 0, 0), 2, cv2.LINE_AA)

            # conn = (sqlite3.connect('db.sqlite'))
            # curr = conn.cursor()
            # curr.execute('INSERT into verify (student,code) VALUES (?,?)', (row[1], dt_string))
            # conn.close()

            s = s + str(c) + ".jpg"
            cv2.imwrite(s, img)
            c = c + 1

        return 'file uploaded successfully'


# @app.route('/verify', methods=['GET', 'POST'])
# def verify():
#     if request.method == 'POST':
#         c = request.form['code']
#         conn = (sqlite3.connect('db.sqlite'))
#         curr = conn.cursor()
#         curr.execute('SELECT name from verify WHERE code = (?)',c)
#         s=str(curr.fetchall());
#         conn.close()
#         return s



if __name__ == "__main__":
    app.debug = True
    app.run(debug=True)




