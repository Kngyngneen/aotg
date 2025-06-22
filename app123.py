import zipfile
import os
import shutil  
import zipfile
import os
import shutil

# Define paths
project_root = "/mnt/data/StoryMagic_Final"
backend_path = os.path.join(project_root, "backend")
frontend_path = os.path.join(project_root, "frontend")

# Create backend and frontend folders
os.makedirs(backend_path, exist_ok=True)
os.makedirs(frontend_path, exist_ok=True)

# --- Backend Files ---
# requirements.txt
with open(os.path.join(backend_path, "requirements.txt"), "w") as f:
    f.write("""fastapi
uvicorn
openai
gtts
moviepy
requests
python-multipart
""")

# render.yaml
with open(os.path.join(backend_path, "render.yaml"), "w") as f:
    f.write("""services:
  - type: web
    name: storymagic-backend
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn main:app --host 0.0.0.0 --port 10000
    envVars:
      - key: OPENAI_API_KEY
        sync: false
""")

# --- Frontend Files ---
# firebase.js
firebase_js = """import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";
import { getFirestore } from "firebase/firestore";

const firebaseConfig = {
  apiKey: "YOUR_API_KEY",
  authDomain: "yourapp.firebaseapp.com",
  projectId: "yourapp",
  storageBucket: "yourapp.appspot.com",
  messagingSenderId: "SENDER_ID",
  appId: "APP_ID"
};

const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
export const db = getFirestore(app);
"""
with open(os.path.join(frontend_path, "firebase.js"), "w") as f:
    f.write(firebase_js)

# App.js
app_js = """import React, { useState, useEffect } from 'react';
import { View, Text, TextInput, Button, ScrollView, Image, ActivityIndicator } from 'react-native';
import { Audio } from 'expo-av';
import { auth, db } from './firebase';
import { doc, setDoc } from 'firebase/firestore';

export default function App() {
  const [prompt, setPrompt] = useState('');
  const [story, setStory] = useState('');
  const [images, setImages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [sound, setSound] = useState();

  const BACKEND_URL = "http://localhost:8000"; // change for production

  const generateStory = async () => {
    setLoading(true);
    const res = await fetch(`${BACKEND_URL}/api/story`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt })
    });
    const data = await res.json();
    setStory(data.story);
    setImages(data.images || []);
    setLoading(false);
  };

  const narrateStory = async () => {
    const res = await fetch(`${BACKEND_URL}/api/narrate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ story_text: story })
    });
    const data = await res.json();
    const { audio_url } = data;

    const { sound } = await Audio.Sound.createAsync({
      uri: `${BACKEND_URL}${audio_url}`,
    });
    setSound(sound);
    await sound.playAsync();
  };

  const saveStory = async () => {
    const uid = auth.currentUser?.uid;
    if (!uid) return;
    const docRef = doc(db, "users", uid, "stories", Date.now().toString());
    await setDoc(docRef, {
      prompt,
      story,
      images
    });
  };

  useEffect(() => {
    return sound ? () => sound.unloadAsync() : undefined;
  }, [sound]);

  return (
    <ScrollView style={{ padding: 20 }}>
      <TextInput
        placeholder="Enter your story idea..."
        value={prompt}
        onChangeText={setPrompt}
        style={{ marginBottom: 20, fontSize: 18, borderBottomWidth: 1 }}
      />
      <Button title="Generate Story" onPress={generateStory} />
      {loading && <ActivityIndicator size="large" style={{ marginTop: 20 }} />}
      {!loading && story && (
        <>
          <Text style={{ marginVertical: 20 }}>{story}</Text>
          {images.map((img, i) => (
            <Image
              key={i}
              source={{ uri: img }}
              style={{ width: '100%', height: 200, marginBottom: 10 }}
            />
          ))}
          <Button title="Play Narration" onPress={narrateStory} />
          <Button title="Save Story" onPress={saveStory} />
        </>
      )}
    </ScrollView>
  );
}
"""
with open(os.path.join(frontend_path, "App.js"), "w") as f:
    f.write(app_js)


# Create export folder and generate zip
final_zip = "/mnt/data/StoryMagic_GitHub_Ready.zip"
with zipfile.ZipFile(final_zip, 'w') as zipf:
    for root, _, files in os.walk(project_root):
        for file in files:
            path = os.path.join(root, file)
            zipf.write(path, os.path.relpath(path, project_root))

print(final_zip)

