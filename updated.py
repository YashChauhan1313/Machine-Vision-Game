import cv2
import mediapipe as mp
import random
import pygame
import time
import tkinter as tk

# Constants
WIDTH, HEIGHT = 640, 480
OBJECT_SIZE = 30
OBJECT_SPEED = 3
NUM_OBJECTS = 5
GAME_TIME = 60

# Colors
WHITE = (255, 255, 255)
RED = (0, 0, 255)
LIME_GREEN = (0, 255, 0)  # Lime green color

# Initialize OpenCV camera capture
cap = cv2.VideoCapture(0)
cap.set(15, WIDTH)
cap.set(15, HEIGHT)

# Check if the camera is opened successfully
if not cap:
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
catcher_height = 20  # Revert the height of the paddle back to normal

# Initialize the player's score
score = 0

# Initialize game state
game_started = False

# Function to start the game
def start_game(event):
    global game_started
    game_started = True
    start_time = time.time()

root = tk.Tk()
root.title("Object Catcher Game")
start_label = tk.Label(root, text="Press 'Enter' to start the game")
start_label.pack()
root.bind("<Return>", start_game)
root.mainloop()

while True:
    if game_started:
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
            random_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            random_x = random.randint(OBJECT_SIZE // 2, WIDTH - OBJECT_SIZE // 2)
            objects.append([random_x, 0, random_color])  # Start the objects at random positions at the top

        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        results = hands.process(rgb_frame)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                for id, landmark in enumerate(hand_landmarks.landmark):
                    if id == 8:
                        catcher_x = int(landmark.x * WIDTH)

        cv2.rectangle(frame, (catcher_x - catcher_width // 2, HEIGHT - catcher_height), (catcher_x + catcher_width // 2, HEIGHT), LIME_GREEN, -1)  # Keep the lime green color for the paddle

        # Update the position of the falling objects
        new_objects = []
        for obj in objects:
            obj_x, obj_y, obj_color = obj[0], obj[1], obj[2]
            obj_y += OBJECT_SPEED  # Move the object down
            obj[1] = obj_y  # Update the y-coordinate

            cv2.circle(frame, (obj_x, obj_y), OBJECT_SIZE, obj_color, -1)

            if obj_y >= HEIGHT - 20 and catcher_x - catcher_width // 2 <= obj_x <= catcher_x + catcher_width // 2:
                score += 1
                catch_sound.play()
            else:
                new_objects.append(obj)  # Add the objects that weren't caught back to the list

        objects = new_objects  # Update the list of objects

        # Display "Score" text
        cv2.putText(frame, f"Score: {score}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, RED, 2)

        # Calculate the position to center the "Time Left" text
        text_size = cv2.getTextSize(f"Time Left: {time_left}", cv2.FONT_HERSHEY_SIMPLEX, 1, 2)[0]
        text_x = (WIDTH - text_size[0]) // 2

        # Display "Time Left" text in the center
        cv2.putText(frame, f"Time Left: {time_left}", (text_x, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, RED, 2)

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


