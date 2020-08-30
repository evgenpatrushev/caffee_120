from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
from flask_mobility import Mobility

from source.google_sheets.google_sheets import GoogleSheets
from datetime import datetime

from source.forms.registration_form import get_reg_form

import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'source/'
Mobility(app)  # add mobility check function

# config key and language
app.secret_key = os.getenv("SECRET_KEY", "jkm-vsnej9l-vm9sqm3:lmve")

# config logger for heroku
if os.environ.get('HEROKU') is not None:
    import logging

    stream_handler = logging.StreamHandler()
    app.logger.addHandler(stream_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('server startup')

# config google sheets
google_obj = GoogleSheets()


# google_obj.add_row([
#     ['Имя', 'Фамилия', 'Пол', 'День рождения', 'Номер телефона', 'E-mail', 'Дата отправки']
# ])

@app.route('/')
def main_page():
    try:
        session['active_lang']
    except:
        session['active_lang'] = 'укр'

    if session['active_lang'] == 'укр':
        HOURS = 'Години роботи'
        interval = 'Пн-Пт'
        menu_str = 'Наше меню'
        registration_str = 'Реєстрація'
        message_str = 'Кава, найкраща органічна суспензія, коли-небудь розроблена.'
    elif session['active_lang'] == 'рус':
        HOURS = 'Часы работы'
        interval = 'Пн-Пт'
        menu_str = 'Наше меню'
        registration_str = 'Регистрация'
        message_str = 'Кофе - лучшая из когда-либо созданных органических суспензий.'
    else:
        HOURS = 'HOURS'
        interval = 'Mon-Fr'
        menu_str = 'Our menu'
        registration_str = 'Registration'
        message_str = 'Coffee, the finest organic suspension ever devised.'

    return render_template('main.html', HOURS=HOURS, interval=interval, menu_str=menu_str,
                           registration_str=registration_str, message_str=message_str)


@app.route('/menu')
def menu():
    # with open('source/120_coffee.pdf', 'rb') as file:
    return send_from_directory(app.config['UPLOAD_FOLDER'], '120_coffee.pdf')


def check_for_uniqueness(form):
    return False


@app.route('/change_lang')
def change_lang():
    # todo add request into last page (request.referrer)
    session['active_lang'] = request.args.get('lang')
    app.logger.info(f'Change language: {session["active_lang"]}')
    if request.referrer:
        if 'registration' in request.referrer:
            return redirect(url_for('registration'))
        else:
            return redirect(url_for('main_page'))
    else:
        return redirect(url_for('main_page'))


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    try:
        session['active_lang']
    except:
        session['active_lang'] = 'укр'

    form = get_reg_form(language=session['active_lang'])

    # Warning (костиль) - новый флакс вкл валидацию на InputRequired у клиента (нам так не нада)
    # form.name.flags.required = False
    # form.surname.flags.required = False
    # form.telephone_number.flags.required = False

    if request.method == 'POST':
        form.preprocessing()
        if not form.validate() and bool(form.birthday.raw_data[0]):
            app.logger.warning(f'POST form with error')
            return render_template('registration_form.html', form=form, form_name="Registration", action="registration",
                                   active=session['active_lang'])
        else:

            if check_for_uniqueness(form):
                return render_template('registration_form.html', form=form, form_name="Registration",
                                       action="registration", msg="error message", active=session['active_lang'])

            # todo add thread/async
            gender = {0: 'не выбран', 1: 'Женский', 2: 'Мужской'}
            birthday = form.birthday.data.strftime("%Y-%m-%d") if form.birthday.data else 'нет информации'
            google_obj.add_row([
                [form.name.data, form.surname.data, gender[form.gender.data], birthday,
                 form.telephone_number.data, form.email.data, datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
            ])

            app.logger.info(f'POST form with success')
            return render_template('success.html', active=session['active_lang'])

    app.logger.info(f'GET form')
    return render_template('registration_form.html', form=form, form_name="Registration", action="registration",
                           active=session['active_lang'])


# END DISCIPLINE ORIENTED QUERIES -----------------------------------------------------------------------------------

if __name__ == '__main__':
    app.run(debug=True)
