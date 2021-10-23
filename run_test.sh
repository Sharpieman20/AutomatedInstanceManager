# TODO - delete this file

mkdir defaults
rsync settings.json defaults
python3 src/python/main.py test_settings.json
rm -rf defaults
