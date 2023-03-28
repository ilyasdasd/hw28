import json
import requests
from bs4 import BeautifulSoup
import unicodedata

url = 'https://spb.hh.ru/search/vacancy?text=python&area=1&area=2'
headers = {'Accept': '*/*',
           'User-Agent': 'Chrome'}
symbol_list = []
links_list = []
links_sorted_list = []
salary_list = []
company_name_list = []
location_list = []
data_list = []


def get_links():
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')
    vacancies = soup.find_all('a', class_='serp-item__title')
    for vacancy in vacancies:
        links = vacancy['href']
        links_list.append(links)
        response_links = requests.get(links, headers=headers)
        links_parsed = BeautifulSoup(response_links.text, 'lxml')
        descriptions = links_parsed.find('div', {'data-qa': 'vacancy-description'})
        if not descriptions:
            continue
        if ('Django' or 'django' or 'Flask' or 'flask') in descriptions.text:
            symbol_list.append('+')
        else:
            symbol_list.append('-')
    for i, c in zip(links_list, symbol_list):
        if c == "+":
            links_sorted_list.append(i)
    return links_sorted_list


def get_salary():
    for link in links_sorted_list:
        salary_link = requests.get(link, headers=headers)
        salary_parsed = BeautifulSoup(salary_link.text, 'lxml')
        salary = salary_parsed.find('span', class_="bloko-header-section-2 bloko-header-section-2_lite")
        if not salary:
            continue
        salary_text = salary.text
        salary_normalized = unicodedata.normalize('NFKD', salary_text)
        salary_list.append(salary_normalized)
    return salary_list


def get_company_name():
    for link in links_sorted_list:
        company_name_link = requests.get(link, headers=headers)
        company_name_parsed = BeautifulSoup(company_name_link.text, 'lxml')
        company_name_ = company_name_parsed.find('a', class_="bloko-link bloko-link_kind-tertiary")
        if not company_name_:
            continue
        company_name = company_name_['href']
        company_name_href = f'https://spb.hh.ru{company_name}'
        company_name_link_2 = requests.get(company_name_href, headers=headers)
        company_name_parsed_2 = BeautifulSoup(company_name_link_2.text, 'lxml')
        company_name_2 = company_name_parsed_2.find('span', class_="company-header-title-name")
        if not company_name_2:
            continue
        company_name_2_text = company_name_2.text
        company_name_normalized = unicodedata.normalize('NFKD', company_name_2_text)
        company_name_list.append(company_name_normalized)
    return company_name_list


def get_location():
    for link in links_sorted_list:
        location_link = requests.get(link, headers=headers)
        location_parsed = BeautifulSoup(location_link.text, 'lxml')
        location = location_parsed.find('p', {'data-qa': 'vacancy-view-location'})
        if not location:
            location = location_parsed.find('span', {'data-qa': 'vacancy-view-raw-address'})
            if not location:
                continue
        location_text = location.text
        location_list.append(location_text)
    return location_list


def get_data(links_, salaries, companies_names, locations):
    all_data = zip(links_, salaries, companies_names, locations)
    for link, salary, company_name, location in all_data:
        data_dict = {'link': link,
                     'salary': salary,
                     'company_name': company_name,
                     'location': location}
        data_list.append(data_dict)
    return data_list


get_links()
get_salary()
get_company_name()
get_location()
get_data(links_sorted_list, salary_list, company_name_list, location_list)

with open('data_file.json', 'w', encoding='utf-8') as data:
    json.dump(data_list, data, indent=2, ensure_ascii=False)
