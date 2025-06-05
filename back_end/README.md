How to run backend app
1: run app.py
python app.py

2: install and run ngrok
✅ Step 1: Sign Up and Get Your Auth Token
Go to https://ngrok.com/

Sign up (free account is enough)

After logging in, you'll see your AuthToken like:
./ngrok config add-authtoken <your-token>

✅ Step 2: Install ngrok
🖥️ On macOS (using brew)
brew install ngrok/ngrok/ngrok
🖥️ On Ubuntu/Debian
sudo snap install ngrok
🖥️ Or Download Binary (All OS)
Go to https://ngrok.com/download

Download, unzip, and move ngrok to a location in your $PATH (e.g., /usr/local/bin)

✅ Step 3: Configure Your Auth Token
Run the command with your token:
ngrok config add-authtoken <your-ngrok-token>

✅ Step 4: Start Your Flask App Locally
Let’s say your app runs on http://127.0.0.1:5000, run:
python app.py
(Ensure your app.run() in Flask uses host='0.0.0.0' if needed)

✅ Step 5: Expose Local Port via Ngrok
Now run:
ngrok http 5000
You’ll see output like:

Forwarding http://abc123.ngrok.io -> http://localhost:5000
Use that abc123.ngrok.io link to access your local server remotely 🌍

✅ Step 6 (Optional): Run in Background or Use Config File
If you want to make it persistent:

# ~/.ngrok/ngrok.yml
authtoken: <your-token>
tunnels:
  flask:
    proto: http
    addr: 5000     # can use different port to avoid conflict

3. run ngrok
ngrok start flask

4. Every time run ngrok, the public url will change, how to change the front-end
Refer to front-end
https://travel-wardrobe.vercel.app/
