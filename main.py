import cv2
import mediapipe as mp
import random
import pygame
import time

# Constants
WIDTH, HEIGHT = 640, 480
OBJECT_SIZE = 30
OBJECT_SPEED = 3
NUM_OBJECTS = 5
GAME_TIME = 60

# Colors
WHITE = (255, 255, 255)
RED = (0, 0, 255)

# Initialize OpenCV camera capture
cap = cv2.VideoCapture(0)
cap.set(15, WIDTH)
cap.set(15, HEIGHT)

# Check if the camera is opened successfully
if not cap.isOpened():
    raise Exception("Could not open video device")

# Initialize MediaPipe Hands model
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()

# Initialize pygame mixer
pygame.mixer.init()

# Load sound effects
catch_sound = pygame.mixer.Sound('catch.wav')
miss_sound = pygame.mixer.Sound('miss.wav')
game_over_music = pygame.mixer.Sound('game_over.wav')

# Start the game timer
start_time = time.time()

# Initialize an empty list to track falling objects
objects = []

# Initialize the player's catching area
catcher_x = WIDTH // 2
catcher_width = 100

# Initialize the player's score
score = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Calculate the time left in the game
    elapsed_time = int(time.time() - start_time)
    time_left = max(0, GAME_TIME - elapsed_time)

    if time_left == 0:
        game_over_music.play()
        break

    if len(objects) < NUM_OBJECTS and random.random() < 0.05:
        objects.append([random.randint(OBJECT_SIZE // 2, WIDTH - OBJECT_SIZE // 2), 0])

    for obj in objects:
        obj[1] += OBJECT_SPEED

    for obj in objects:
        if obj[1] >= HEIGHT - 20 and catcher_x - catcher_width // 2 <= obj[0] <= catcher_x + catcher_width // 2:
            score += 1
            objects.remove(obj)
            catch_sound.play()
        elif obj[1] >= HEIGHT - 20:
            objects.remove(obj)
            miss_sound.play()

    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    results = hands.process(rgb_frame)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            for id, landmark in enumerate(hand_landmarks.landmark):
                if id == 8:
                    catcher_x = int(landmark.x * WIDTH)

    cv2.rectangle(frame, (catcher_x - catcher_width // 2, HEIGHT - 20), (catcher_x + catcher_width // 2, HEIGHT - 10), RED, -1)
    for obj in objects:
        cv2.circle(frame, (obj[0], obj[1]), OBJECT_SIZE, RED, -1)

    cv2.putText(frame, f"Score: {score}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, RED, 2)
    cv2.putText(frame, f"Time Left: {time_left}", (WIDTH - 150, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, RED, 2)

    cv2.imshow("Object Catcher", frame)

    key = cv2.waitKey(1)
    if key & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

pygame.mixer.quit()

player_name = input("Enter your name: ")
with open('leaderboard.txt', 'a') as leaderboard_file:
    leaderboard_file.write(f"{player_name}: {score}\n")

