"""
Generate historic overview of wind strengths for a kitespot
"""
import click
import requests
import os
import traceback
import shutil
import imgkit
import enquiries
import json
import re
from wand.image import Image
from cv2 import cv2

# later used to replace multiple underscores
rx = re.compile(r'_{2,}')

def get_options(query):

    print(query)
    headers = {'Referer': 'https://www.windguru.cz/'}

    params = {
        "q":"autocomplete_ss",
        "type_info":"true",
        "all":"0",
        "latlon":"1",
        "country":"1",
        "favourite":"1",
        "custom":"1",
        "stations":"1",
        "geonames":"40",
        "spots":"1",
        "priority_sort":"1",
        "query": query,
        "_mha":"58184b7b"
    }

    r = requests.get('https://www.windguru.cz/int/iapi.php', headers=headers, params=params)

    options = json.loads(r.text)

    return [(save_filename(suggestion["value"]), suggestion["data"]) for suggestion in options["suggestions"][:10]]

def save_filename(filename):
    filename = "".join([c if c.isalpha() or c.isdigit() else '_' if c ==' ' else '' for c in filename]).rstrip()
    return rx.sub('_', filename)


def get_folder_name(spot):
    return "generated/{spot}/".format(spot=spot)


def weather(
        idu, spot_name, spot_id,
        month_from,
        day_from,
        month_to,
        day_to,
        year
):
    date_from = "{year}-{month_from}-{day_from}".format(
        year=year,
        month_from=month_from,
        day_from=day_from
    )
    date_to = "{year}-{month_to}-{day_to}".format(
        year=year,
        month_to=month_to,
        day_to=day_to
    )

    cookies = {"idu": str(idu)}
    params = {
        "date_from": date_from,
        "date_to": date_to,
        "id_spot": spot_id,
        "step": 3,
        "pwindspd": 1,
        "psmer": 1,
        "ptmp": 1,
        "id_model": 3,
        "id_stats_type": 1
    }

    r = requests.get('https://www.windguru.cz/ajax/ajax_archive.php', cookies=cookies, params=params)

    file_name = "{folder}/{spot}_{year}".format(folder=get_folder_name(spot_name), spot=spot_name, year=year)
    with open(f"{file_name}.html", 'w') as f:
        f.write('<b>{year}</b><br\>'.format(year=year))
        f.write(r.text)
    imgkit.from_file(f"{file_name}.html", f"{file_name}_original.jpg")

    with Image(filename=f"{file_name}_original.jpg") as img:
        img.crop(width=img.width - 250, height=img.height, gravity='west')
        img.save(filename=f"{file_name}_resized.jpg")

    # convert ${spot}/${spot}_${year}.jpg -gravity East -chop 250x0 ${spot}/${spot}_${year}.jpg


def recreate_directory(spot_name):
    folder_name = get_folder_name(spot_name)
    if os.path.exists(folder_name):
        # removing the file using the os.remove() method
        try:
            shutil.rmtree(folder_name)
        except OSError as e:
            print("Cloud not delete directory %s" % folder_name)
            traceback.print_exc()

    try:
        os.makedirs(folder_name)
    except OSError:
        print("Creation of the directory %s failed" % folder_name)
        traceback.print_exc()
    else:
        print("Successfully created the directory %s" % folder_name)


def delete_files(spot_name, suffixes):
    folder_name = get_folder_name(spot_name)
    files = os.listdir(folder_name)

    for file in files:
        for suffix in suffixes:
            if file.endswith(suffix):
                os.remove(os.path.join(folder_name, file))


def create_overview(spot_name):
    folder_name = get_folder_name(spot_name)
    files = sorted(os.listdir(folder_name))

    images = []

    for file in files:
        if file.endswith("_resized.jpg"):
            # for a vertical stacking it is simple: use vstack
            images.append(cv2.imread(f"{folder_name}/{file}"))
            # convert -append El_Gouna/*.jpg El_Gouna/El_Gouna_overview.jpg
    im_v = cv2.vconcat(images)

    # show the output image
    cv2.imwrite(f"{folder_name}/{spot_name}_overview.jpg", im_v)


@click.command()
@click.option('--idu', required=True,
              help='idu from Cookie of windguru.cz')
@click.option('--spots', required=True, multiple=True,
              help='Spotname and id from windguru.cz')
@click.option('--month-from', '-mf', required=True,
              help='Month from')
@click.option('--day-from', '-df', required=True,
              help='Day from')
@click.option('--month-to', '-mt', required=True,
              help='Month to')
@click.option('--day-to', '-dt', required=True,
              help='Day to')
@click.option('--years', '-y', default=[2020], required=True, multiple=True,
              help='Years to generate report(s) for')
def main(
    idu,
    spots,
    month_from,
    day_from,
    month_to,
    day_to,
    years
):

    for spot_name in spots:
        options = get_options(spot_name)

        if not options:
            print("Spot could not be found")
            return

        option_list = [key for key, value in options]

        spot_names = enquiries.choose('Choose one of these options: ', option_list, multi=True)

        for spot_name in spot_names:
            spot_id = dict(options)[spot_name]

            recreate_directory(spot_name)

            for year in years:
                print("Creating for year: {year}".format(year=year))
                weather(
                    idu,
                    spot_name,
                    spot_id,
                    month_from,
                    day_from,
                    month_to,
                    day_to,
                    year
                )
            create_overview(spot_name)
            delete_files(spot_name, [".html", "_resized.jpg", "_original.jpg"])

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
