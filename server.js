const express = require("express");
const mongoose = require("mongoose");
const cors = require("cors");
const multer = require("multer");
const axios = require("axios");

const app = express();
app.use(cors());
app.use(express.json());

// MongoDB Connection
mongoose.connect("mongodb+srv://wengaboy:mypassword@firstmongoproj.5guew.mongodb.net/ResumeDatabase", {
    useNewUrlParser: true,
    useUnifiedTopology: true
});

const db = mongoose.connection;
db.on("error", console.error.bind(console, "MongoDB connection error:"));
db.once("open", () => console.log("Connected to MongoDB"));

// Multer Storage (Memory Buffer)
const upload = multer({ storage: multer.memoryStorage() });

// Upload Route
app.post("/api/upload", upload.single("file"), async (req, res) => {
    if (!req.file) return res.status(400).json({ message: "No file uploaded" });

    try {
        // Send file buffer to Python (`parser.py`)
        const response = await axios.post("http://127.0.0.1:5001/upload", req.file.buffer, {
            headers: { "Content-Type": "application/pdf" },  // Ensure proper content type
        });

        // Get User ID from Python response
        const userId = response.data.user_id;
        res.json({ message: "Resume processed successfully", user_id: userId });

    } catch (error) {
        console.error("Error parsing resume:", error);
        res.status(500).json({ message: "Error parsing resume", error: error.message });
    }
});

// Fetch User Data by ID
app.get("/api/user/:id", async (req, res) => {
    try {
        const userId = req.params.id;
        if (!mongoose.Types.ObjectId.isValid(userId)) {
            return res.status(400).json({ message: "Invalid user ID format" });
        }

        const user = await db.collection("Users").findOne({ _id: new mongoose.Types.ObjectId(userId) });
        console.log(user)
        if (!user) {
            return res.status(404).json({ message: "User not found" });
        }

        res.json(user);
    } catch (error) {
        console.error("Error fetching user data:", error);
        res.status(500).json({ message: "Server error", error: error.message });
    }
});

const PORT = 3000;
app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});
