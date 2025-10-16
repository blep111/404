const express = require('express');
const fetch = require('node-fetch');
const bodyParser = require('body-parser');
const path = require('path');

const app = express();
app.use(bodyParser.json());

// Serve static frontend
app.use(express.static(path.join(__dirname, 'public')));

// Environment variables
const FB_TOKEN = process.env.FB_TOKEN;
const FB_RECIPIENT_ID = process.env.FB_RECIPIENT_ID;

// Owner-controlled keys
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

// Render / production fallback for frontend routing
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// Start server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));