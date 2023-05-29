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

            #かてる英文解釈
            "url": "https://www.amazon.co.jp/dp/4877255060/?coliid=I196AQR5OV8T91&colid=3ORR1NPPA61RG&psc=0&ref_=cm_sw_r_cp_ud_lstpd_J20EHF2BMT7B2RARG9RX",
            "selector": "span.olp-from"
        },
        {
            #長文読解のベスト対策試験に出る抽象名詞 (大学受験武蔵の抜群シリーズ 14)
            "url": "https://www.amazon.co.jp/dp/4895260143/?coliid=I20KSSEMSZYVKF&colid=3ORR1NPPA61RG&psc=0&ref_=cm_sw_r_cp_ud_lstpd_J20EHF2BMT7B2RARG9RX",
            "selector": "span.olp-from"
        },
        {
            #西谷の英語重要語法96
            "url": "https://www.amazon.co.jp/dp/4896804864/?coliid=I10NMSBTHCLRWS&colid=3ORR1NPPA61RG&psc=0&ref_=cm_sw_r_cp_ud_lstpd_J20EHF2BMT7B2RARG9RX",
            "selector": "span.olp-from"
        },
        {
            #プラトンの英作文講義
            "url": "https://www.amazon.co.jp/dp/4327762903/?coliid=I3C275GNIT6VJ1&colid=3ORR1NPPA61RG&psc=0&ref_=cm_sw_r_cp_ud_lstpd_J20EHF2BMT7B2RARG9RX",
            "selector": "span.olp-from"
        },
        {
            #ねむる直前に読む英語暗記例文
            "url": "https://www.amazon.co.jp/dp/4844025376/?coliid=I3724BT55037DK&colid=3ORR1NPPA61RG&psc=0&ref_=cm_sw_r_cp_ud_lstpd_J20EHF2BMT7B2RARG9RX",
            "selector": "span.olp-from"
        },
        {
            #基礎問 英語長文 (大学入試基礎問シリーズ)
            "url": "https://www.amazon.co.jp/dp/4053007321/?coliid=I3MK3DJUYY6GK1&colid=3ORR1NPPA61RG&psc=0&ref_=cm_sw_r_cp_ud_lstpd_J20EHF2BMT7B2RARG9RX",
            "selector": "span.olp-from"
        },
        {
            #スクリーンプレイ学習法―シナリオのからくり、セリフのなりたち
            "url": "https://www.amazon.co.jp/dp/4894070014/?coliid=IRHT3608Q6W1K&colid=3ORR1NPPA61RG&psc=0&ref_=cm_sw_r_cp_ud_lstpd_J20EHF2BMT7B2RARG9RX",
            "selector": "span.olp-from"
        },
        {
            #これでナットク!前置詞・副詞―映画で学ぶ生きた英文法学習
            "url": "https://www.amazon.co.jp/dp/4894071088/?coliid=INUUONO2MDMP7&colid=3ORR1NPPA61RG&psc=0&ref_=cm_sw_r_cp_ud_lstpd_J20EHF2BMT7B2RARG9RX",
            "selector": "span.olp-from"
        },
        {
            #映画で学ぶ英語構文120
            "url": "https://www.amazon.co.jp/dp/4894070243/?coliid=I3QY2JHCL0KP90&colid=3ORR1NPPA61RG&psc=0&ref_=cm_sw_r_cp_ud_lstpd_J20EHF2BMT7B2RARG9RX",
            "selector": "span.olp-from"
        },
        {
            #横山英文速読入門講義の実況中継―高2~大学入試
            "url": "https://www.amazon.co.jp/dp/4875685297/?coliid=IAGSPBVOHR3CR&colid=3ORR1NPPA61RG&psc=0&ref_=cm_sw_r_cp_ud_lstpd_J20EHF2BMT7B2RARG9RX",
            "selector": "span.olp-from"
        },
        {
            #津守の英語のしくみ基礎のキソ part.2 (代ゼミTVネットシリーズ)
            "url": "https://www.amazon.co.jp/dp/4896805372/?coliid=IK5NBNR76XOOE&colid=3ORR1NPPA61RG&psc=0&ref_=cm_sw_r_cp_ud_lstpd_J20EHF2BMT7B2RARG9RX",
            "selector": "span.olp-from"
        },
        {
            #木原のENGLISHラリー語法・表現・熟語 (Part.2) (Yozemi TV‐net)
            "url": "https://www.amazon.co.jp/dp/4896805283/?coliid=I2Q0PDW7XC0FE9&colid=3ORR1NPPA61RG&psc=0&ref_=cm_sw_r_cp_ud_lstpd_J20EHF2BMT7B2RARG9RX",
            "selector": "span.olp-from"
        },
        {
            #凄語法構文マニュアル―試験場まできっと持って行く
            "url": "https://www.amazon.co.jp/dp/4327764507/?coliid=INQC48PAD32N1&colid=3ORR1NPPA61RG&psc=0&ref_=cm_sw_r_cp_ud_lstpd_J20EHF2BMT7B2RARG9RX",
            "selector": "span.olp-from"
        },
        {
            #英語の本質がよくわかる英文法講話
            "url": "https://www.amazon.co.jp/dp/4844025384/?coliid=I3IJX6CV9Q7F0M&colid=3ORR1NPPA61RG&psc=0&ref_=cm_sw_r_cp_ud_lstpd_J20EHF2BMT7B2RARG9RX",
            "selector": "span.olp-from"
        },
        {
            #スーパー英文読解演習 1
            "url": "https://www.amazon.co.jp/dp/484600211X/?coliid=I5HFBHMR3M1S&colid=3ORR1NPPA61RG&psc=0&ref_=cm_sw_r_cp_ud_lstpd_J20EHF2BMT7B2RARG9RX",
            "selector": "span.olp-from"
        },
        {
            #スーパー英文読解演習 3
            "url": "https://www.amazon.co.jp/dp/4846002136/?coliid=IZHED267F1CJB&colid=3ORR1NPPA61RG&psc=0&ref_=cm_sw_r_cp_ud_lstpd_J20EHF2BMT7B2RARG9RX",
            "selector": "span.olp-from"
        },
        {
            #英語読解力問題 (センター試験対策シリーズ)
            "url": "https://www.amazon.co.jp/dp/4327763624/?coliid=I3PQAXV6F8LBLZ&colid=3ORR1NPPA61RG&psc=0&ref_=cm_sw_r_cp_ud_lstpd_J20EHF2BMT7B2RARG9RX",
            "selector": "span.olp-from"
        },
        {
            #わかる使える最重要英単語751
            "url": "https://www.amazon.co.jp/dp/4327763624/?coliid=I3PQAXV6F8LBLZ&colid=3ORR1NPPA61RG&psc=0&ref_=cm_sw_r_cp_ud_lstpd_J20EHF2BMT7B2RARG9RX",
            "selector": "span.olp-from"
        },
        {
            #大学入試 登木健司の 英文読解が戦略的にできる本
            "url": "https://www.amazon.co.jp/dp/4046003162/?coliid=I10W6V7FZCWUCK&colid=3ORR1NPPA61RG&psc=0&ref_=cm_sw_r_cp_ud_lstpd_J20EHF2BMT7B2RARG9RX",
            "selector": "span.olp-from"
        },
        {
            #正規表現の達人 第2版
            "url": "https://www.amazon.co.jp/dp/4797330813/?coliid=I7G2JRUOS82XW&colid=3ORR1NPPA61RG&psc=0&ref_=cm_sw_r_cp_ud_lstpd_J20EHF2BMT7B2RARG9RX",
            "selector": "span.olp-from"
        },
        {
            #実戦英語　作戦要務令
            "url": "https://www.amazon.co.jp/dp/4896800400/?coliid=I1TECLO702JUIF&colid=3ORR1NPPA61RG&psc=0&ref_=cm_sw_r_cp_ud_lstpd_J20EHF2BMT7B2RARG9RX",
            "selector": "span.olp-from"
        },
        {
            #センター試験英語攻略本
            "url": "https://www.amazon.co.jp/dp/4566048772/?coliid=I3D6MT7XFHSUAZ&colid=3ORR1NPPA61RG&psc=0&ref_=cm_sw_r_cp_ud_lstpd_J20EHF2BMT7B2RARG9RX",
            "selector": "span.olp-from"
        },
        {
            #瀬下英語入門講義の実況中継(上)
            "url": "https://www.amazon.co.jp/dp/4875682565/?coliid=I35JK5IQW8X45D&colid=3ORR1NPPA61RG&psc=0&ref_=cm_sw_r_cp_ud_lstpd_J20EHF2BMT7B2RARG9RX",
            "selector": "span.olp-from"
        },
        {
            #英文読解33―理系の文章で学ぶ (大学受験英語ワークアウト・シリーズ)
            "url": "https://www.amazon.co.jp/dp/4943880053/?coliid=I243FQKMIFP876&colid=3ORR1NPPA61RG&psc=0&ref_=cm_sw_r_cp_ud_lstpd_J20EHF2BMT7B2RARG9RX",
            "selector": "span.olp-from"
        },
        {
            #数学SOS!! (数2・数B編) (東大銀杏学舎の面白いほど受かるシリーズ)
            "url": "https://www.amazon.co.jp/dp/4806110507/?coliid=IIYKOZIO1LJ3K&colid=3ORR1NPPA61RG&psc=0&ref_=cm_sw_r_cp_ud_lstpd_J20EHF2BMT7B2RARG9RX",
            "selector": "span.olp-from"
        },
        {
            #英文法SOS!!―ムダを徹底的に省いた最強の学習法! (超合格シリーズ)
            "url": "https://www.amazon.co.jp/dp/4806109282/?coliid=I1FMHTNCODYCIN&colid=3ORR1NPPA61RG&psc=0&ref_=cm_sw_r_cp_ud_lstpd_J20EHF2BMT7B2RARG9RX",
            "selector": "span.olp-from"
        },
        {
            #20人の東大生グループが書いた 最新 大学合格の勉強法が面白いほどわかる本―新課程の勉強法に完全対応
            "url": "https://www.amazon.co.jp/dp/480611023X/?coliid=I1ZGIR9G7WPZX9&colid=3ORR1NPPA61RG&psc=0&ref_=cm_sw_r_cp_ud_lstpd_J20EHF2BMT7B2RARG9RX",
            "selector": "span.olp-from"
        },
        {
            #受験の悩み相談 90のSOS!!―学校も親も決して教えてくれない! (超合格シリーズ)
            "url": "https://www.amazon.co.jp/dp/4806109061/?coliid=I1IA5WKDO4KN2O&colid=3ORR1NPPA61RG&psc=0&ref_=cm_sw_r_cp_ud_lstpd_J20EHF2BMT7B2RARG9RX",
            "selector": "span.olp-from"
        },
        {
            #大学合格の勉強法が面白いほどわかる本―ゴールへの20の超ヒント!
            "url": "https://www.amazon.co.jp/dp/4806108405/?coliid=I15D004V6W7QRY&colid=3ORR1NPPA61RG&psc=0&ref_=cm_sw_r_cp_ud_lstpd_RDTA7CGT4N6S792X5RN5",
            "selector": "span.olp-from"
        },
        {
            #福崎の英語長文特講 (シグマベスト―大学入試CD講義)
            "url": "https://www.amazon.co.jp/dp/4578009084/?coliid=I2FNBBJ2M7NQPG&colid=3ORR1NPPA61RG&psc=0&ref_=cm_sw_r_cp_ud_lstpd_J20EHF2BMT7B2RARG9RX",
            "selector": "span.olp-from"
        },
        {
            #小説の解き方―速読英語長文 (Scientific approach series)
            "url": "https://www.amazon.co.jp/dp/4806111481/?coliid=I2SDRA7EWV80BV&colid=3ORR1NPPA61RG&psc=0&ref_=cm_sw_r_cp_ud_lstpd_J20EHF2BMT7B2RARG9RX",
            "selector": "span.olp-from"
        },
        {
            #トップ講師の英語教室
            "url": "https://www.amazon.co.jp/dp/4844025252/?coliid=I25DILRSWM9HLR&colid=3ORR1NPPA61RG&psc=0&ref_=cm_sw_r_cp_ud_lstpd_J20EHF2BMT7B2RARG9RX",
            "selector": "span.olp-from"
        },
        {
            #徳重スペシャル パワーアップ英単語
            "url": "https://www.amazon.co.jp/dp/4896802195/?coliid=I3OL38I9GAN4I3&colid=3ORR1NPPA61RG&psc=0&ref_=cm_sw_r_cp_ud_lstpd_J20EHF2BMT7B2RARG9RX",
            "selector": "span.olp-from"
        },
        {
            #すぐ使える英文法問題を解く公式
            "url": "https://www.amazon.co.jp/dp/431233014X/?coliid=I6D4Q6HRN27V3&colid=3ORR1NPPA61RG&psc=0&ref_=cm_sw_r_cp_ud_lstpd_J20EHF2BMT7B2RARG9RX",
            "selector": "span.olp-from"
        },
        {
            #CD付 耳から覚える試験にでる英文解釈 (試験シリーズDX)
            "url": "https://www.amazon.co.jp/dp/4413038452/?coliid=I1WKD2NOVFP2E&colid=3ORR1NPPA61RG&psc=0&ref_=cm_sw_r_cp_ud_lstpd_J20EHF2BMT7B2RARG9RX",
            "selector": "span.olp-from"
        },
        {
            #逆配列英単語速習
            "url": "https://www.amazon.co.jp/dp/4875718047/?coliid=I2EDVAT30IY13Q&colid=3ORR1NPPA61RG&psc=0&ref_=cm_sw_r_cp_ud_lstpd_J20EHF2BMT7B2RARG9RX",
            "selector": "span.olp-from"
        },
        {
            #試験で差がつくラディカル英文法
            "url": "https://www.amazon.co.jp/dp/4903315010/?coliid=I2W2M7DOP1UAQM&colid=3ORR1NPPA61RG&psc=0&ref_=cm_sw_r_cp_ud_lstpd_J20EHF2BMT7B2RARG9RX",
            "selector": "span.olp-from"
        },
        {
            #精説英文読解　内容からのアプローチ (大学入試マグナム)
            "url": "https://www.amazon.co.jp/dp/4796912118/?coliid=IGTEJJZK9OZ44&colid=3ORR1NPPA61RG&psc=0&ref_=cm_sw_r_cp_ud_lstpd_J20EHF2BMT7B2RARG9RX",
            "selector": "span.olp-from"
        },
        {
            #〈思考する〉英文読解 (駿台レクチャー叢書)
            "url": "https://www.amazon.co.jp/dp/479612022X/?coliid=I1DWAEVL23BNZS&colid=3ORR1NPPA61RG&psc=0&ref_=cm_sw_r_cp_ud_lstpd_J20EHF2BMT7B2RARG9RX",
            "selector": "span.olp-from"
        },
        {
            #英文解釈秘解答術セブン
            "url": "https://www.amazon.co.jp/dp/4881990675/?coliid=I9R0K7NGV701N&colid=3ORR1NPPA61RG&psc=0&ref_=cm_sw_r_cp_ud_lstpd_J20EHF2BMT7B2RARG9RX",
            "selector": "span.olp-from"
        },
        {
            #6点からでも立ち直る英文読解
            "url": "https://www.amazon.co.jp/dp/4844025368/?coliid=IDQDDG4Y2U6C1&colid=3ORR1NPPA61RG&psc=0&ref_=cm_sw_r_cp_ud_lstpd_J20EHF2BMT7B2RARG9RX",
            "selector": "span.olp-from"
        },
        {
            #川田流英語のツボ―熱血講義だ全員集合!!
            "url": "https://www.amazon.co.jp/dp/4844025368/?coliid=IDQDDG4Y2U6C1&colid=3ORR1NPPA61RG&psc=0&ref_=cm_sw_r_cp_ud_lstpd_J20EHF2BMT7B2RARG9RX",
            "selector": "span.olp-from"
        },
        {
            #誰も教えてくれなかった英文解釈のテクニック
            "url": "https://www.amazon.co.jp/dp/4022190884/?coliid=I3QMZHP3T80XGB&colid=3ORR1NPPA61RG&psc=0&ref_=cm_sw_r_cp_ud_lstpd_J20EHF2BMT7B2RARG9RX",
            "selector": "span.olp-from"
        },
        {
            #代々木ゼミ方式 帆糸英語一気シリーズ (5) 副詞
            "url": "https://www.amazon.co.jp/dp/4896800818/?coliid=I7V6DHUBI9LM5&colid=3ORR1NPPA61RG&psc=0&ref_=cm_sw_r_cp_ud_lstpd_J20EHF2BMT7B2RARG9RX",
            "selector": "span.olp-from"
        },
        {
            #名人の授業 永田の英語の神髄 長文読解法講義 (東進ブックス―名人の授業)
            "url": "https://www.amazon.co.jp/dp/4890852794/?coliid=I2HAQLSP3KVD1C&colid=3ORR1NPPA61RG&psc=0&ref_=cm_sw_r_cp_ud_lstpd_J20EHF2BMT7B2RARG9RX",
            "selector": "span.olp-from"
        },
        {
            #口語英語で満点をとる!
            "url": "https://www.amazon.co.jp/dp/4806111511/?coliid=I2IB3Z1TFBO2PB&colid=3ORR1NPPA61RG&psc=0&ref_=cm_sw_r_cp_ud_lstpd_J20EHF2BMT7B2RARG9RX",
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
