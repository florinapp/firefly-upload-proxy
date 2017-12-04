import json
import flask
import subprocess
import uuid
import base64


app = flask.Flask(__name__)


@app.route('/import', methods=['POST'])
def import_statement():
    user_id = flask.request.json['user_id']
    account_id = flask.request.json['account_id']
    ofx_filename = '/tmp/{}.ofx'.format(str(uuid.uuid4()))
    config_filename = '{}.json'.format(ofx_filename)

    print('user_id={}'.format(user_id))
    print('account_id={}'.format(account_id))
    print('data={}'.format(flask.request.json['data']))

    config_file_content = base64.b64encode(json.dumps({"import-account": account_id}).encode('ascii')).decode('ascii')
    subprocess.check_call('cd ~/firefly-iii && '
                          'docker-compose exec firefly-app '
                          'bash -c "echo {} | base64 -d > {}"'.format(
                              config_file_content,
                              config_filename,
                          ),
                          shell=True)
    subprocess.check_call('cd ~/firefly-iii && '
                          'docker-compose exec firefly-app '
                          'bash -c "echo {} | base64 -d > {}"'.format(
                              flask.request.json['data'],
                              ofx_filename,
                          ),
                          shell=True)
    cmd = (
        'cd ~/firefly-iii && '
        'docker-compose exec firefly-app '
        'bash -c "php artisan firefly:create-import {} {} --type=ofx --user={} --token=dabc769b178bea1b8cae4e04f24cdb6a --start"'.format(
            ofx_filename,
            config_filename,
            user_id,
        )
    )
    p = subprocess.call(cmd, shell=True)
    return str(p)


if __name__ == '__main__':
    app.run(debug=True, port=6060, host='0.0.0.0')
