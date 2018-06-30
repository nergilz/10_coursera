import random
import requests
import sys
import argparse
from openpyxl.workbook import Workbook
from bs4 import BeautifulSoup


def get_arguments():
    parser = argparse.ArgumentParser(
        description='This script get the data about course on coursera.org'
        )
    parser.add_argument(
        '--output',
        required=False,
        default='coursera-courses.xlsx',
        help='This is name for result .xlsx file'
        )
    parser.add_argument(
        '--count',
        required=False,
        type=int,
        default=20,
        help='Count urls for fetch information about course'
        )
    return parser.parse_args()


def fetch_html(url):
    try:
        response = requests.get(url)
        response.encoding = 'utf-8'
        return response.text

    except requests.HTTPError as error:
        sys.exit('ERROR: {}'.format(error))


def get_courses_urls(xtml_with_links):
    courses_urls = []

    soup = BeautifulSoup(xtml_with_links, 'lxml')
    loc_tags = soup.find_all('url')

    for element in loc_tags:
        courses_urls.append(element.find('loc').next)

    return courses_urls


def get_course_info(course_html):
    soup = BeautifulSoup(course_html, 'lxml')

    course_name = soup.find(
        'div',
        class_='course-info bt3-col-xs-6'
        ).find(
            'h2',
            class_='headline-4-text course-title'
            ).text.strip()

    commitment = soup.find(
        'td',
        class_='td-data'
        ).text.strip()

    try:
        rating = soup.find(
            'div',
            class_='ratings-text headline-2-text'
            ).find(
                'span'
                ).next.next
    except AttributeError:
        rating = None

    language = soup.find(
        'div',
        class_='rc-Language'
        ).next.next

    start_date = soup.find(
        'div',
        id='start-date-string'
        ).find(
            'span'
            ).text.strip()

    if rating is not None:
        rating = rating.split()[1]
    if start_date:
        date = start_date.split()
        start_date = '{}-{}'.format(date[1], date[2])

    return {
        'course_name': course_name,
        'rating': rating,
        'language': language,
        'start_date': start_date,
        'commitment': commitment
        }


def get_courses_data(random_urls):
    courses_data = {}

    for link in random_urls:
        course_html = fetch_html(link)
        course_info = get_course_info(course_html)
        courses_data.update({link: course_info})

    return courses_data


def output_courses_info_to_xlsx(courses_data):
    columns = ('Course_name', 'Rating', 'Language', 'Start_date', 'Commitment', 'Link')
    work_book = Workbook()
    work_sheet = work_book.active
    work_sheet.append(columns)

    for link, data in courses_data.items():
        work_sheet.append(
            (data['course_name'],
             data['rating'],
             data['language'],
             data['start_date'],
             data['commitment'],
             link)
            )

    return work_book


def save_work_book(course_data):

    work_book = output_courses_info_to_xlsx(courses_data)
    work_book.save(arguments.output)


if __name__ == '__main__':
    url_xml_feed = 'https://www.coursera.org/sitemap~www~courses.xml'
    arguments = get_arguments()
    random_urls = []

    xml_with_links = fetch_html(url_xml_feed)
    courses_urls = get_courses_urls(xml_with_links)
    random_urls = random.sample(courses_urls, arguments.count)
    courses_data = get_courses_data(random_urls)
    save_work_book(courses_data)
