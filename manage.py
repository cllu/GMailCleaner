import os


def set_env():
    for line in open('.env'):
        line = line.strip()
        if not line:
            continue

        key, value = line.split('=')
        os.environ[key] = value


if __name__ == '__main__':
    set_env()
    from app import app
    app.run(debug=True)
