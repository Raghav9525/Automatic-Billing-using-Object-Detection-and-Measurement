from flask import Flask, render_template, jsonify
import threading
# dectection function for pizza apple and banana.
# from objectDetectionCount import detections

# dectection function for apple and banana only.
from appleBananaDetection1 import detections
from math import ceil

from threading import Event

app = Flask(__name__)

stop_detection_flag = Event()  # Initialize as an Event
response_dict = {}

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/start_detection", methods=["GET", "POST"])
def start_detection():
    global stop_detection_flag
    # Clear the flag to ensure the thread runs
    stop_detection_flag.clear()
    # Ensure only one detection thread runs at a time
    if not hasattr(start_detection, "thread") or not start_detection.thread.is_alive():
        start_detection.thread = threading.Thread(target=detections, args=(response_dict, stop_detection_flag))
        start_detection.thread.start()
    return render_template("start_detection.html")

@app.route("/stop_detection", methods=["GET", "POST"])
def stop_detection():
    global response_dict
    stop_detection_flag.set()  # Signal the thread to stop
    if hasattr(start_detection, "thread") and start_detection.thread.is_alive():
        start_detection.thread.join()  # Wait for the thread to finish

    productPrice = {
        "ApplePrice": 200,
        "BananaPrice": 6,
        "CarrotPrice": 50,
        "BroccoliPrice": 130,
    }

    appleMeasurementScale = 1000  # for kg measurement
    broccoliMeasurementScale = 1000  # for kg measurement
    carrotMeasurementScale = 1000  # for kg measurement
    bananaMeasurementScale = 140  # for count measurement so 1 banana weight = 200g

    bill = 0
    items_with_count = []  # Collect items with non-zero count
    detailed_bill = {}

    # collect items with non-zero count and calculate bill
    for item, weight_str in response_dict.items():
        weight = float(weight_str)
        if weight > 0:
            if item == "appleCount":
                apple_kg = weight / appleMeasurementScale
                apple_kg_formatted = f"{apple_kg:.1f}"  # Format apple_kg to one decimal place
                apple_cost = float(apple_kg_formatted) * productPrice["ApplePrice"]  # Convert to float
                apple_cost_ceil = ceil(apple_cost)  # Use ceil to round up to the nearest whole number
                bill += apple_cost_ceil
                items_with_count.append((item.replace("Count", ""), f"{apple_kg_formatted} kg"))
                detailed_bill["Apples"] = {"Weight": f"{apple_kg_formatted} kg", "Cost": f"${apple_cost_ceil}"}

            elif item == "broccoliCount":
                broccoli_kg = weight / broccoliMeasurementScale
                broccoli_kg_formatted = f"{broccoli_kg:.1f}"
                broccoli_cost = float(broccoli_kg_formatted) * productPrice["BroccoliPrice"]
                broccoli_cost_ceil = ceil(broccoli_cost)
                bill += broccoli_cost_ceil
                items_with_count.append((item.replace("Count", ""), f"{broccoli_kg_formatted} kg"))
                detailed_bill["Broccoli"] = {"Weight": f"{broccoli_kg_formatted} kg", "Cost": f"${broccoli_cost_ceil}"}

            elif item == "carrotCount":
                carrot_kg = weight / carrotMeasurementScale
                carrot_kg_formatted = f"{carrot_kg:.1f}"
                carrot_cost = float(carrot_kg_formatted) * productPrice["CarrotPrice"]
                carrot_cost_ceil = ceil(carrot_cost)
                bill += carrot_cost_ceil
                items_with_count.append((item.replace("Count", ""), f"{carrot_kg_formatted} kg"))
                detailed_bill["Carrots"] = {"Weight": f"{carrot_kg_formatted} kg", "Cost": f"${carrot_cost_ceil}"}


            elif item == "bananaCount":
                    # Assuming weight is the total weight of bananas and each banana weighs `bananaMeasurementScale` grams
                banana_count = int(weight / bananaMeasurementScale)
                banana_cost = banana_count * productPrice["BananaPrice"]
                bill += banana_cost
                items_with_count.append((item.replace("Count", ""), f"{banana_count:.0f} count"))
                detailed_bill["Bananas"] = {"Count": f"{banana_count:.0f}", "Cost": f"${banana_cost:.2f}"}

    total_response = {
        "Items": detailed_bill,
        "TotalBill": f"${bill:.2f}",
        "Details": items_with_count,
    }
    print(total_response)

    return render_template("bill_generate.html", Items=total_response["Items"], TotalBill=total_response["TotalBill"])


if __name__ == "__main__":
    app.run(debug=True)
