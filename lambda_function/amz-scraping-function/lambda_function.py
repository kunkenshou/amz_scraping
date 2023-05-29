import boto3
import urllib.request
from bs4 import BeautifulSoup
import time

def get_book_info(url, selector):
    while True:
        try:
            with urllib.request.urlopen(url) as html:
                soup = BeautifulSoup(html, "html.parser")
                title = soup.find("title").string
                price = soup.select_one(selector).string if soup.select_one(selector) else "価格情報が見つかりませんでした"
                return title, price
        except Exception as e:
            print(f"Error: {e}. Retrying in 10 seconds...")
            time.sleep(5)

def get_past_title(table_name, primary_key):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)
    response = table.get_item(Key={"Mail": primary_key, "ContentsName": "Amazon"})
    if 'Item' in response:
        return response['Item']['ContentsName']
    else:
        return None

def update_dynamodb(table, primary_key, secondary_key, data):
    past_title = get_past_title(table, primary_key)
    if past_title is not None and past_title != data["title"]:
        response = table.update_item(
            Key={
                "Mail": secondary_key,
                "ContentsName": primary_key
            },
            UpdateExpression="set ContentsName=:c, Price=:p, UpdateFlag=:u",
            ExpressionAttributeValues={
                ':c': data["title"],
                ':p': data["price"],
                ':u': 1
            },
            ReturnValues="UPDATED_NEW"
        )
        print("Updated DynamoDB Table: ", response)
    else:
        print("New title not found or same as past title. Skipped DynamoDB update.")

def add_to_dynamodb(table_name, primary_key, secondary_key, data):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)
    try:
        response = table.get_item(Key={"Mail": secondary_key, "ContentsName": primary_key})
        if 'Item' in response:
            update_dynamodb(table, primary_key, secondary_key, data)
        else:
            table.put_item(
                Item={
                    "Mail": secondary_key,
                    "ContentsName": "Amazon",
                    "Price": data["price"],
                    "Title": data["title"],
                    "URL": data["url"],
                    "UpdateFlag": 1
                }
            )
    except Exception as e:
        print(f"Error: {e}. Failed to update or add to DynamoDB.")

def lambda_handler(event, context):
    book_list = [
        {
            #奥井の英文読解 3つの物語            
            "url": "https://www.amazon.co.jp/dp/4796120289/?coliid=I370YNL8L980SB&colid=3ORR1NPPA61RG&psc=0&ref_=cm_sw_r_cp_ud_lstpd_J20EHF2BMT7B2RARG9RX",
            "selector": "span.olp-from"
        },
        {
            #英構文バイブル 梅山紀一
            "url": "https://www.amazon.co.jp/dp/4915053059/?coliid=I1W0Y0FRBXVEIM&colid=3ORR1NPPA61RG&psc=0&ref_=cm_sw_r_cp_ud_lstpd_J20EHF2BMT7B2RARG9RX",
            "selector": "span.olp-from"
        },
        {
            #英文法対応〈攻めの英文読解〉初めの一歩から実践へ―完全攻略
            "url": "https://www.amazon.co.jp/dp/4479190406/?coliid=I36OXEYUH2MWNN&colid=3ORR1NPPA61RG&psc=0&ref_=cm_sw_r_cp_ud_lstpd_J20EHF2BMT7B2RARG9RX",
            "selector": "span.olp-from"
        },
        {
            #石黒の英解公式 110番
            "url": "https://www.amazon.co.jp/dp/4312345031/?coliid=I316JDJUE8FSMZ&colid=3ORR1NPPA61RG&psc=0&ref_=cm_sw_r_cp_ud_lstpd_J20EHF2BMT7B2RARG9RX",
            "selector": "span.olp-from"
        },
        {
            #これだけ英文法 長文問題篇
            "url": "https://www.amazon.co.jp/dp/4255930325/?coliid=I3OJQ4SH08Q5QD&colid=3ORR1NPPA61RG&psc=0&ref_=cm_sw_r_cp_ud_lstpd_J20EHF2BMT7B2RARG9RX",
            "selector": "span.olp-from"
            #入試英文法93の盲点
        },
        {
            "url": "https://www.amazon.co.jp/dp/432776289X/?coliid=I3NINLAIAB3J3Q&colid=3ORR1NPPA61RG&psc=0&ref_=cm_sw_r_cp_ud_lstpd_J20EHF2BMT7B2RARG9RX",
            "selector": "span.olp-from"
        },
        {
            #高校で教えない英文解釈のコツ―合格点をかせげる
            "url": "https://www.amazon.co.jp/dp/4768010466/?coliid=I2DI6YK766MU2N&colid=3ORR1NPPA61RG&psc=0&ref_=cm_sw_r_cp_ud_lstpd_J20EHF2BMT7B2RARG9RX",
            "selector": "span.olp-from"
        },
        {
            #英文解釈ゼミ (大学入試 3グレードシリーズ2)
            "url": "https://www.amazon.co.jp/dp/4817710748/?coliid=I3IIZLH1KO0O9D&colid=3ORR1NPPA61RG&psc=0&ref_=cm_sw_r_cp_ud_lstpd_J20EHF2BMT7B2RARG9RX",
            "selector": "span.olp-from"
        },
        {
            #アクセス英熟語
            "url": "https://www.amazon.co.jp/dp/4255900094/?coliid=IF0GKHN3WERL5&colid=3ORR1NPPA61RG&psc=0&ref_=cm_sw_r_cp_ud_lstpd_J20EHF2BMT7B2RARG9RX",
            "selector": "span.olp-from"
        },
        {
            #なるほど英文法
            "url": "https://www.amazon.co.jp/dp/4255900140/?coliid=I14BT7BMW00MKB&colid=3ORR1NPPA61RG&psc=0&ref_=cm_sw_r_cp_ud_lstpd_J20EHF2BMT7B2RARG9RX",
            "selector": "span.olp-from"
        },
        {
            #英語構文SOS!! (上巻) 
            "url": "https://www.amazon.co.jp/dp/4806110086/?coliid=I1K2JN79S4EZD9&colid=3ORR1NPPA61RG&psc=0&ref_=cm_sw_r_cp_ud_lstpd_J20EHF2BMT7B2RARG9RX",
            "selector": "span.olp-from"
        },
        {
            #入試英語長文問題の正解法
            "url": "https://www.amazon.co.jp/dp/4385213224/?coliid=I2KV5TYY13TG9S&colid=3ORR1NPPA61RG&psc=0&ref_=cm_sw_r_cp_ud_lstpd_J20EHF2BMT7B2RARG9RX",
            "selector": "span.olp-from"
        },
        {
            #英文法ワンランクアップ12日間
            "url": "https://www.amazon.co.jp/dp/4792511798/?coliid=I2MA19FDDYIAP4&colid=3ORR1NPPA61RG&psc=0&ref_=cm_sw_r_cp_ud_lstpd_J20EHF2BMT7B2RARG9RX",
            "selector": "span.olp-from"
        },
        {
            #サクセス英文読解 (旺文社サクセスシリーズ)
            "url": "https://www.amazon.co.jp/dp/4010320788/?coliid=I3O4N2A9PU5TN1&colid=3ORR1NPPA61RG&psc=0&ref_=cm_sw_r_cp_ud_lstpd_J20EHF2BMT7B2RARG9RX",
            "selector": "span.olp-from"
        },
        {
            #みてすぐわかる英文解釈 (大学合格シリーズ)
            "url": "https://www.amazon.co.jp/dp/4385219729/?coliid=I20VVD9HM6ALG8&colid=3ORR1NPPA61RG&psc=0&ref_=cm_sw_r_cp_ud_lstpd_J20EHF2BMT7B2RARG9RX",
            "selector": "span.olp-from"
        },
        {
            #マーク式英語問題演習 (実戦力アップ)
            "url": "https://www.amazon.co.jp/dp/4385229538/?coliid=I3H3CTXRNH885G&colid=3ORR1NPPA61RG&psc=0&ref_=cm_sw_r_cp_ud_lstpd_J20EHF2BMT7B2RARG9RX",
            "selector": "span.olp-from"
        },
        {
            #記憶王が伝授する 場所法 英単語
            "url": "https://www.amazon.co.jp/dp/4385361428/?coliid=I3OI5KP9K7P096&colid=3ORR1NPPA61RG&psc=1&ref_=cm_sw_r_cp_ud_lstpd_J20EHF2BMT7B2RARG9RX",
            "selector": "span.olp-from"
        },
        {
            #江川の英文法・語法 (大学受験Doシリーズ)
            "url": "https://www.amazon.co.jp/dp/4010341793/?coliid=I2EAP005H0ZNCJ&colid=3ORR1NPPA61RG&psc=0&ref_=cm_sw_r_cp_ud_lstpd_J20EHF2BMT7B2RARG9RX",
            "selector": "span.olp-from"
        },
        {
            #福崎・柴田の英語長文―合格点への最短距離 (大学受験Do series)
            "url": "https://www.amazon.co.jp/dp/4010341815/?coliid=I11RHAIC764MO&colid=3ORR1NPPA61RG&psc=0&ref_=cm_sw_r_cp_ud_lstpd_J20EHF2BMT7B2RARG9RX",
            "selector": "span.olp-from"
        },
        {
            #めざせ!英語偏差値65+ (偏差値UPシリーズ)
            "url": "https://www.amazon.co.jp/dp/4893741217/?coliid=I39WEFQK7XFR2K&colid=3ORR1NPPA61RG&psc=0&ref_=cm_sw_r_cp_ud_lstpd_J20EHF2BMT7B2RARG9RX",
            "selector": "span.olp-from"
        },
        {
            #ズバリ!入試にでる英文法の盲点 (知的生きかた文庫)
            "url": "https://www.amazon.co.jp/dp/4837980236/?coliid=IPU9GYWH9G35J&colid=3ORR1NPPA61RG&psc=0&ref_=cm_sw_r_cp_ud_lstpd_J20EHF2BMT7B2RARG9RX",
            "selector": "span.olp-from"
        },
        {
            #超頻出!入試出題者が狙う英語問題237の盲点 (知的生きかた文庫)
            "url": "https://www.amazon.co.jp/dp/483798021X/?coliid=I1BI2DCGWVGN28&colid=3ORR1NPPA61RG&psc=0&ref_=cm_sw_r_cp_ud_lstpd_J20EHF2BMT7B2RARG9RX",
            "selector": "span.olp-from"
        },
        {
            #英語語法の征服　改訂版　(マイセレクト)
            "url": "https://www.amazon.co.jp/dp/4010383771/?coliid=I1N8S2WJF53HGG&colid=3ORR1NPPA61RG&psc=0&ref_=cm_sw_r_cp_ud_lstpd_J20EHF2BMT7B2RARG9RX",
            "selector": "span.olp-from"
        },
        {
            #大学入試センター試験英語問題演習 2 (実況中継シリーズ)
            "url": "https://www.amazon.co.jp/dp/4875684053/?coliid=ITZX2OZBEKBRM&colid=3ORR1NPPA61RG&psc=0&ref_=cm_sw_r_cp_ud_lstpd_J20EHF2BMT7B2RARG9RX",
            "selector": "span.olp-from"
        },
        {
            #英文法・語法標準問題集 (ベストセレクション)
            "url": "https://www.amazon.co.jp/dp/4828870210/?coliid=IB20LHLO0OMQU&colid=3ORR1NPPA61RG&psc=0&ref_=cm_sw_r_cp_ud_lstpd_J20EHF2BMT7B2RARG9RX",
            "selector": "span.olp-from"
        },
        {
            #松原の直前講習英語長文下線部訳混乱72 (大学入試ドタン場check)
            "url": "https://www.amazon.co.jp/dp/4053003148/?coliid=I3BGU815Z7E3ZH&colid=3ORR1NPPA61RG&psc=0&ref_=cm_sw_r_cp_ud_lstpd_J20EHF2BMT7B2RARG9RX",
            "selector": "span.olp-from"
        },
        {
            #図解英語構文の基本ルール20
            "url": "https://www.amazon.co.jp/dp/4385227225/?coliid=IL7HIDA2KE8ZN&colid=3ORR1NPPA61RG&psc=0&ref_=cm_sw_r_cp_ud_lstpd_J20EHF2BMT7B2RARG9RX",
            "selector": "span.olp-from"
        },
        {
            #読解力問題 (英語「新テスト」対策シリーズ)
            "url": "https://www.amazon.co.jp/dp/4327762741/?coliid=I3N9ZP4REC61D0&colid=3ORR1NPPA61RG&psc=0&ref_=cm_sw_r_cp_ud_lstpd_J20EHF2BMT7B2RARG9RX",
            "selector": "span.olp-from"
        },
        {
            #英語ここで差をつける・文法・語法の盲点 (河合塾シリーズ)
            "url": "https://www.amazon.co.jp/dp/4879995304/?coliid=I2LEIMSJSEHPI3&colid=3ORR1NPPA61RG&psc=0&ref_=cm_sw_r_cp_ud_lstpd_J20EHF2BMT7B2RARG9RX",
            "selector": "span.olp-from"
        },
        {
            #入試にでる英単語もう一つの意味
            "url": "https://www.amazon.co.jp/dp/4806107174/?coliid=I10L2O46T1MZ2T&colid=3ORR1NPPA61RG&psc=0&ref_=cm_sw_r_cp_ud_lstpd_J20EHF2BMT7B2RARG9RX",
            "selector": "span.olp-from"
        
        }
    ]

    for book in book_list:
        url = book["url"]
        selector = book.get("selector")
        try:
            title, price = get_book_info(url, selector)
            print(f"Title: {title}, Price: {price}")
            add_to_dynamodb("AmzScraping", "example@mail.com", url, {"title": title, "price": price, "url": url})
        except Exception as e:
            print(f"Error: {e}. Failed to get information for {url}.")
            
    return {}
