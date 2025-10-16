const express = require("express");
const axios = require("axios");
const path = require("path");
require("dotenv").config();

const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.urlencoded({ extended: true }));
app.use(express.json());
app.use(express.static(path.join(__dirname, "public")));

app.get("/", (req, res) => {
  res.sendFile(path.join(__dirname, "public", "index.html"));
});

app.post("/approve", (req, res) => {
  const { key } = req.body;
  if (key === process.env.APPROVAL_KEY) {
    res.redirect("/autoshare.html");
  } else {
    res.send(`
    <html><body style="background:black;color:red;text-align:center;padding-top:100px;">
      <h2>❌ Invalid Key!</h2>
      <a href="/" style="color:#00ffcc;">Try Again</a>
    </body></html>
    `);
  }
});

app.post("/share", async (req, res) => {
  const { link } = req.body;
  const token = process.env.FB_TOKEN;

  if (!token)
    return res.send(`<html><body style="background:black;color:red;text-align:center;padding-top:100px;">❌ Missing FB token in .env</body></html>`);

  try {
    const response = await axios.post(`https://graph.facebook.com/me/feed`, { link, access_token: token });

    if (response.data.id) {
      res.send(`
      <html><body style="background:black;color:#00ffcc;text-align:center;padding-top:100px;">
        <h2>✅ Shared Successfully!</h2>
        <p>Post ID: ${response.data.id}</p>
        <a href="/share.html" style="color:#00ffcc;">Share Another</a>
      </body></html>
      `);
    } else {
      res.send(`<html><body style="background:black;color:red;text-align:center;padding-top:100px;">❌ Failed to Share Post</body></html>`);
    }
  } catch (error) {
    res.send(`
    <html><body style="background:black;color:red;text-align:center;padding-top:100px;">
      ❌ Error: ${error.response?.data?.error?.message || error.message}
    </body></html>
    `);
  }
});

app.listen(PORT, () => console.log(`🚀 Server running on port ${PORT}`));