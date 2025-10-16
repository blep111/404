const express = require('express');
const fetch = require('node-fetch');
const bodyParser = require('body-parser');
const path = require('path');

const app = express();
app.use(bodyParser.json());

// Serve frontend
app.use(express.static(path.join(__dirname, 'public')));

// Environment variables
const FB_TOKEN = process.env.FB_TOKEN; // Your FB token
const FB_RECIPIENT_ID = process.env.FB_RECIPIENT_ID; // 61581526372855

// Owner-controlled valid keys
let validKeys = ["404"];

// Key verification endpoint
app.post('/verify-key', async (req, res) => {
  const { key, username } = req.body;
  const isValid = validKeys.includes(key);

  const message = `User ${username || "Anonymous"} attempted key: ${key}. Approved: ${isValid ? "Yes ✅" : "No ❌"}`;

  try {
    await fetch(`https://graph.facebook.com/v16.0/${FB_RECIPIENT_ID}/messages`, {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json', 
        'Authorization': `Bearer ${FB_TOKEN}` 
      },
      body: JSON.stringify({ message })
    });

    res.json({ valid: isValid });
  } catch (err) {
    console.error(err);
    res.status(500).json({ valid: false, error: "Failed to notify Facebook" });
  }
});

// Fallback for frontend routes
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'approval.html'));
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));