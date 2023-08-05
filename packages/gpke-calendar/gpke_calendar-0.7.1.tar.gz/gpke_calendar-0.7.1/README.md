#GPKE Kalender

##installation
pip install gpke_calendar

##usage

import gpke_calendar

get_next_date(datetime.now(),10)

get_next_date(datetime.now(),-10)

##pypi
python setup.py sdist
twine upload dist/*
