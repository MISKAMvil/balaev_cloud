
from flask import Flask, render_template, session, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required


app = Flask(__name__)
application = app
# Импортирование конфигурации из файла config.py
app.config.from_pyfile('config.py')
# LoginManager - это класс, через который осуществляетяс настройка
# аутентификации
login_manager = LoginManager()
# Передаем менеджеру экземляр Flask (приложение),
# чтобы иметь возможность проверять учетные данные пользователей.
login_manager.init_app(app)
# Если пользователь не вошел в систему, но пытается получиь доступ
# к странице, для которой установлен декоратор login_required,
# то происходит перенаправление на endpoint указанный в login_view
# в случае остутствия login_view приложение вернет 401 ошибку
login_manager.login_view = 'login'
# Login_message и login_message_category используется flash,
# когда пользователь перенаправляется на страницу аутентификации
# Сообщение выводимое пользователю, при попытке доступа к страницам,
# требующим авторизации
login_manager.login_message = 'Для доступа к этой странице нужно авторизироваться.'
# Категория отображаемого сообщения
login_manager.login_message_category = 'warning'


# Требования Flask login к User Class
# is_authenticated - return True, если пользователь аутентифицирован
# is_active - return True, если это активный пользователь.
# помимо того, что он прошел проверку, пользователь также
# активировал свою учетную запись, не был заблокирован и т.д.
# Неактивные пользователи не могут войти в систему.
# is_anonymous - return True, если текущий пользователь
# не аутентифицирован, то есть выполняется анонимный доступ
# get_id() - этот метод возвращает уникальный идентификатор
# пользователя и может исопльзоваться для загрузки пользователя из
# обратного вызова user_loader. Идентифкатор должен иметь тип str

# Создание класса пользователь с наследованием от UserMixin,
# который предоствляет реализацию определенных методов и свойств
class User(UserMixin):
    def __init__(self, user_id, user_login):
        self.id = user_id
        self.login = user_login


# Главная страница
@app.route('/')
def index():
    return render_template('index.html')


# Используя объект request, извлекаем значения переданные в форме
# login и password и проверяем пользователя на существование в "БД"
# login_user(UserClass, remember) - обновляет данные сессии и при
# необходимости запоминает пользователя
# redirect(url) - используется для перенаправления на страницу
# с url, переданным в качестве параметра
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        remember = request.form.get('remember_me') == 'on'
        for user in get_users():
            if user['login'] == login and user['password'] == password:
                login_user(User(user['id'], user['login']), remember=remember)
                flash('Вы успешно прошли аутентификацию!', 'success')
                param_url = request.args.get('next')
                return redirect(param_url or url_for('index'))
        flash('Введён неправильный логин или пароль.', 'danger')
    return render_template('login.html')


# Используется для удаления из сессии данных о текущем пользователе
@app.route('/logout', methods=['GET'])
def logout():
    logout_user()
    return redirect(url_for('index'))


users = []

# "БД"


def get_users():
    print(users)
    return users

# @login_required - декоратор, который блокирует доступ
# не аутентифицированным пользователям к странице


@app.route('/registration', methods=["GET", "POST"])
def registration():
    if request.method == "POST":
        login = request.form['login']
        password = request.form['password']
        id = len(users) + 1
        user = {
            "id": id,
            "login": login,
            "password": password,
        }
        users.append(user)
        flash('Регистрация прошла успешно', 'success')
        return redirect(url_for('index'))
    return render_template('registration.html')


# user_loader - декоратор.
# Внутри объекта login_manager запоминается функция
# Функция позволяет по идентификатору пользователя, который
# хранится в сессии, вернуть объект соответствующий пользователю
# или если такого пользователя нет, то вернуть None
# Функция load_user используется для обработки запроса, в ходе которой
# необходимо проверить наличие пользователя
# При помощи декоратора функция записывается в login_manager и
# вызывается, при получении доступа к current_user
@login_manager.user_loader
def load_user(user_id):
    for user in get_users():
        if user['id'] == int(user_id):
            return User(user['id'], user['login'])
    return None



import requests

IAM_TOKEN = 't1.9euelZrHj5aVl56WjJSOzIuYjI_Kl-3rnpWaj5zJz5Gbio2LjYnIl5eQz5Tl9Pc3Y1JN-e8xSGnY3fT3dxFQTfnvMUhp2M3n9euelZrOzJCMyIqKmo6ampCaiZOUje_8zef1656VmpmXyIzLiY6bzMmNlpmLzMaT7_3F656Vms7MkIzIioqajpqakJqJk5SN.mhfwTHJL_29fNlng0y00-z0cffnewP7iYZ0eplf8O-0ocKZNLhq-JfaFGiXt29Df5C5944k6nkvKbf_zodO6AA'

@app.route('/translate', methods=['GET', 'POST'])
def translate():
    # target_language = 'ru'
    # texts = ["Hello", "World"]
    # body = {
    #     "targetLanguageCode": target_language,
    #     "texts": texts
    # }
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer {0}".format(IAM_TOKEN)
    }
    response = requests.post('https://translate.api.cloud.yandex.net/translate/v2/languages',
        # json=body,
        headers=headers
    )

    dict_languages = response.json()
    my_dict = {}

    for pair in dict_languages['languages']:
        values = list(pair.values())
        if len(values) == 2:
            code, name = values
            if code != name:
                my_dict[code] = name

    translated_text = ""
    input_text = ""
    input_language = ""
    if request.method == 'POST':
        input_text = request.form.get('inputText')
        input_language = request.form.get('inputLanguage')
        if input_text and input_language:
            translate_body = {
                "targetLanguageCode": input_language,
                "texts": [input_text]
            }
            translate_response = requests.post(
                'https://translate.api.cloud.yandex.net/translate/v2/translate',
                json=translate_body,
                headers=headers
            )
            translate_result = translate_response.json()
            translated_text = translate_result['translations'][0]['text']

    return render_template('translate.html', languages=my_dict, input_text=input_text, input_language=input_language, translated_text=translated_text)


# Запуск приложения при непосредственном запуске файла
if __name__ == '__main__':
    # port = int(input('Введите порт >>> '))
    # app.run(host='0.0.0.0', port=port)
    app.run(host='0.0.0.0', port=80)


@app.route('/all_users')
def all_users():
    users = get_users()
    return render_template('all_users.html', users=users)

