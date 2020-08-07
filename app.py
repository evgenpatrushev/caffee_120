from flask import Flask, render_template, request, redirect, url_for
from flask_mobility import Mobility

from source.google_sheets.google_sheets import GoogleSheets
from datetime import datetime

from source.forms.registration_form import get_reg_form

import os


app = Flask(__name__)
Mobility(app)  # add mobility check function

# config key and language
app.secret_key = os.getenv("SECRET_KEY", "jkm-vsnej9l-vm9sqm3:lmve")
active_lang = 'укр'

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


def check_for_uniqueness(form):
    return False


@app.route('/change_lang')
def change_lang():
    global active_lang
    active_lang = request.args.get('lang')
    app.logger.info(f'Change language: {active_lang}')
    return redirect(url_for('registration'))


@app.route('/', methods=['GET', 'POST'])
def registration():
    form = get_reg_form(language=active_lang)

    # Warning (костиль) - новый флакс вкл валидацию на InputRequired у клиента (нам так не нада)
    # form.name.flags.required = False
    # form.surname.flags.required = False
    # form.telephone_number.flags.required = False

    if request.method == 'POST':
        form.preprocessing()
        if not form.validate() and bool(form.birthday.raw_data[0]):
            app.logger.warning(f'POST form with error')
            return render_template('registration_form.html', form=form, form_name="Registration", action="",
                                   active=active_lang)
        else:

            if check_for_uniqueness(form):
                return render_template('registration_form.html', form=form, form_name="Registration",
                                       action="", msg="error message", active=active_lang)

            # todo add thread/async
            gender = {0: 'не выбран', 1: 'Женский', 2: 'Мужской'}
            birthday = form.birthday.data.strftime("%Y-%m-%d") if form.birthday.data else 'нет информации'
            google_obj.add_row([
                [form.name.data, form.surname.data, gender[form.gender.data], birthday,
                 form.telephone_number.data, form.email.data, datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
            ])

            app.logger.info(f'POST form with success')
            return render_template('success.html', active=active_lang)

    app.logger.info(f'GET form')
    return render_template('registration_form.html', form=form, form_name="Registration", action="",
                           active=active_lang)


# END DISCIPLINE ORIENTED QUERIES -----------------------------------------------------------------------------------

if __name__ == '__main__':
    app.run(debug=True)
