from django.db import models

# Create your models here.
##########item detail info from json ########################
# "title": "【24期分期】DELL/戴尔G15 5520 15.6英寸12代英特尔酷睿i5/i7游戏本3050笔记本电脑RTX3060手提学生外星人",
# "pic_url": "http://gw.alicdn.com/i2/379092568/O1CN015X22JF1UqBuA5oyjj_!!2-item_pic.png",
# "promotion_price": "8199.0",
# "price": "8199.0",
# "sales": 164,
# "num_iid": "673285931849",
# "seller_nick": "戴尔官方旗舰店",
# "seller_id": "379092568",
# "detail_url":
#################additional custom cell#############################
# # district: taobao
# # search_keyword: hp
# # image_url
####################################################################
class Items(models.Model):
    #custom cell
    District=models.CharField(max_length=255, null=True, blank=True)
    SearchKeyword=models.CharField(max_length=255, null=True, blank=True)
    # Image=models.ImageField(
    #     upload_to="images",
    #     max_length=500,
    #     null=True, blank=True
    # )

    #default cell from json file
    Title=models.CharField(max_length=255, null=True, blank=True)
    PicUrl=models.CharField(max_length=255, null=True, blank=True)
    DetailUrl=models.CharField(max_length=255, null=True, blank=True)
    Price=models.CharField(max_length=255, null=True, blank=True)
    PromotionPrice=models.CharField(max_length=255, null=True, blank=True)
    Sales=models.CharField(max_length=255, null=True, blank=True)
    NumIid=models.CharField(max_length=255, null=True, blank=True)
    SellerNick=models.CharField(max_length=255, null=True, blank=True)
    SellerID=models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.Title
    
class SearchHistory(models.Model):
    District=models.CharField(max_length=255, null=True, blank=True)
    SearchKeyword=models.CharField(max_length=255, null=True, blank=True)