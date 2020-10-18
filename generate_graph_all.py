from PIL import Image, ImageDraw, ImageFont
from datetime import date
import math
from matplotlib import pyplot as plt
import matplotlib
import requests
import time
from bs4 import BeautifulSoup
from urllib.parse import quote
import random
import time
import os

header = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36"}

item_images_path = "assets/hero_img/"

# get all tracked links
with open("tracked_links.txt", 'r') as file:
    tracked_links = file.read().split("\n")

print("All Items:")
for i in tracked_links:
    print(i)


def timeStamp(timecode):
    # convert time code to normal date
    timeStamp = float(timecode / 1000)
    timeArray = time.localtime(timeStamp)
    real_date = time.strftime("%m.%d", timeArray)
    return real_date


def getPriceHistory(shop_link):
    time.sleep(1.5)
    # get price history html
    history_html = requests.get("http://p.zwjhl.com/price.aspx?url=" + quote(store_link), headers=header)
    history_html = history_html.text

    soup = BeautifulSoup(history_html, 'html.parser')
    title = soup.find('title').text
    title = title.strip()

    if "\n" in title:
        title = title.split("\n")[1]

    print()
    print("Checking Item:")
    print(title)

    for line in history_html.split("\n"):
        if "flotChart.chartNow" in line:
            # picking out price history
            history_price_list = line.split("flotChart.chartNow(")[1].split("'")[1]
            break

    time_list = []
    price_list = []

    for daily_price in history_price_list.split("["):
        if daily_price != "":
            daily_price = daily_price.split(",")
            date = daily_price[0]
            date = timeStamp(int(date))
            price = daily_price[1]
            time_list.append(date)
            price_list.append(price)

    if time_list[-1] == time_list[-2]:
        time_list = time_list[:-1]
        price_list[-2] = price_list[-1]
        price_list = price_list[:-1]

    if price_list[-1] < price_list[-2]:
        print("Yay! Price Dropped!!!")
    else:
        print("No Price Drop!")

    # only return the latest data
    return [title, time_list[-15:], price_list[-15:]]


def getHeroImage(shop_link):
    # download product image
    print("Getting Image...")
    image_name = shop_link.split(".com/")[1].split(".html")[0]

    time.sleep(1)
    shop_html = requests.get(shop_link, headers=header)
    shop_html = shop_html.text

    soup = BeautifulSoup(shop_html, 'html.parser')

    image_element = soup.findAll("div", {"id": "spec-n1"})
    img_link = image_element[0].img.get('data-origin')
    image_link = requests.get("http:" + img_link)

    # save product image
    file = open(item_images_path + image_name + ".jpg", "wb")
    file.write(image_link.content)
    file.close()
    print("Item image Saved.")


# Checking items one at a time
tracked_items = []
time_sequence = []
price_sequence = []
for i in tracked_links:
    store_link = i
    current_id = store_link.split(".com/")[1].split(".html")[0]

    if not os.path.exists(item_images_path + current_id + ".jpg"):
        # item image doesn't exists
        getHeroImage(store_link)

    current_name, current_time_sequence, current_price_sequence = getPriceHistory(store_link)

    # limit the item name length
    current_name = current_name[:25] + "..."

    if float(current_price_sequence[-1]) < float(current_price_sequence[-2]):
        price_diff = float(current_price_sequence[-2]) - float(current_price_sequence[-1])
        tracked_items.append([current_name, float(current_price_sequence[-1]), True, current_id + ".jpg", price_diff])

        # if price dropped, keep history price
        price_sequence.append(current_price_sequence)
        time_sequence.append(current_time_sequence)
    else:
        tracked_items.append([current_name, float(current_price_sequence[-1]), False, current_id + ".jpg"])


# Draw Report Start
header_area = 170
price_drop_detail = 440
dropped_not_dropped_trans = 110
bottom_logo_area = 170

left_margin = 67

dropped_list = []
not_dropped_list = []
price_dropped = False

for i in tracked_items:
    if i[2]:
        price_dropped = True
        dropped_list.append(i)
    else:
        not_dropped_list.append(i)

# print(dropped_list)
# print(not_dropped_list)

# loading fonts & images
bold_font = "Fonts/Alibaba-PuHuiTi-Bold.ttf"
heavy_font = "Fonts/Alibaba-PuHuiTi-Heavy.ttf"
regular_font = "Fonts/Alibaba-PuHuiTi-Regular.ttf"

logo_image = Image.open('assets/logo.jpg')
nothing_changed_image = Image.open('assets/nothing_changed.jpg')
price_dropped_image = Image.open('assets/PriceDropped.jpg')
not_changed_transition = Image.open('assets/PriceDropped_not_changed.jpg')


def drawCanvas():
    global date, tracked_items, canvas, canvas_height

    # get date
    today = date.today()
    date = today.strftime("%d/%m/%Y")
    # make the date text spacing bigger
    date = " ".join(date)

    if len(not_dropped_list) != 0:
        not_changed_rows_count = math.ceil(len(not_dropped_list) / 5)
    else:
        not_changed_rows_count = 1
    not_changed_area = 200 * not_changed_rows_count + (not_changed_rows_count - 1) * 20

    if price_dropped:
        canvas_height = header_area + price_drop_detail * len(
            dropped_list) + dropped_not_dropped_trans + not_changed_area + bottom_logo_area
    else:
        canvas_height = header_area + not_changed_area + bottom_logo_area

    margin = 68
    item_image_size = 130
    item_image_spacing = 30
    if price_dropped:
        item_image_y_axis = len(dropped_list) * price_drop_detail + dropped_not_dropped_trans + 170
        not_changed_transition_location = header_area + price_drop_detail * len(dropped_list)
    else:
        item_image_y_axis = 190

    canvas_size = (1000, canvas_height)

    date_location = (canvas_size[0] - 340, canvas_size[1] - 98)
    logo_location = (0, canvas_size[1] - 150)

    canvas = Image.new('RGB', canvas_size, (255, 255, 255))  # create white canvas
    draw = ImageDraw.Draw(canvas)

    item_name_location = (20, canvas_size[1] - 50)
    if price_dropped:
        canvas.paste(price_dropped_image, (0, 0))
    else:
        canvas.paste(nothing_changed_image, (0, 0))

    date_font = ImageFont.truetype(bold_font, 34)
    price_tag_font = ImageFont.truetype(regular_font, 23)
    draw.text(date_location, date, font=date_font, fill="black")

    canvas.paste(logo_image, logo_location)

    if price_dropped:
        canvas.paste(not_changed_transition, (0, not_changed_transition_location))

    counter = 0
    for i in not_dropped_list:
        item_img = Image.open('assets/hero_img/' + i[3])
        item_img = item_img.resize((item_image_size, item_image_size))
        if math.floor(len(not_dropped_list) / 5) == 0:
            location_x = margin + counter * (item_image_size + item_image_spacing)
            location_y = item_image_y_axis
        else:
            if counter + 1 < 5:
                location_x = margin + counter * (item_image_size + item_image_spacing)
                location_y = item_image_y_axis
            else:
                location_x = margin + (counter % 5) * (item_image_size + item_image_spacing)
                location_y = item_image_y_axis + math.floor(counter / 5) * (item_image_size + 40 + item_image_spacing)

        current_location = (location_x, location_y)
        canvas.paste(item_img, current_location)

        # price tag
        draw.text((location_x, location_y + item_image_size + 10), "￥" + str(round(i[1], 2)), font=price_tag_font,
                  fill="black")
        counter += 1


def generateLineGraph(dev_x, dev_y, section):
    # visualise price history if price dropped
    temp_graph = "temp_graph.jpg"

    load_days = 10

    dev_y = dev_y[load_days * -1:]
    dev_x = dev_x[load_days * -1:]

    annotations = []

    counter = 0
    for i in dev_y:
        dev_y[counter] = float(i)
        dev_x[counter] = dev_x[counter].split(".")[-1]
        annotations.append([counter, float(i)])
        counter += 1

    upper_gap = 50
    y_range = [min(dev_y) - upper_gap, max(dev_y) + upper_gap]

    font = {'weight': 'normal', 'size': 15}
    matplotlib.rc('font', **font)

    fig, ax = plt.subplots(figsize=(7, 2.4), dpi=80)

    plt.gca().axes.get_yaxis().set_visible(False)

    plt.grid(color='#D3D3D3', which='major', axis='x', linestyle='solid')
    plt.box(on=None)

    plt.plot(dev_x, dev_y, color="black", mfc="red", mec="red", linestyle="solid", marker=".", markersize=25,
             linewidth=5)
    plt.ylim(y_range)

    # adding data labels
    for x, y in zip(dev_x, dev_y):
        label = int(y)
        plt.annotate(label, (x, y), color="#505050", textcoords="offset points", xytext=(0, 10), ha='center')

    plt.savefig(temp_graph)
    im = Image.open(temp_graph)  # load line graph

    width, height = im.size
    side_crop = 40
    im = im.crop((side_crop, 0, width - side_crop, height))  # crop image

    canvas.paste(im, (410, header_area + 150 + price_drop_detail * section))

    # canvas.show()
    # canvas.save("test_canvas_with_graph.jpg")


def drawPriceDrop():
    global canvas
    # canvas = Image.open("test_canvas_with_graph.jpg")
    draw = ImageDraw.Draw(canvas)

    counter = 0
    for i in dropped_list:
        current_img = Image.open('assets/hero_img/' + i[3])  # load image
        current_img = current_img.resize((350, 350))
        canvas.paste(current_img, (left_margin, header_area + 10 + price_drop_detail * counter))

        current_price = "{:0.2f}".format(i[1])  # load price
        big_price_font = ImageFont.truetype(heavy_font, 95)
        draw.text((455, header_area + 20 + price_drop_detail * counter), str(current_price), font=big_price_font, fill="red")

        current_item_name = i[0]  # load item name
        item_font = ImageFont.truetype(regular_font, 25)
        draw.text((left_margin, header_area + 385 + price_drop_detail * counter), current_item_name, font=item_font, fill="black")

        change_amount = "{:0.2f}".format(i[4])  # laod dropped price
        price_drop_font = ImageFont.truetype(heavy_font, 35)
        draw.text((left_margin + 680, header_area + 380 + price_drop_detail * counter), "↓" + str(change_amount), font=price_drop_font, fill="red")

        if len(dropped_list) > 1:
            if counter != len(dropped_list) - 1:
                # draw a devider
                shape = [(left_margin, header_area + 435 + price_drop_detail * counter),
                         (1000 - left_margin - 50, header_area + 435 + price_drop_detail * counter)]
                img1 = ImageDraw.Draw(canvas)
                img1.line(shape, fill="black", width=1)

        counter += 1


def drawNothingHere():
    global canvas, canvas_height
    # if everything's on sale
    im = Image.open("assets/nothing_here.jpg")
    canvas.paste(im, (0, canvas_height - 350))


drawCanvas()

if price_dropped:
    for i in range(len(price_sequence)):
        generateLineGraph(time_sequence[i], price_sequence[i], i)
    drawPriceDrop()

if len(not_dropped_list) == 0:
    drawNothingHere()

if os.path.exists("temp_graph.jpg"):
    os.remove("temp_graph.jpg")

# Saving a log for the email program to see
if price_dropped:
    log = "T," + str(len(dropped_list))
else:
    log = "F"

with open("log.txt", "w") as text_file:
    text_file.write(log)

# canvas.show()
canvas.save("price_report_newest.jpg")
