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
    return parser.parse_args()


def fetch_html(url):
    response = requests.get(url)
    response.encoding = 'utf-8'
    return response.text


def get_courses_list(html_with_links):
    courses_list = []

    soup = BeautifulSoup(html_with_links, 'lxml')
    loc_tags = soup.find_all('url')

    for element in loc_tags:
        courses_list.append(element.find('loc').next)

    return courses_list


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


def output_courses_info_to_xlsx(data_for_xlsx):
    work_book = Workbook()
    work_sheet = work_book.active

    for row in data_for_xlsx:
        work_sheet.append(row)

    return work_book


def main():
    url = 'https://www.coursera.org/sitemap~www~courses.xml'
    arguments = get_arguments()
    courses_slug = []
    count_urls = 20

    try:
        html_with_links = fetch_html(url)
        courses_list = get_courses_list(html_with_links)
        courses_slug = random.sample(courses_list, count_urls)
        columns = [
            'Id',
            'Course_name',
            'Rating',
            'Language',
            'Start_date',
            'Commitment',
            'Link'
            ]
        data_for_xlsx = [columns]

        for count_id, link in enumerate(courses_slug, 1):
            course_data = [count_id]
            course_html = fetch_html(link)
            course_info = get_course_info(course_html)

            course_data.extend(
                [course_info['course_name'],
                 course_info['rating'],
                 course_info['language'],
                 course_info['start_date'],
                 course_info['commitment']]
                )
            course_data.append(link)
            data_for_xlsx.append(course_data)

        work_book = output_courses_info_to_xlsx(data_for_xlsx)
        work_book.save(arguments.output)

    except requests.HTTPError as error:
        sys.exit('ERROR: {}'.format(error))


if __name__ == '__main__':
    main()
