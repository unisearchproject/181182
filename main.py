# handlers ################

@bot.message_handler(commands=['start', 'help'])
def commands_handler(message):
    # обрабатываем отдельно команды /start и /help
    try:
        text = message.text
        user_id = message.chat.id
        
        if text == '/start':
            bot.send_message(user_id, cfg.start_message)
            if db.get_state(user_id) is None:
                new_state = start(nessage)
                db.set_state(user_id, new_state)
                
        elif text == '/help':
            bot.send_message(user_id, cfg.help_message)
            
    except ConnectionError:
        pass
    
   
@bot.message_handler(content_types=['text'])
def finite_state_machine(message):
    try:
        user_id = message.chat.id
        current_state = db.get_state(user_id)
        if current_state is None:
            current_state = start.__name__

        function = DICT_HANDLER[current_state]
        new_state = function(message)  # new state is function
        if new_state is not None:
            db.set_state(user_id, new_state)
    except ConnectionError:
        # не обрабатываем другие ошибки, т.к. это нам не  не надо
        pass
    
def start(message):
    # это будет начало нашего бота, отправка клавиатуры пользователю и информация о предметах
    keyboard = adjust_keyboard(cfg.subjects_keyboard)
    bot.send_message(
        message.chat.id, cfg.choice_subjects,
        reply_markup=reply_markup(keyboard)
    )
    db.set_vars(message.chat.id, keyboard_subjects=keyboard)
    return which_subjects


def which_subjects(message):
    # обрабатываем ввод предметов и сохраняем их, после спрашиваем баллы
    text = message.text.replace(
        cfg.added_char, '').replace(cfg.ignored_char, '')
    keyboard = db.get_var(message.chat.id, 'keyboard_subjects')

    if text == cfg.buttons_subjects_keyboard['apply']:
        subjects = pull_subjects(keyboard)
        if len(subjects) >= 3:
            bot.send_message(
                message.chat.id, cfg.subjects_saved,
                reply_markup=reply_markup(None)
            )
            bot.send_message(
                message.chat.id, cfg.which_points.format(
                    cfg.decode_subjects_dative[subjects[-1]]
                )
            )
            db.set_vars(message.chat.id, subjects=subjects, points=[])
            return which_points
        else:
            bot.send_message(message.chat.id, cfg.no_subjects)

    elif text in cfg.encode_subjects:
        keyboard = update_keyboard(text, keyboard)
        db.set_vars(message.chat.id, keyboard_subjects=keyboard)

        bot.send_message(
            message.chat.id,
            random.choice(cfg.nextsubj_messages),
            reply_markup=reply_markup(keyboard)
        )


def which_points(message):
    # обрабатываем ввод баллов, сохраняем их, после спросим регионы
    text = message.text
    user_id = message.chat.id

    if text.isdigit() and int(text) < 101:
        subjects = db.get_var(user_id, 'subjects')
        points = db.get_var(user_id, 'points')

        current_points = int(text)
        current_subject = subjects.pop()
        minimum_points = cfg.minimal_grades[
            cfg.decode_subjects_ucheba[current_subject]]

        if current_points >= minimum_points:
            points.append(
                {
                    'subject_id': current_subject,
                    'points': int(text)
                }
            )
            db.set_vars(user_id, subjects=subjects, points=points)
            if subjects:
                bot.send_message(
                    message.chat.id,
                    random.choice(cfg.following_points).format(
                        cfg.decode_subjects_dative[subjects[-1]]
                    )
                )
            else:
                bot.send_message(
                    message.chat.id, cfg.data_saved_message,
                    parse_mode='HTML')

                keyboard = adjust_keyboard(
                    [[cfg.break_button_regions]] +
                    [[city] for city in cfg.cities])
                bot.send_message(
                    message.chat.id, cfg.choice_regions,
                    reply_markup=reply_markup(keyboard)
                )
                db.set_vars(message.chat.id, keyboard_regions=keyboard)

                return which_regions
        else:  # баллы меньше минимальных
            bot.send_message(user_id, cfg.points_dont_match)
    else:  # пользователь ввел баллы неправильно
        bot.send_message(user_id, cfg.invalid_points)
        
        
def which_regions(message):
    # обрабатываем ввод регионов, выдаем найденые вузы
    # после отправляем repeat_serch_menu
    text = message.text.replace(cfg.added_char, '').replace(
        cfg.ignored_char, '')
    keyboard = db.get_var(message.chat.id, 'keyboard_regions')

    if text == cfg.break_button_regions:
        # геренируем аргументы для get_universities
        selected_regions = deepcopy(cfg.selected_cities)
        regions = pull_selected(keyboard)
        for region in regions:
            selected_regions[region] = True

        subjects = deepcopy(cfg.subjects)
        passed_exams = deepcopy(cfg.passed_exams)
        points = db.get_var(message.chat.id, 'points')
        for subj in points:
            title = cfg.decode_subjects_ucheba[subj['subject_id']]
            subjects[title] = subj['points']
            passed_exams[title] = True

        universities = unifinder.get_universities(
            _selected_cities=selected_regions,
            _subjects=subjects,
            _passed_exams=passed_exams
        )
        # выводим параметры поиска
        points_msg = '\n'.join(
            [
                cfg.data_saved.format(
                    cfg.decode_subjects[subj['subject_id']],
                    subj['points']
                )
                for subj in points
            ]
        )
        regions_msg = '\n'.join(regions)
        if not regions_msg:
            regions_msg = 'Не выбрано'
        parameters_msg = cfg.search_parameters.format(points_msg, regions_msg)
        bot.send_message(
            message.chat.id, parameters_msg, parse_mode='HTML')

        if universities:
            for univer in universities:
                title = univer['Название']
                object_id = db.save_programs(
                    univer_title=univer['Название'],
                    programs_url=univer['Программы']
                )
                keyboard = telebot.types.InlineKeyboardMarkup()
                button = telebot.types.InlineKeyboardButton(
                    text=cfg.button_programs, callback_data=object_id
                )
                keyboard.add(button)
                bot.send_message(
                    message.chat.id, title,
                    parse_mode='HTML', reply_markup=keyboard
                )
        else:
            bot.send_message(message.chat.id, cfg.nothing_found)

        bot.send_message(
            message.chat.id, cfg.repeat_search_message,
            reply_markup=reply_markup(cfg.repeat_serch_menu)
        )
        return repeat_serch_menu

    elif text in cfg.cities:
        keyboard = update_keyboard(text, keyboard)
        db.set_vars(message.chat.id, keyboard_regions=keyboard)
        bot.send_message(
            message.chat.id, random.choice(cfg.region_saved_messages),
            reply_markup=reply_markup(keyboard)
        )

    else:
        bot.send_message(message.chat.id, cfg.nonexist_region)
