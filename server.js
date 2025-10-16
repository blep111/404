// server.js
const express = require('express');
const fetch = require('node-fetch'); // npm i node-fetch
const bodyParser = require('body-parser');
require('dotenv').config(); // for environment variables

const app = express();
app.use(bodyParser.json());

// Environment variables (set these in Render, Railway, or Replit)
const FB_TOKEN = process.env.FB_TOKEN; // your FB token
const FB_RECIPIENT_ID = process.env.FB_RECIPIENT_ID; // 61581526372855
let validKeys = ["404"]; // owner controlled keys

// Endpoint to verify key
app.post('/verify-key', async (req, res) => {
  const { key, username } = req.body;
  const isValid = validKeys.includes(key);

  // Create the message
  const message = `User ${username || "Anonymous"} attempted key: ${key}. Approved: ${isValid ? "Yes ✅" : "No ❌"}`;

  try {
    // Send Messenger message to your account
    await fetch(`https://graph.facebook.com/v16.0/${FB_RECIPIENT_ID}/messages`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${FB_TOKEN}` },
      body: JSON.stringify({ message })
    });

    res.json({ valid: isValid });
  } catch (err) {
    console.error(err);
    res.status(500).json({ valid: false, error: "Failed to notify Facebook" });
  }
});

app.listen(3000, () => console.log("Backend running on port 3000"));