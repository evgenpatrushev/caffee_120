from flask_wtf import Form
from wtforms import StringField, SubmitField, SelectField, HiddenField, IntegerField
from datetime import date
from wtforms import validators


def get_reg_form(language):
    class RegistrationForm(Form):
        name = StringField("name: ")
        surname = StringField("surname: ")
        telephone_number = StringField("telephone number : ")
        submit = SubmitField("submit")

        def preprocessing(self):
            self.name.data = self.name.data.strip()
            self.surname.data = self.surname.data.strip()

            self.name.data = self.name.data.capitalize()
            self.surname.data = self.surname.data.capitalize()

            # self.professor_university.data = self.professor_university.data.lower()
            # self.professor_department.data = self.professor_department.data.lower()

    if language == 'укр':
        name_str = "Ім'я"
        surname_str = 'Прізвище'
        age_str = 'Вік'
        telephone_number_str = 'Номер телефона'
        submit_str = 'Відправити'

        validators_DataRequired = 'Будь ласка, введіть поле {}'
        validators_length = '{} повинно бути від {} да {} символів'
    elif language == 'рус':
        name_str = 'Имя'
        surname_str = 'Фамилия'
        age_str = 'Возраст'
        telephone_number_str = 'Номер телефона'
        submit_str = 'Отправить'

        validators_DataRequired = 'Введите обязательно поле {}'
        validators_length = '{} необходимо от {} до {} символов'
    else:
        name_str = 'Name'
        surname_str = 'Surname'
        age_str = 'Age'
        telephone_number_str = 'Telephone number'
        submit_str = 'Submit'

        validators_DataRequired = 'Required field {}'
        validators_length = '{} require from {} till {} symbols'

        # self.registration_id = HiddenField()

    setattr(RegistrationForm, 'name', StringField(f"{name_str}: ", [
        validators.InputRequired(validators_DataRequired.format(name_str)),
        validators.Length(3, 255, validators_length.format(name_str, 3, 255))
    ]))

    setattr(RegistrationForm, 'surname', StringField(f"{surname_str}: ", [
        validators.InputRequired(validators_DataRequired.format(surname_str)),
        validators.Length(3, 255, validators_length.format(surname_str, 3, 255))
    ]))

    setattr(RegistrationForm, 'age',
            SelectField(f"{age_str}: ", choices=[(0, '--')] + [(i, str(i)) for i in range(14, 101)], coerce=int,
                        default=0))

    setattr(RegistrationForm, 'telephone_number', StringField(f"{telephone_number_str} : ", [
        # todo add validation for telephone number
        validators.DataRequired(validators_DataRequired.format(telephone_number_str))
    ]))

    setattr(RegistrationForm, 'submit', SubmitField(f"{submit_str}"))

    return RegistrationForm()
