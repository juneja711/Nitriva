# 🚀 Nitriva Deployment Guide

Deploy **Nitriva** to the cloud so anyone can access it over the public internet with a live URL (e.g., `https://nitriva.onrender.com`), with real-time browser eye tracking, gesture communication, and smart device control.

---

## 🌟 Method 1: Deploy on Render.com (Recommended - Free Tier)

Render provides free hosting with automatic HTTPS, persistent WebSockets, and Python/Docker support.

### Step 1: Push your project to GitHub

1. Open PowerShell or Terminal in your project folder:
   ```bash
   cd "C:\Users\vijit juneja\.gemini\antigravity\scratch\nitriva"
   ```

2. Initialize Git and commit all files:
   ```bash
   git init
   git add .
   git commit -m "Deploy Nitriva Assistive ML System"
   ```

3. Create a new repository on [GitHub](https://github.com/new) named `nitriva`.

4. Link and push to your GitHub repo:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/nitriva.git
   git branch -M main
   git push -u origin main
   ```

---

### Step 2: Deploy on Render

1. Go to [Render.com](https://render.com) and sign in (or sign up with GitHub).
2. Click **New +** $\rightarrow$ **Web Service**.
3. Select **Build and deploy from a Git repository** $\rightarrow$ Connect your `nitriva` repository.
4. Fill in the service details:
   - **Name**: `nitriva`
   - **Region**: Choose the closest region to you (e.g., Frankfurt, Oregon, Singapore)
   - **Runtime**: **Docker** (or **Python 3**)
     - *If choosing Docker*: Render will automatically use the included `Dockerfile`.
     - *If choosing Python*:
       - **Build Command**: `pip install -r requirements.txt`
       - **Start Command**: `uvicorn src.server:app --host 0.0.0.0 --port $PORT`
   - **Instance Type**: **Free**
5. Click **Create Web Service**.
6. Render will build the container and provide your live public URL:
   ```text
   https://nitriva.onrender.com
   ```

---

## 🤗 Method 2: Deploy on Hugging Face Spaces (100% Free ML Hosting)

Hugging Face Spaces is designed specifically for ML models and provides generous free CPU tiers with free SSL.

1. Go to [Hugging Face Spaces](https://huggingface.co/spaces) and click **Create new Space**.
2. Set Space Name: `nitriva`
3. License: `MIT`
4. Space SDK: **Docker** $\rightarrow$ **Blank**
5. Space Hardware: **Free CPU (2 vCPU, 16 GB RAM)**
6. Clone the space repository locally or push your existing files:
   ```bash
   git remote add hf https://huggingface.co/spaces/YOUR_USERNAME/nitriva
   git push hf main
   ```
7. Hugging Face will automatically build the `Dockerfile` and launch your live app!

---

## ⚡ Method 3: Deploy on Railway.app

1. Go to [Railway.app](https://railway.app) and log in with GitHub.
2. Click **New Project** $\rightarrow$ **Deploy from GitHub repo**.
3. Select `nitriva`.
4. Railway will automatically detect the `Dockerfile` and deploy.
5. In your service settings $\rightarrow$ **Networking**, click **Generate Domain** to get your public HTTPS URL.

---

## 🌐 Method 4: Deploy Static Frontend on Vercel

If you want static frontend hosting on Vercel similar to `nayan-vaani.vercel.app`:

1. Install the Vercel CLI:
   ```bash
   npm install -g vercel
   ```
2. In the `nitriva` directory, run:
   ```bash
   vercel
   ```
3. Follow the prompts. Vercel will deploy the static app using the included `vercel.json`.

---

## 📱 Accessing on Local Network (LAN / Phone / Tablet)

To test on another device (such as an iPad, phone, or another laptop on your Wi-Fi):

1. Find your computer's local IP address:
   ```powershell
   ipconfig
   ```
   (Look for *IPv4 Address*, e.g., `192.168.1.15`).

2. Start Nitriva:
   ```powershell
   python run.py
   ```

3. On your phone/tablet connected to the same Wi-Fi, open:
   ```text
   http://192.168.1.15:8000
   ```

---

## 🛡️ Camera Privacy & Permissions

- When visiting the deployed URL over HTTPS, the browser will ask for camera permission:
  Click **Allow** so the client webcam can track eye gaze and detect left-eye winks in real time.
- Nitriva processes camera frames in-memory without saving or storing any patient video or photos.
