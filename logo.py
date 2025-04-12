import cv2

# Path to your video file on the desktop
video_path = r"c:\Users\Ammuc\OneDrive\Desktop\WhatsApp Video 2025-04-12 at 07.40.16_e6d028a8.mp4"
# Create a VideoCapture object using the path
cap = cv2.VideoCapture(video_path)

# Check if the video file opened successfully
if not cap.isOpened():
    print("Error: Could not open video.")
    exit()

# Loop to read and display video frames
while True:
    ret, frame = cap.read()
    
    if not ret:
        print("Reached end of video or failed to read the frame.")
        break

    # Show the video frame
    cv2.imshow('Video Playback', frame)

    # Press 'q' to quit
    if cv2.waitKey(25) & 0xFF == ord('q'):
        break

# Release the video capture object and close windows
cap.release()
cv2.destroyAllWindows()
