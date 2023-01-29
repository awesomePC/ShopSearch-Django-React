from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import SearchHistorySerializer, ItemsSerializer
from .models import SearchHistory, Items
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.core import files
from io import BytesIO
import requests
import urllib.request
import json
import os
import time

#global variables
url_list = []
page_count = 0
new_search = False

########################################################################
#retrieve search history for dropdown data in the offline mode first page
@api_view(['GET', 'POST'])
def search_history(request):
    if request.method =='GET':
        search_history = SearchHistory.objects.all()
        serializer = SearchHistorySerializer(search_history, many=True)
        return Response(serializer.data)

    if request.method =='POST':  
        print(request.data)
        print("request.data")
        serializer = SearchHistorySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        # return Response ({"name": "superstar"})

#in online mode#     
#according to selected keyword, download images and save data in DB
@api_view(['GET'])
def online_items(request):
    #delete all database

    # items = Items.objects.all()
    # history = SearchHistory.objects.all()
    # for i in items:
    #     i.delete()
    # for j in history:
    #     j.delete()

    #end delete all database

    per_page = int(request.query_params.get('per_page'))
    page_num = int(request.query_params.get('page_num'))
    # key = "t_856 2094008186"
    key = request.query_params.get('key')
    # secret = "20230114"
    secret = request.query_params.get('secret')
    # search_keyword = "dell"
    search_keyword = request.query_params.get('search_keyword')
    
    district = request.query_params.get('district')

    global page_count, new_search
    
    arr_argument = []
    arr_argument.append(key)
    arr_argument.append(secret)
    arr_argument.append(search_keyword)
    arr_argument.append(district)
    arr_argument.append(1)
    receive_json_and_analyse(arr_argument)
    # receive_json_and_analyse(key, secret, search_keyword, district, 1)

    if page_count != 0 and not new_search:
        print("pagenum", page_count)
        page_list = []
        for page in range(2,page_count):
            arr_argument = []
            arr_argument.append(key)
            arr_argument.append(secret)
            arr_argument.append(search_keyword)
            arr_argument.append(district)
            arr_argument.append(page)
            page_list.append(arr_argument)
            
            page_count = receive_json_and_analyse(arr_argument)
        
        # from concurrent.futures import ThreadPoolExecutor
        # with ThreadPoolExecutor(max_workers=16) as executor:
        #     executor.map(receive_json_and_analyse, page_list)

        # Adding information about user agent
        opener=urllib.request.build_opener()
        opener.addheaders=[('User-Agent','Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1941.0 Safari/537.36')]
        urllib.request.install_opener(opener)

        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=16) as executor:
        #executor.map(downloadImage, url_list) #urls=[list of url]
            executor.map(downloadOneImage, url_list) #urls=[list of url]
    
    #initialize global variables
    page_count = 0
    new_search = False

    items = Items.objects.filter(District=district, SearchKeyword=search_keyword).order_by('-id')
    total = items.count()
    start = per_page*(page_num-1)
    end = per_page*(page_num-1) + per_page
    if end > total:
        end = total
    items = items[start: end]

    serializer = ItemsSerializer(items, many=True)

    return Response({"data":serializer.data, "total": total})

#in offline mode#
#according to selected keyword retrieve data from DB 
@api_view(['GET', 'POST'])
def offline_items(request):
    
    if request.method =='GET':
        per_page = int(request.query_params.get('per_page'))
        page_num = int(request.query_params.get('page_num'))
        # print(request.data['District'])
      
        if request.query_params.get('search_keyword') == "":
            items = Items.objects.all().order_by('-id')
            total = items.count()
            start = per_page*(page_num-1)
            end = per_page*(page_num-1) + per_page
            if end > total:
                end = total
            items = items[start: end]
        else:
            items = Items.objects.filter(District=request.query_params.get('district'), SearchKeyword=request.query_params.get('search_keyword')).order_by('-id')
            total = items.count()
            start = per_page*(page_num-1)
            end = per_page*(page_num-1) + per_page
            if end > total:
                end = total
            items = items[start: end]

        serializer = ItemsSerializer(items, many=True)

        return Response({"data":serializer.data, "total": total})
        
    if request.method =='POST':
        serializer = ItemsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

def localPathFrom(url):
    urlForDic = url.split("//")[1]
    folder, fn = os.path.split(urlForDic)
    filename = f"media/images/{folder}/{fn}"
    return filename

def addDownloadUrl(url):
    pic_url = url
    if 'http' not in pic_url:
        pic_url = f"http:{pic_url}"

    filename = localPathFrom(pic_url)
    isExist = os.path.exists(filename)

    if isExist is False:
        global url_list
        url_list.append(pic_url)

def downloadOneImage(image_url):
    print(image_url)
    filename = localPathFrom(image_url)
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    path, headers = urllib.request.urlretrieve(image_url, filename)
    #print(headers)    
    #time.sleep(5)

#donwload json
# def receive_json_and_analyse(key, secret, search_keyword, district, page):
def receive_json_and_analyse(arr_argument):
    key, secret, search_keyword, district, page = [element for element in arr_argument]
    print('page', page)
    url = f"https://api-gw.onebound.cn/{district}/item_search/?key={key}&secret={secret}&q={search_keyword}&start_price=0&end_price=0&page={page}&cat=0&discount_only=&sort =&page_size=&seller_info=&nick=&ppath=&imgid=&filter="

    headers = {
        "Accept-Encoding": "gzip",
        "Connection": "close"
    }
    if page == 1:
        global new_search
        search_history = SearchHistory.objects.filter(District=district, SearchKeyword=search_keyword).exists()
        print("history:", search_history)
        
        new_search = not search_history

    if new_search:
        print("no exist")
        while True:
            print("start")
            r = requests.get(url, headers=headers)
            json_obj = r.json()
            # print(json_obj)
            if "items" in json_obj.keys():
                print("true")
                if page == 1:
                    global page_count
                    page_count = int(json_obj['items']["pagecount"])
                    new_search_history = SearchHistory(District=district, SearchKeyword=search_keyword)
                    new_search_history.save()
                break
            time.sleep(1)
            loop_num += 1
            if loop_num == 5:
                break

        
        for obj in json_obj['items']["item"]:
            if obj["pic_url"] is None:
                filename = None
            else:
                addDownloadUrl(obj["pic_url"])
                pic_url = obj["pic_url"]
                if 'http' not in pic_url:
                    pic_url = f"http:{pic_url}"
                print("pic_url", pic_url)
                filename = localPathFrom(pic_url)
                print("filename", filename)
            new_item = Items(District=district, 
                            SearchKeyword=search_keyword,
                            Title=obj["title"],
                            PicUrl=obj["pic_url"],
                            PromotionPrice=obj["promotion_price"],
                            Image=filename,
                            Price=obj["price"],
                            Sales=obj["sales"],
                            NumIid=obj["num_iid"],
                            SellerNick=obj["seller_nick"],
                            SellerID=obj["seller_id"],
                            DetailUrl=obj["detail_url"],)
            new_item.save()
    
            # from django.core import files
            # from io import BytesIO
            # import requests
            # pic_url = obj["pic_url"]
            # if 'http' not in pic_url:
            #     pic_url = f"http:{pic_url}"
                
            # urlForDic = pic_url.split("//")[1]
            # img_filename = urlForDic.split("/")[3]
            # # url = "https://example.com/image.jpg"
            # resp = requests.get(pic_url)
            # if resp.status_code != requests.codes.ok:
            #     #  Error handling here
            #     pass
            # else:
            #     fp = BytesIO()
            #     fp.write(resp.content)
            #     # file_name = url.split("/")[-1]  # There's probably a better way of doing this but this is just a quick example
            #     new_item.Image.save(img_filename, files.File(fp))
            # time.sleep(2)

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
        # ################################
        # loop_num = 0
        # while True:
        #     print("start")
        #     r = requests.get(url, headers=headers)
        #     json_obj = r.json()
        #     print(json_obj)
        #     if "items" in json_obj.keys():
        #         print("true")
        #         break
        #     time.sleep(1)
        #     loop_num += 1
        #     if loop_num == 5:
        #         break
        # #analyse first response to get data including page count...
        # # print(json_obj['items']['page_count'])
        # global page_count, shop_id, district
        

        # page = int(json_obj['items']['page'])
        # page_count = int(json_obj['items']['page_count'])
        
        # #analyse url to get neccessary info
        # url_split = url.split("/")

        # #district --> example: taobao, 1688, Dangdang...
        # district = url_split[3]+"_json"

        # #shop id inside district
        # shop_id = url_split[5].split("&&")[1].split("&")[0]

        # filename = f'{district}/{shop_id}/page_{page}/page.json'
        # isExist = os.path.exists(filename)

        # if isExist is False:
        #     os.makedirs(os.path.dirname(filename), exist_ok=True)

        #     with open(f'{district}/{shop_id}/page_{page}/page.json', 'w') as f:
        #         json.dump(json_obj, f, indent=4)



        # for item in json_obj['items']['item']:
        #     # downloadJson(item, page)
        #     # downloadImage(filename,f"{prev}/{filename}")
        #     downloadThread = Thread(target=downloadJson, args=(item, page, ))
        #     downloadThread.isDaemon = True
        #     downloadThread.start()




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
