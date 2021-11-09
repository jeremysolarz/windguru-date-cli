"""
Generate historic overview of wind strengths for a kitespot
"""
import click
import requests
import os
import traceback
import shutil
import imgkit
from wand.image import Image
from wand.display import display

## please set spots & spot_ids here manually
## e.g.:

month_day_from="05-01"
month_day_to="05-30"


def weather(idu, spot_name, spot_id, year):
    date_from="{year}-{month_day_from}".format(year=year, month_day_from=month_day_from)
    date_to="{year}-{month_day_to}".format(year=year, month_day_to=month_day_to)

    print(idu, spot_name, spot_id, date_from, date_to)

    cookies = {"idu": str(idu)}
    params={
        "date_from": date_from,
        "date_to": date_to,
        "id_spot": spot_id,
        "step": 3,
        "pwindspd":1,
        "psmer": 1,
        "ptmp": 1,
        "id_model": 3,
        "id_stats_type":1
    }

    r = requests.get('https://www.windguru.cz/ajax/ajax_archive.php', cookies=cookies, params=params)

    file_name = "{spot}/{spot}_{year}".format(spot=spot_name, year=year)
    with open(f"{file_name}.html", 'w') as f:
        f.write('<b>{year}</b><br\>'.format(year=year))
        f.write(r.text)
    imgkit.from_file(f"{file_name}.html", f"{file_name}.jpg")

    with Image(filename=f"{file_name}.jpg") as img:
    # convert ${spot}/${spot}_${year}.jpg -gravity East -chop 250x0 ${spot}/${spot}_${year}.jpg

def recreate_directory(spot_name):
    if os.path.exists(spot_name):
        # removing the file using the os.remove() method
        try:
            shutil.rmtree(spot_name)
        except OSError as e:
            print("Cloud not delete dirctory %s" % spot_name)
            traceback.print_exc()

    try:
        os.makedirs(spot_name)
    except OSError:
        print ("Creation of the directory %s failed" % spot_name)
        traceback.print_exc()
    else:
        print ("Successfully created the directory %s" % spot_name)

def delete_htmls(spot_name):
    files = os.listdir(spot_name)

    for file in files:
        if file.endswith(".html"):
            os.remove(os.path.join(spot_name, file))

def create_overview(spot_name):
    delete_htmls(spot_name)
    # convert -append El_Gouna/*.jpg El_Gouna/El_Gouna_overview.jpg

@click.command()
@click.option('--idu', default=1505322, required=True,
              help='idu from Cookie of windguru.cz')
@click.option('--spots', type=(str, int), default=[("DK_Kloster", 500768)], required=True, multiple=True,
              help='Spotname and id from windguru.cz')
@click.option('--years', default=[2020, 2019, 2018, 2017, 2016, 2015, 2014], required=True, multiple=True,
              help='Years to generate report(s) for')
def main(idu, spots, years):
    for spot in spots:
        spot_name, spot_id = spot
        recreate_directory(spot_name)

        for year in years:
            print("Creating for year: {year}".format(year=year))
            weather(idu, spot_name, spot_id, year)

        create_overview(spot_name)

if __name__ == '__main__':
    main()

# import os
#
# from flask import Flask, render_template
#
# # pylint: disable=C0103
# app = Flask(__name__)
#
#
# @app.route('/')
# def hello():
#     """Return a friendly HTTP greeting."""
#     message = "It's running!"
#
#     """Get Cloud Run environment variables."""
#     service = os.environ.get('K_SERVICE', 'Unknown service')
#     revision = os.environ.get('K_REVISION', 'Unknown revision')
#
#     return render_template('index.html',
#         message=message,
#         Service=service,
#         Revision=revision)
#
# if __name__ == '__main__':
#     server_port = os.environ.get('PORT', '8080')
#     app.run(debug=False, port=server_port, host='0.0.0.0')
