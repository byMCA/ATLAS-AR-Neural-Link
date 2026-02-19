🕶️ Project ATLAS: Smart Glass Operating System
ATLAS transforms your computer-connected smart glasses (or any screen) into a sci-fi companion. Its purpose is to feed you the information you need quietly onto your lens without blocking your field of view while you work or explore.

🌟 What Can Your Glasses Do?
🎙️ A Voice That Talks To You
ATLAS doesn't sound like a robot; it talks like a human. When you ask a question, it responds with a smooth, natural-sounding voice


🎵 Ghost Media Player
No need to look at a monitor to listen to music. Just say the song name, and ATLAS plays it in the background. A tiny widget appears in the corner of your glass showing the track name, leaving your main vision clear.

📚 Instant Knowledge (Wikipedia)
Hear a name or a concept and want to know more? Just ask "Who is this?". ATLAS pulls the data from Wikipedia and projects a concise 2-sentence summary onto the left side of your lens like a digital sticky note.

🛰️ Live Transcription Mode
In a meeting or listening to someone speak? Say "Open Translation Mode". ATLAS listens and displays every word in real-time as subtitles at the bottom of your glass.

🛠️ How to Set It Up (Very Simple)
No complex configurations required. Just follow these 4 steps:

Install the Brain: Run the following to install the Python backend requirements:
pip install -r requirements.txt

Prepare the HUD: Go to the frontend folder and run:
npm install

Add Your Key: Enter your OpenAI API key in the configuration file inside the backend folder.

Ignition: Run the master file that starts everything at once:
python start_atlas.py

🗣️ Commands for Your Glasses
Once you put on the glasses, you can give commands like:

Volume Control: "Set volume to 30 percent."

Music: "Play Barış Manço from YouTube."

Information: "Who is Mustafa Kemal Atatürk?"

Vision: "What do you see? Analyze this."

Transcription: "Open Translation Mode."

Web: "Search for today's news on Google."

Control: "Scroll the page down a bit."

📁 File Structure
📂 backend: The "Thinking" part of the glasses. AI and logic live here.

📂 frontend: The "Visual" part of the glasses. The HUD graphics live here.

📄 start_atlas.py: The main switch that wakes up both the Brain and the HUD.
![unnamed](https://github.com/user-attachments/assets/c81d4f9a-aa87-4736-9985-c68b47e4cdae)

