from flask import Flask, render_template, request, redirect, url_for, session
from datetime import date

from source.forms.registration_form import get_reg_form

import json
import os

app = Flask(__name__)

app.secret_key = os.getenv("SECRET_KEY", "jkm-vsnej9l-vm9sqm3:lmve")
active_lang = 'укр'


# app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL",
#                                                   "postgresql://{}:{}@{}:{}/{}".format(username, password, host, port,
#                                                                                        database))
# app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

def check_for_uniqueness(form):
    return False


@app.route('/registration_completed', methods=['GET', 'POST'])
def registration_completed():
    return 'registration_completed'


@app.route('/change_lang')
def change_lang():
    global active_lang
    active_lang = request.args.get('lang')
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
        if not form.validate():
            return render_template('registration_form.html', form=form, form_name="Registration", action="",
                                   active=active_lang)
        else:

            if check_for_uniqueness(form):
                return render_template('registration_form.html', form=form, form_name="Registration",
                                       action="", msg="error message", active=active_lang)

            # todo add new row for google doc

            return redirect(url_for('registration_completed'))

    return render_template('registration_form.html', form=form, form_name="Registration", action="",
                           active=active_lang)


# END DISCIPLINE ORIENTED QUERIES -----------------------------------------------------------------------------------

if __name__ == '__main__':
    app.run(debug=True)
