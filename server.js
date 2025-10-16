const express = require('express');
const fetch = require('node-fetch');
const bodyParser = require('body-parser');
const path = require('path');
require('dotenv').config();

const app = express();
app.use(bodyParser.json());
app.use(express.static(path.join(__dirname, 'public')));

const FB_TOKEN = process.env.FB_TOKEN;
const FB_RECIPIENT_ID = process.env.FB_RECIPIENT_ID;
const validKeys = ["404"]; // Owner can change key anytime

// 🔑 Verify key and notify owner via Facebook
app.post('/verify-key', async (req, res) => {
  const { key, username } = req.body;
  const isValid = validKeys.includes(key);

  const message = `Key attempt: ${key} | User: ${username || "Unknown"} | Approved: ${isValid ? "✅ Yes" : "❌ No"}`;
  try {
    await fetch(`https://graph.facebook.com/${FB_RECIPIENT_ID}/feed`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message,
        access_token: FB_TOKEN
      })
    });
  } catch (err) {
    console.error('Facebook notification failed:', err.message);
  }

  res.json({ valid: isValid });
});

// 📤 AutoShare endpoint (server handles external API)
app.post('/autoshare', async (req, res) => {
  const { cookie, link, limit } = req.body;

  if (!cookie || !link) {
    return res.status(400).json({ error: "Missing required fields" });
  }

  try {
    const apiUrl = `https://vern-rest-api.vercel.app/api/autoshare?cookie=${encodeURIComponent(cookie)}&link=${encodeURIComponent(link)}${limit ? `&limit=${limit}` : ''}`;
    const response = await fetch(apiUrl);
    const result = await response.json();
    res.json(result);
  } catch (error) {
    console.error("AutoShare API Error:", error.message);
    res.status(500).json({ error: "Failed to share post" });
  }
});

// Default page
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'approval.html'));
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`✅ Server running on port ${PORT}`));