import requests
from bs4 import BeautifulSoup
import csv
import json


def get_token_cookies(url, headers):
    req = requests.get(url, headers=headers, timeout=10)
    cookies = req.cookies
    soup = BeautifulSoup(req.text, 'lxml')
    token = soup.find(attrs={"name": "CSRFToken"})
    return token["value"], cookies


def count_pages(query_url, headers):
    list_pages = []
    list_pages.append(query_url)
    req = requests.get(query_url, headers=headers, timeout=10)
    soup = BeautifulSoup(req.text, 'lxml')
    try:
        pagination = soup.find_all('div', class_="b-pagination")
        for i in pagination:
            page = "https://366.ru/" + i.find("a").get("href")
            list_pages.append(page)
        return list_pages
    except Exception as ex:
        print(ex)


def get_numbers(id_drug, headers, cookies):
    list_pharm = []
    try:
        url = "https://366.ru/stockdb/ajax/product/" + str(id_drug) + "/stores/all?sortName=recommend&sortType=ASC"
        req = requests.get(url, headers=headers, cookies=cookies, timeout=10)
        data_json = json.loads(req.content.decode('utf-8'))
        for i in range(data_json['total']):
                if int(data_json['data'][i]["productCounts"][id_drug]) > 0:
                    list_pharm.append(data_json['data'][i]["name"])
        print("Аптек добавлено - ", len(list_pharm))
        return list_pharm
    except Exception as ex:
        print(ex)


def description_drugs(query_url, headers):
    token, cookies = get_token_cookies(query_url, headers)
    print('Токен поиска определен')
    pages = count_pages(query_url, headers)
    print('Количество страниц определено - ', len(pages))
    count_page = 1 #счетчик страниц
    count_drug = 0 #счетчик лекарств
    for i in pages:
        req_page = requests.get(i, headers=headers, cookies=cookies, timeout=15)
        print("\nСтраница поиска №" + str(count_page) + " загружена")
        soup = BeautifulSoup(req_page.content, 'lxml')
        try:
            list_drugs = soup.find_all('div', class_="listing_product__desc")
            for item in list_drugs:
                name = item.a['data-gtm-name']
                print()
                print(name)
                manufacturer = item.find('div', class_='listing_product__manufacturer').text[33:]
                material = item.find('div', class_='i-text-ellipsis').text
                manufacturer_brand = manufacturer[:manufacturer.index(material)]
                price = item.a['data-gtm-price']
                id_drug = item.a['data-gtm-id']
                with open("№" + str(count_drug + 1), 'w') as save:
                    writer = csv.writer(save, delimiter=',')
                    writer.writerow(["№", "Name", "Manufacturer", "Address", "Price"])
                    list_pharm = get_numbers(id_drug, headers, cookies)
                    k = 0
                    if len(list_pharm) > 0:
                        data = {
                        'CSRFToken': token,
                        'names': list_pharm
                        }
                        url = "https://366.ru/stockdb/ajax/product/" + str(id_drug) + "/stores/names"
                        req_store = requests.post(url, headers=headers, cookies=cookies, data=data, timeout=10)
                        data_json = json.loads(req_store.content.decode('utf-8'))
                        for i in range(len(list_pharm)):
                            k += 1
                            address = data_json[i]["displayName"], data_json[i]["address"]
                            writer.writerow([k, name, manufacturer_brand, address, price])
                    else:
                        k += 1
                        address = 'None'
                        writer.writerow([k, name, manufacturer_brand, address, price])
                    count_drug += 1
                    print('Лекарств записано - ', count_drug)

            print("\nСтраниц обработано - ", count_page)
            count_page += 1

        except Exception as ex:
            print(ex)


headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36",
}

query_url = input("Введите URL в виде 'https://366.ru/spb/search/?text=название_лекарства'\n")
# query_url = "https://366.ru/spb/search/?text=азитромицин"
description_drugs(query_url, headers)
