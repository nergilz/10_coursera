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

    course_name = soup.find('div', class_='course-info bt3-col-xs-6').find('h2', class_='headline-4-text course-title').text.strip()
    commitment = soup.find('td', class_='td-data').text.strip()

    try:
        rating = soup.find('div', class_='ratings-text headline-2-text').find('span').next.next
    except AttributeError:
        rating = None
        
    language = soup.find('div', class_='rc-Language').next.next
    start_date = soup.find('div', id='start-date-string').find('span').text.strip()

    if rating is not None:
        rating = rating.split()[1]
    if start_date:
        date = start_date.split()
        start_date = '{}-{}'.format(date[1], date[2])

    return course_name, rating, language, start_date, commitment


def output_courses_info_to_xlsx(courses_info):
    work_book = Workbook()
    work_sheet = work_book.active

    for row in courses_info:
        work_sheet.append(row)

    work_book.save('coursera_courses.xlsx')


def main():
    url = 'https://www.coursera.org/sitemap~www~courses.xml'
    courses_slug = []
    count_urls = 20

    try:
        get_file_xml(url)
        courses_list = get_courses_list()
        courses_slug = random.sample(courses_list, count_urls)
        columns = ['Id', 'Course_name', 'Rating', 'Language', 'Start_date', 'Commitment', 'Link']
        courses_info = [columns]

        for count_id, link in enumerate(courses_slug, 1):
            course_data = [count_id]
            course_html = get_html_text(link)
            course_info = get_course_info(course_html)
            course_data.extend(course_info)
            course_data.append(link)
            courses_info.append(course_data)

        output_courses_info_to_xlsx(courses_info)

    except requests.HTTPError as error:
        sys.exit('ERROR: {}'.format(error))


if __name__ == '__main__':
    main()
