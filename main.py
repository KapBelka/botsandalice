import os
from flask import Flask, request
import logging
import json


app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

sessionStorage = {}


@app.route('/post', methods=['POST'])
def main(item='слона'):
    logging.info(f'Request: {request.json!r}')

    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }

    handle_dialog(request.json, response, item)

    logging.info(f'Response:  {response!r}')
    return json.dumps(response)


def handle_dialog(req, res, item):
    user_id = req['session']['user_id']

    if req['session']['new']:
        sessionStorage[user_id] = {
            'suggests': [
                "Не хочу.",
                "Не буду.",
                "Отстань!",
            ]
        }
        res['response']['text'] = f'Привет! Купи {item}!'
        res['response']['buttons'] = get_suggests(user_id)
        return
    user_answers = ['ладно', 'куплю', 'покупаю', 'хорошо']
    for elem in user_answers:
        if elem in req['request']['nlu']['tokens']:
            res['response']['text'] = f'{item} можно найти на Яндекс.Маркете!'
            if item == 'кролика':
                res['response']['end_session'] = True
            else:
                main('кролика')
            return
    res['response']['text'] = \
        f"Все говорят '{req['request']['original_utterance']}', а ты купи {item}!"
    res['response']['buttons'] = get_suggests(user_id)


def get_suggests(user_id, item):
    session = sessionStorage[user_id]

    suggests = [
        {'title': suggest, 'hide': True}
        for suggest in session['suggests'][:2]
    ]

    session['suggests'] = session['suggests'][1:]
    sessionStorage[user_id] = session

    if len(suggests) < 2:
        suggests.append({
            "title": "Ладно",
            "url": f"https://market.yandex.ru/search?text={item}",
            "hide": True
        })

    return suggests


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)