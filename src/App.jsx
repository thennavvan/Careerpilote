import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Portfolio from "./Portfolio";
import Home from "./pages/Home";
import React from "react";
import Prep from "./pages/Prep";

function App() {
    return (
        <Router>
            <Routes>
                <Route path="/" element={<Home/>}/>
                <Route path="/user/:id" element={<Portfolio />} />
                <Route path="/user/chat" element={<Prep/>}/>
            </Routes>
        </Router>
    );
}

export default App;
