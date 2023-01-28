from django.shortcuts import render

# Create your views here.
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
# from .serializers import QueueSerializer
# from .models import Queue
from rest_framework import status

###########################
import requests
import json
import os
import time
from threading import Thread

url = "https://api-gw.onebound.cn/taobao/item_search_shop/?key=t_856 2094008186&&shop_id=57301367&page=1&sort=&&lang=zh-CN&secret=20230114"
headers = {
    "Accept-Encoding": "gzip",
    "Connection": "close"
}
#################################
@api_view(['GET', 'POST'])
def download_images(request):
    pass
# Create your views here.
@api_view(['GET', 'POST'])
def all_items(request):
    url = "https://api-gw.onebound.cn/taobao/item_search_shop/?key=t_856 2094008186&&shop_id=57301367&page=1&sort=&&lang=zh-CN&secret=20230114"
    headers = {
        "Accept-Encoding": "gzip",
        "Connection": "close"
    }

    if request.method =='GET':
        print("ok")
        ################################
        loop_num = 0
        while True:
            print("start")
            r = requests.get(url, headers=headers)
            json_obj = r.json()
            print(json_obj)
            if "items" in json_obj.keys():
                print("true")
                break
            time.sleep(1)
            loop_num += 1
            if loop_num == 5:
                break
        #analyse first response to get data including page count...
        # print(json_obj['items']['page_count'])
        global page_count, shop_id, district
        

        page = int(json_obj['items']['page'])
        page_count = int(json_obj['items']['page_count'])
        
        #analyse url to get neccessary info
        url_split = url.split("/")

        #district --> example: taobao, 1688, Dangdang...
        district = url_split[3]+"_json"

        #shop id inside district
        shop_id = url_split[5].split("&&")[1].split("&")[0]

        filename = f'{district}/{shop_id}/page_{page}/page.json'
        isExist = os.path.exists(filename)

        if isExist is False:
            os.makedirs(os.path.dirname(filename), exist_ok=True)

            with open(f'{district}/{shop_id}/page_{page}/page.json', 'w') as f:
                json.dump(json_obj, f, indent=4)



        for item in json_obj['items']['item']:
            # downloadJson(item, page)
            # downloadImage(filename,f"{prev}/{filename}")
            downloadThread = Thread(target=downloadJson, args=(item, page, ))
            downloadThread.isDaemon = True
            downloadThread.start()




        ##############################
        # djqueue = Queue.objects.all()
        # serializer = QueueSerializer(djqueue, many=True)
        return Response ({"name": "superstar"})

    elif request.method == 'POST':
        # serializer = QueueSerializer(data=request.data)
        # serializer.is_valid(raise_exception=True)
        # serializer.save()
        return Response ({"name": "superstar--post"})
        # return Response(serializer.data, status=status.HTTP_201_CREATED)

def downloadJson(item, page):
    global page_count, shop_id, district
    print(f"page count: {page_count}")
    print("======================================================")
    num_iid = item["num_iid"]
    pic_url = item["pic_url"]
    #image download    ====================
    if 'http' not in pic_url:
        pic_url = f"http:{pic_url}"
    response = requests.get(pic_url)
    # if response.status_code == 200:
    #     print("img")

    #     filename = f"{district}/{shop_id}/page_{page}/item_image/{num_iid}.jpg"
    #     os.makedirs(os.path.dirname(filename), exist_ok=True)

    #     with open(f"{district}/{shop_id}/page_{page}/item_image/{num_iid}.jpg", 'wb') as f:
    #         f.write(response.content)
    #     print("ok")
    #end image downlaod  ====================

    #page item detail
    loop_num = 0
    while True:
        url = f"https://api-gw.onebound.cn/taobao/item_get/?key=t_856 2094008186&&num_iid={num_iid}&is_promotion=1&&lang=zh-CN&secret=20230114&cache=no"
        r = requests.get(url, headers=headers)
        json_obj = r.json()

        if "item" in json_obj.keys():
            if json_obj['item']['format_check'] == "ok":
                break
        time.sleep(1)
        loop_num += 1
        if loop_num == 5:
            break

    filename = f"{district}/{shop_id}/page_{page}/item_detail/{num_iid}/{num_iid}.json"
    isExist = os.path.exists(filename)

    if isExist is False:
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        with open(f"{district}/{shop_id}/page_{page}/item_detail/{num_iid}/{num_iid}.json", 'w') as f:
            json.dump(json_obj, f, indent=4)

    

    #loop for page count
    while page < page_count:
        page += 1
        loop_num = 0
        while True:
            print("start")
            url = f"https://api-gw.onebound.cn/taobao/item_search_shop/?key=t_856 2094008186&&shop_id=57301367&page={page}&sort=&&lang=zh-CN&secret=20230114"
            print(url)
            r = requests.get(url, headers=headers)
            json_obj = r.json()
            if "items" in json_obj.keys():
                print("true")
                break
            time.sleep(1)
            loop_num += 1
            if loop_num == 5:
                break
        
        filename = f'{district}/{shop_id}/page_{page}/page.json'
        isExist = os.path.exists(filename)

        if isExist is False:
            os.makedirs(os.path.dirname(filename), exist_ok=True)

            with open(f'{district}/{shop_id}/page_{page}/page.json', 'w') as f:
                json.dump(json_obj, f, indent=4)

        for item in json_obj['items']['item']:
            num_iid = item["num_iid"]
            pic_url = item["pic_url"]
            #image download    ====================
            if 'http' not in pic_url:
                pic_url = f"http:{pic_url}"
            response = requests.get(pic_url)
            # if response.status_code == 200:
            #     print("img")

            #     filename = f"{district}/{shop_id}/page_{page}/item_image/{num_iid}.jpg"
            #     os.makedirs(os.path.dirname(filename), exist_ok=True)

            #     with open(f"{district}/{shop_id}/page_{page}/item_image/{num_iid}.jpg", 'wb') as f:
            #         f.write(response.content)
            #     print("ok")
            #end image downlaod  ====================

            #page item detail
            loop_num = 0
            while True:
                url = f"https://api-gw.onebound.cn/taobao/item_get/?key=t_856 2094008186&&num_iid={num_iid}&is_promotion=1&&lang=zh-CN&secret=20230114&cache=no"
                r = requests.get(url, headers=headers)
                json_obj = r.json()

                if "item" in json_obj.keys():
                    if json_obj['item']['format_check'] == "ok":
                        break
                time.sleep(1)
                loop_num += 1
                if loop_num == 5:
                    break
                

            filename = f"{district}/{shop_id}/page_{page}/item_detail/{num_iid}/{num_iid}.json"
            isExist = os.path.exists(filename)

            if isExist is False:
                os.makedirs(os.path.dirname(filename), exist_ok=True)

                with open(f"{district}/{shop_id}/page_{page}/item_detail/{num_iid}/{num_iid}.json", 'w') as f:
                    json.dump(json_obj, f, indent=4)

        
        time.sleep(3)
