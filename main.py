def start(message):
    # это будет начало нашего бота, отправка клавиатуры пользователю и информация о предметах
    keyboard = adjust_keyboard(cfg.subjects_keyboard)
    bot.send_message(
        message.chat.id, cfg.choice_subjects,
        reply_markup=reply_markup(keyboard)
    )
    db.set_vars(message.chat.id, keyboard_subjects=keyboard)
    return which_subjects

# все функции добавить в отдельную папку (cfg с андреем и никой обсудить)
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
