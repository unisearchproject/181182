def universities_data(
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



def get_universities(
        _selected_cities, _subjects, _passed_exams,
        ucheba_link = ucheba_link, headers=headers, exams_to_ids = exams_to_ids,
        ucheba_for_abiturients_link = ucheba_for_abiturients_link):
    # выдает нужные университеты по нужным критериям

    if (sum(_subjects.values()) >= 3 and
            sum(x > 0 for x in _passed_exams.values()) >= 3):
        additional = ''
        for city in range(len(_selected_cities)):
            if list(_selected_cities.items())[city][1]:
                additional += 'eq%5B{}%5D=__l%3A{}&'.format(
                    city,
                    city_to_id[list(_selected_cities.items())[city][0]]
                )

        for subject in range(len(_subjects)):
            if list(_passed_exams.items())[subject][1]:
                additional += '{}=1&'.format(
                    exams_to_ids[list(_passed_exams.items())[subject][0]]
                ).replace('val', 'set')

                additional += '{}={}&'.format(
                    exams_to_ids[list(_passed_exams.items())[subject][0]],
                    subjects[list(_passed_exams.items())[subject][0]]
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



