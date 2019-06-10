 import requests

from bs4 import BeautifulSoup
import html2text

from cfg import ucheba_link, ucheba_for_abiturients_link, headers
from cfg import city_to_id, selected_cities, subjects, passed_exams
from cfg import exams_to_ids, max_tries, exceptions


def get_universities_data(
        url, headers=headers,
        try_count=max_tries, exceptions=exceptions):
    # достает данные вуза по ссылке
    while try_count:
        try_count -= 1
        try:
            r = requests.get(url, headers=headers)
            soup = BeautifulSoup(r.text, 'html.parser')
            universities = soup.find_all(
                'div', class_='search-results-item-inner'
            )

            universities_data = []
            for university in universities:
                current_university = {
                    'Название': html2text.html2text(
                        university.find_all(
                            'a', class_='js_webstat'
                        )[-1].text
                    ).replace('\n', ''),

                    'Проходной балл': html2text.html2text(
                        university.find_all(
                            'div', class_='big-number-h2'
                        )[0].text
                    ).replace('\n', ''),

                    'Бюджетных мест': html2text.html2text(
                        university.find_all(
                            'div', class_='big-number-h2 price-year'
                        )[0].text
                    ).replace('\n', ''),

                    'Стоимость': html2text.html2text(
                        university.find_all(
                            'div', class_='big-number-h2 price-year'
                        )[1].text).replace('\n', ''),

                    'Программы': html2text.html2text(
                        university.find_all(
                            'a',
                            class_='search-results-more-info js-search-'
                                   'results-more-info js_show_all_programs',
                            href=True
                        )[0]['data-programs-url']
                    ).replace('\n', '').replace(';', ''),

                    'Ссылка': html2text.html2text(
                        university.find_all(
                            'a', class_='js_webstat', href=True
                        )[0]['href']
                    ).replace('\n', '')
                }
                universities_data.append(current_university)
            return universities_data
        except exceptions as e:
            if not try_count:
                raise e


def get_university_programs(
        url, ucheba_link=ucheba_link, headers=headers,
        try_count=max_tries, exceptions=exceptions):
    # выдает программы университета по ссылке
    while try_count:
        try_count -= 1
        try:
            r = requests.get(ucheba_link + url, headers=headers)
            soup = BeautifulSoup(r.text, 'html.parser')
            programs = soup.find_all(
                'section', class_='search-results-info-item')
            programs_data = []
            for program in programs:
                current_program = {
                    'Название': html2text.html2text(
                        program.find_all(
                            'a', class_='js_webstat', href=True
                        )[0].text
                    ).replace('\n', ''),

                    'Степень': html2text.html2text(
                        program.find_all('div', class_='fs-small')[0].text
                    ).replace('\n', ''),

                    'Проходной балл': html2text.html2text(
                        program.find_all('div', class_='big-number-h2')[0].text
                    ).replace('\n', ''),

                    'Бюджетных мест': html2text.html2text(
                        program.find_all(
                            'div', class_='big-number-h2 price-year'
                        )[0].text
                    ).replace('\n', ''),

                    'Стоимость': html2text.html2text(
                        program.find_all(
                            'div', class_='big-number-h2 price-year'
                        )[1].text
                    ).replace('\n', ''),

                    'Ссылка': html2text.html2text(
                        program.find_all(
                            'a', class_='js_webstat', href=True
                        )[0]['href']
                    ).replace('\n', '')
                }

                programs_data.append(current_program)

            return programs_data
        except exceptions as e:
            if not try_count:
                raise e




def get_universities(
        _selected_cities, _subjects, _passed_exams,
        ucheba_link=ucheba_link, headers=headers, exams_to_ids=exams_to_ids,
        ucheba_for_abiturients_link=ucheba_for_abiturients_link):
    # выдает нужные университеты по нужным критериям

    if (sum(_subjects.values()) >= 3 and
            sum(x > 0 for x in _passed_exams.values()) >= 3):
        additional = ''
        for city, value in _selected_cities.items():
            if value:
                additional += 'eq%5B{}%5D=__l%3A{}&'.format(
                    city, city_to_id[city]
                )

        for subject, value in _subjects.items():
            if value:
                additional += '{}=1&'.format(exams_to_ids[subject]).replace(
                    'val', 'set')

                additional += '{}={}&'.format(
                    exams_to_ids[subject], subjects[subject]
                )

        string_ = f'{ucheba_link}{ucheba_for_abiturients_link}{additional}'
        return get_universities_data(url=string_)
    else:
        raise ValueError('Выберите минимум 3 экзамена')


if __name__ == '__main__':  # код для тестирования
    # Вопросы юзеру по поводу сданных предметов.

    check_list = [
        'готов сдать профильный, профессиональный или '
        'творческий экзамен в ВУЗе',
        'красный диплом',
        'ГТО'
    ]

    print('Answer yes/no')
    for exam in passed_exams:
        if exam not in check_list:
            q = input('Did you pass {} exam? '.format(exam))
            if q == 'yes':
                passed_exams[exam] = True
        else:
            q = input('What about {}? '.format(exam))
            if q == 'yes':
                passed_exams[exam] = True
    print('Done')

    print('Enter your bands, please.')
    for exam in passed_exams:
        if passed_exams[exam] and exam not in check_list:
            subjects[exam] = input(f'How many points did you get on {exam}? ')
    print('Done')

    print('Which cities do you prefer to study in?')
    for city in selected_cities:
        q = input('What about {}? '.format(city))
        if q == 'yes':
            selected_cities[city] = True
    print('Done')



