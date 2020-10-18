from PIL import Image

import generate_graph_all
print()
import send_report_email
print()
print("Everything's done!")

im = Image.open("price_report_newest.jpg")
im.show()
