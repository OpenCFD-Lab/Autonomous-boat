import cv2
import numpy as np
# 2개 이상 점수 높은거#
# Define color constants
Sky = (255, 128, 128)
White = (255, 255, 255)
find = (174, 255, 66)

min_size = 10
max_size = 150000
sample_ranges = {
    "red": [
        (np.array([0, 100, 100]), np.array([10, 255, 255])),   # 밝은 빨강
        (np.array([160, 100, 100]), np.array([180, 255, 255])) # 어두운 빨강
    ],
    "orange": [
        (np.array([10, 100, 100]), np.array([25, 255, 255]))   # 주황
    ],
    "green": [
        (np.array([40, 100, 100]), np.array([80, 255, 255]))    # 초록
    ],
    "blue": [
        (np.array([100, 100, 100]), np.array([140, 255, 255]))  # 파랑
    ],
    "black": [
        (np.array([0, 0, 0]), np.array([180, 255, 30]))          # 검정
    ],
}

# Define shape specifications
ideal_shape_condition = {
    "tri": {"vertices": 3, "angles": [60, 60, 60]},
    "rec": {"vertices": 4, "angles": [90, 90, 90, 90]},
    "cir": {"vertices": 12, "angles": [360]}
}

click_hsv_value = None
angle_file_path = '/home/opencfd/mins/Camera/cameraData.dat'


def draw_contour(frame, contour):
    cv2.drawContours(frame, [contour], -1, Sky, 3)


def set_label(frame, text, contour):
    fontface = cv2.FONT_HERSHEY_SIMPLEX
    scale = 0.5
    thickness = 1
    text_size, _ = cv2.getTextSize(text, fontface, scale, thickness)
    rect = cv2.boundingRect(contour)
    pt = (rect[0] + (rect[2] - text_size[0]) // 2, rect[1] + (rect[3] + text_size[1]) // 2)
    cv2.rectangle(frame, (pt[0], pt[1] - text_size[1]), (pt[0] + text_size[0], pt[1]), White, cv2.FILLED)
    cv2.putText(frame, text, pt, fontface, scale, (0, 0, 0), thickness, 8)


def adjustment_color_ranges(click_hsv_value):
    clicked_hue = int(click_hsv_value[0])
    clicked_saturation = int(click_hsv_value[1])
    clicked_value = int(click_hsv_value[2])

    lower_hue = clicked_hue - 10
    upper_hue = clicked_hue + 10
    lower_saturation = np.clip(clicked_saturation - 50, 0, 255)
    upper_saturation = np.clip(clicked_saturation + 50, 0, 255)
    lower_brightness = np.clip(clicked_value - 70, 0, 255)
    upper_brightness = np.clip(clicked_value + 70, 0, 255)

    if 0 <= clicked_hue <= 10 or 170 <= clicked_hue <= 180:
        if lower_hue < 0:
            return [
                (np.array([lower_hue + 180, lower_saturation, lower_brightness]),
                 np.array([180, upper_saturation, upper_brightness])),
                (np.array([0, lower_saturation, lower_brightness]),
                 np.array([upper_hue, upper_saturation, upper_brightness]))
            ]
        return [
            (np.array([lower_hue, lower_saturation, lower_brightness]),
             np.array([upper_hue, upper_saturation, upper_brightness]))
        ]

    elif 40 <= clicked_hue <= 90:
        return [
            (np.array([lower_hue, lower_saturation, lower_brightness]),
             np.array([upper_hue, upper_saturation, upper_brightness]))
        ]

    elif 100 <= clicked_hue <= 150:
        return [
            (np.array([lower_hue, lower_saturation, lower_brightness]),
             np.array([upper_hue, upper_saturation, upper_brightness]))
        ]

    return None


def on_mouse_click(event, x, y, flags, param):
    global click_hsv_value, frame
    if event == cv2.EVENT_LBUTTONDOWN:
        pixel = frame[y, x]
        click_hsv_value = cv2.cvtColor(np.uint8([[pixel]]), cv2.COLOR_BGR2HSV)[0][0]
        print(f"Clicked HSV value: {click_hsv_value}")

        updated_ranges = adjustment_color_ranges(click_hsv_value)
        if updated_ranges:
            print("Updated Color Ranges:")
            for lower, upper in updated_ranges:
                print(f"Lower: {lower}, Upper: {upper}")
        else:
            print("No color range adjustment needed.")


def calculate_shape_score(approx, target_vertices):
    # Calculate the score based on how close the number of vertices is to the target
    vertex_count = len(approx)
    score = max(0, 10 - abs(target_vertices - vertex_count))  # Example scoring system
    return score


def main():
    global frame
    cap = cv2.VideoCapture(2)
    width = 640
    height = 480
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    if not cap.isOpened():
        print("Camera could not be opened.")
        return

    wantcolor = input("Enter color (red, orange, blue, green, black): ")
    Shape = input("Enter shape (tri, rec, cir): ")
    target_vertices = ideal_shape_condition[Shape]["vertices"]

    cv2.namedWindow("Frame")
    cv2.setMouseCallback("Frame", on_mouse_click)

    # Initialize VideoWriter
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter('output.avi', fourcc, 20.0, (width, height))

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture frame.")
            break

        blurred = cv2.GaussianBlur(frame, (5, 5), 0)
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
        mask = None

        for (lower, upper) in sample_ranges.get(wantcolor, []):
            if mask is None:
                mask = cv2.inRange(hsv, lower, upper)
            else:
                mask = cv2.bitwise_or(mask, cv2.inRange(hsv, lower, upper))

        res = cv2.bitwise_and(frame, frame, mask=mask)
        gray = cv2.cvtColor(res, cv2.COLOR_BGR2GRAY)
        _, gray = cv2.threshold(gray, 40, 255, cv2.THRESH_BINARY)

        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))
        gray = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)
        gray = cv2.morphologyEx(gray, cv2.MORPH_OPEN, kernel)

        contours, _ = cv2.findContours(gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if len(contours) == 0:
            with open(angle_file_path, 'w') as f:
                f.write(f"360\tEOF")
        else:
            max_score = 0
            best_contour = None

            for contour in contours:
                if min_size < cv2.contourArea(contour) < max_size:
                    epsilon = 0.02 * cv2.arcLength(contour, True)
                    approx = cv2.approxPolyDP(contour, epsilon, True)

                    score = calculate_shape_score(approx, target_vertices)
                    if score > max_score:
                        max_score = score
                        best_contour = contour

            if best_contour is not None:
                draw_contour(frame, best_contour)
                set_label(frame, Shape.capitalize(), best_contour)
                frame_center = cv2.moments(best_contour)
                if frame_center["m00"] != 0:
                    cX = int(frame_center["m10"] / frame_center["m00"])
                    cY = int(frame_center["m01"] / frame_center["m00"])
                    cv2.circle(frame, (cX, cY), 5, White, -1)
                    distance_from_center = (cX - frame.shape[1] // 2) / (frame.shape[1] // 78)
                    angle = float(distance_from_center)
                    cv2.arrowedLine(frame, (cX, cY), (cX, cY - 30), find, 2)
                    cv2.putText(frame, f"Angle: {angle:.2f}", (cX + 10, cY), cv2.FONT_HERSHEY_SIMPLEX, 0.5, find, 2)

                    # Save angle to file
                    with open(angle_file_path, 'w') as f:
                        print(angle)
                        f.write(f"{angle:.0f}\tEOF")

        out.write(frame)
        cv2.imshow("Frame", frame)
        key = cv2.waitKey(1)
        if key == 27:  # ESC key to exit
            break

    cap.release()
    out.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()

