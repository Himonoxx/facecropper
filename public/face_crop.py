import cv2
import os
import boto3
import urllib

def mosaic(before, ratio=0.1):
    small = cv2.resize(before, None, fx=ratio, fy=ratio, interpolation=cv2.INTER_NEAREST)
    return cv2.resize(small, before.shape[:2][::-1], interpolation=cv2.INTER_NEAREST)


def mosaic_area(before, x, y, width, height, ratio=0.1):
    dst = before.copy()
    dst[y:y + height, x:x + width] = mosaic(dst[y:y + height, x:x + width], ratio)
    return dst

bucket_name='pythonphp-us'
region='us-east-2'
base_path='http://s3-' + region + '.amazonaws.com/' + bucket_name
keys=[]

s3=boto3.resource('s3')
bucket=s3.Bucket(bucket_name)


now_dir=os.getcwd()

import_path=base_path + '/faceupload'
output_path=base_path + '/facedownload/'
cascade_file=[now_dir + '/haarcascade_frontalface_default.xml',now_dir + 'haarcascade_profileface']
cascade = cv2.CascadeClassifier(cascade_file[0])

try:
    #keyを拾う
    objs = bucket.meta.client.list_objects_v2(Bucket=bucket.name, Prefix='faceupload/', Delimiter='/')
    
    for i in range(1,len(objs['Contents']),1):
        tmp_file_name=objs['Contents'][i]['Key']
        keys.append(tmp_file_name.replace('faceupload/',''))

    file_name=keys[len(keys)-1]
    print(file_name)
    key='faceupload/' + file_name
    
    image_file=urllib.parse.quote(file_name)
    image_path= import_path + file_name
    image_output ='facedownload/' + 'output_' + image_file
    image_output_local='tmp_output/output_' + image_file
    
    bucket.download_file(Key=key,Filename=now_dir + '/tmp/' + file_name)
    image_data='tmp/' + file_name
    print(image_data)

    before=cv2.imread(image_data)
    after=cv2.imread(image_data)
    print(before,after)
    imgray=cv2.cvtColor(before, cv2.COLOR_BGR2GRAY)
    face=cascade.detectMultiScale(imgray,1.3,5)

    if 0<len(face):
        for x,y,w,h in face:
            after=mosaic_area(before,x,y,w,h)
    else:
        print('顔を発見できませんでした。')
    
    
    #横顔モザイク処理
    cascade = cv2.CascadeClassifier(cascade_file[1])
    cv2.imwrite(image_output_local,after)
    bucket.upload_file(image_output_local,'facedownload/' + image_file)
    
    #keyを拾う
    objs = bucket.meta.client.list_objects_v2(Bucket=bucket.name, Prefix='facedownload/', Delimiter='/')
    
    for i in range(1,len(objs['Contents']),1):
        tmp_file_name=objs['Contents'][i]['Key']
        keys.append(tmp_file_name.replace('facedownload/',''))

    file_name=keys[len(keys)-1]
    print(file_name)
    key='facedownload/' + file_name
    
    image_file=urllib.parse.quote(file_name)
    image_path= import_path + file_name
    image_output ='facedownload/' + 'totaloutput_' + image_file
    image_output_local='tmp_output/totaloutput_' + image_file
    
    bucket.download_file(Key=key,Filename=now_dir + '/tmp/' + file_name)
    image_data='tmp/' + file_name
    print(image_data)

    before=cv2.imread(image_data)
    after=cv2.imread(image_data)
    print(before,after)
    imgray=cv2.cvtColor(before, cv2.COLOR_BGR2GRAY)
    face=cascade.detectMultiScale(imgray,1.3,5)

    if 0<len(face):
        for x,y,w,h in face:
            after=mosaic_area(before,x,y,w,h)
    else:
        print('顔を発見できませんでした。')
    
    cv2.imwrite(image_output_local,after)
    bucket.upload_file(image_output_local,'facedownload/' + image_file)


except Exception as e:
        print(e)
        raise e