from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import requests
import json
import glob
import pandas as pd

def get_urls():
    path = 'C:\\Users\\giehx\\Documents\\Python\\edgedriver_win64\\msedgedriver.exe'
    driver = webdriver.Edge(path)
    driver.get('https://kyou.id/search?q=Nendoroid&page=1%2C40&sort=newest') #change your url here
    # driver.get('https://kyou.id/search?q=poster&page=1%2C40&sort=newest')
    # driver.get(' https://kyou.id/search?q=poster&page=7%2C40&sort=newest')
    links = []
    try:
        while True:
            def x():
                find_urls = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located(
                        (By.CLASS_NAME, 'indexstyled__Thumbnail-sc-1vqzqkx-1 [href]'))
                )
                urls = [url.get_attribute('href') for url in find_urls]
                return urls

            next = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="__next"]/div[1]/div/div/div/div/div[2]/div[3]/div[2]/ul/li[7]'))
            )
            next_class = next.get_attribute('class')

            # while True:
            links.extend(x())
            next.click()
            if next_class == 'disabled':
                driver.quit()
    except:
        pass
    print(f'All urls obtained! {len(links)} totals')
    return links


def get_datas(links):
    req = requests.get(links)
    soup = BeautifulSoup(req.content, features='html.parser')

    try:
        productname = soup.find('h2', attrs={'class': 'product-view__content__title'}).text.strip().replace('/','').replace(',', '').replace('-', '_').replace(':',' ').replace('"','').replace('*','').replace('?','').replace('.','').replace('\n','')
    except:
        productname = 'Internal site page error'
    try:
        price_element = soup.find('span', attrs={'class': 'product-view__content__price'}).text.strip().replace('Earn','').split()
        price = price_element[0] + ' ' + price_element[1]
    except:
        price = 'no price'
    try:
        lis = soup.find_all('div', attrs={'class': 'info'})
    except:
        pass
    try:
        status = soup.find('span', attrs={'class': 'status'}).text
    except:
        status = 'no status'
    try:
        character = lis[0].text.strip().replace('Character: ', '')
    except:
        character = 'no character'
    try:
        series = lis[1].text.strip().replace('Series: ', '')
    except:
        series = 'no series'
    try:
        category = lis[2].text.strip().replace('Category: ', '')
    except:
        category = 'no category'
    try:
        manufacturer = lis[3].text.strip().replace('Category: ', '')
    except:
        manufacturer = 'no category'

    dict_data = {
        'Product Name': productname,
        'Status': status,
        'Price': price,
        'Character': character,
        'Category': category,
        'Series': series,
        'manufacturer': manufacturer
    }
    print("Saving : ", dict_data['Product Name'])


    file = './nendo_results/{}.json'.format(productname)
    with open(file, 'w', encoding='utf-8') as outfile:
        json.dump(dict_data, outfile)

def build_csv():
    print("Converting results to CSV file . . .")

    files = sorted(glob.glob('./nendo_results/*.json'))
    datas = []
    for file in files:
        print(file)
        with open(file) as json_file:
            data = json.load(json_file)
            datas.append(data)

    df = pd.DataFrame(datas)
    df.to_csv('nendo_results.csv', index=False)
    print("Output files generated!")


def run():
    start = input('Welcome to kyou.id scrapper, to start press Enter button: ')
    if start == "":
        print('Obtaining all urls . . .')
        links = get_urls()
        print('Obtaining all product datas . . .')
        # links = ['https://kyou.id/items/71415/nendoroid-ryza-atelier-ryza-tokoyami-no-joou-to-himitsu-no-kakurega']
        for link in links:
            get_datas(link)
        build_csv()
        print('All product datas obtained!')
        print('Program has finished!')
    else:
        print('Error, please try again!')
        run()


if __name__ == '__main__':
    run()
