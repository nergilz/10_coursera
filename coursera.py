import random
import requests
import sys
from openpyxl.workbook import Workbook
from bs4 import BeautifulSoup


def get_file_xml(url):
    response = requests.get(url)
    with open('courses.xml', 'w') as file:
        file.write(response.text)


def get_courses_list():
    courses_list = []

    with open('courses.xml') as xml_hendler:
        xml = xml_hendler.read()

    soup = BeautifulSoup(xml, 'lxml')
    loc_tags = soup.find_all('url')

    for element in loc_tags:
        courses_list.append(element.find('loc').next)

    return courses_list


def get_html_text(link):
    response = requests.get(link)
    response.encoding = 'utf-8'
    return response.text


def get_course_info(html):
    soup = BeautifulSoup(html, 'lxml')

    try:
        name = soup.find('div', class_='course-info bt3-col-xs-6').find('h2', class_='headline-4-text course-title').text.strip()
    except AttributeError:
        name = None

    try:
        commitment = soup.find('td', class_='td-data').text.strip()
    except AttributeError:
        commitment = None

    try:
        rating = soup.find('div', class_='ratings-text headline-2-text').find('span').next.next
    except AttributeError:
        rating = None

    try:
        language = soup.find('div', class_='rc-Language').next.next
    except AttributeError:
        language = None

    try:
        start_date = soup.find('div', id='start-date-string').find('span').text.strip()
    except AttributeError:
        start_date = None

    if rating is not None:
        rating = rating.split()[1]
    if start_date:
        date = start_date.split()
        start_date = '{}-{}'.format(date[1], date[2])

    return name, rating, language, start_date, commitment


def output_courses_info_to_xlsx(courses_info):
    wbook = Workbook()
    wsheet = wbook.active

    for row in courses_info:
        wsheet.append(row)

    wbook.save('coursera_courses.xlsx')


if __name__ == '__main__':
    url = 'https://www.coursera.org/sitemap~www~courses.xml'
    courses_slug = []

    try:
        get_file_xml(url)
        courses_list = get_courses_list()
        courses_slug = random.sample(courses_list, 20)
        columns = ['Id', 'Course_name', 'Rating', 'Language', 'Start_date', 'Commitment', 'Link']
        courses_info = [columns]

        for count_id, link in enumerate(courses_slug, 1):
            course_data = [count_id]
            html = get_html_text(link)
            info = get_course_info(html)
            course_data.extend(info)
            course_data.append(link)
            courses_info.append(course_data)

        output_courses_info_to_xlsx(courses_info)

    except requests.HTTPError as error:
        sys.exit('ERROR: {}'.format(error))
