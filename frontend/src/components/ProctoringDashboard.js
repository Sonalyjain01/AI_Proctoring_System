import React, { useEffect, useState } from "react";
import { io } from "socket.io-client";
import "bootstrap/dist/css/bootstrap.min.css";

const SERVER_URL = process.env.REACT_APP_SERVER_URL || "http://localhost:5000";
const socket = io(SERVER_URL);

const ProctoringDashboard = () => {
    const [alerts, setAlerts] = useState([]);
    const [logs, setLogs] = useState([]);
    const [canPlay, setCanPlay] = useState(true);

    // 📢 Play notification sound with cooldown
    const playAlertSound = () => {
        if (canPlay) {
            const audio = new Audio("/alert.mp3");
            audio.play();
            setCanPlay(false);
            setTimeout(() => setCanPlay(true), 3000); // Cooldown 3s
        }
    };

    // 🧠 Handle live WebSocket alerts
    useEffect(() => {
        const handleAlert = (data) => {
            console.log("🚨 New Alert:", data);
            setAlerts((prev) => [data, ...prev]);
            playAlertSound();
        };

        socket.on("cheating_alert", handleAlert);
        socket.on("proctoring_alert", handleAlert);

        return () => {
            socket.off("cheating_alert", handleAlert);
            socket.off("proctoring_alert", handleAlert);
        };
    }, [canPlay]);

    // 📝 Fetch logs periodically
    useEffect(() => {
        const fetchLogs = async () => {
            try {
                const response = await fetch(`${SERVER_URL}/api/proctoring_logs`);
                if (!response.ok) throw new Error("Failed to fetch logs");
                const data = await response.json();
                setLogs(data.reverse());
            } catch (error) {
                console.error("Error fetching logs:", error);
            }
        };

        fetchLogs();
        const interval = setInterval(fetchLogs, 5000);
        return () => clearInterval(interval);
    }, []);

    // 🚀 Manual trigger emitters
    const handleTrigger = (type) => {
        const payload = { user_id: "admin" };
        socket.emit(type, payload);
    };

    return (
        <div className="container mt-4">
            <h1 className="text-center text-primary">AI Proctoring Dashboard</h1>

            {/* 🔘 Manual Triggers */}
            <div className="card mt-4">
                <div className="card-header bg-secondary text-white">Manual Triggers</div>
                <div className="card-body d-flex gap-3 flex-wrap">
                    <button className="btn btn-outline-primary" onClick={() => handleTrigger("start_face_tracking")}>
                        👁️ Start Face Tracking
                    </button>
                    <button className="btn btn-outline-success" onClick={() => handleTrigger("start_voice_monitoring")}>
                        🎤 Start Voice Monitoring
                    </button>
                    <button className="btn btn-outline-danger" onClick={() => handleTrigger("start_video_recording")}>
                        🎥 Start Video Recording
                    </button>
                </div>
            </div>

            {/* 🚨 Live Alerts */}
            <div className="card mt-4">
                <div className="card-header bg-danger text-white">Live Alerts</div>
                <div className="card-body">
                    {alerts.length > 0 ? (
                        <ul className="list-group">
                            {alerts.map((alert, index) => (
                                <li key={index} className="list-group-item list-group-item-danger">
                                    🚨 {alert.event}: {alert.details}
                                </li>
                            ))}
                        </ul>
                    ) : (
                        <p className="text-muted">No live alerts</p>
                    )}
                </div>
            </div>

            {/* 📄 Proctoring Logs */}
            <div className="card mt-4">
                <div className="card-header bg-info text-white">Suspicious Activity Logs</div>
                <div className="card-body">
                    {logs.length > 0 ? (
                        <ul className="list-group">
                            {logs.map((log, index) => (
                                <li key={index} className="list-group-item">
                                    {log.event_type}: {log.details}
                                </li>
                            ))}
                        </ul>
                    ) : (
                        <p className="text-muted">No logs found</p>
                    )}
                </div>
            </div>
        </div>
    );
};

export default ProctoringDashboard;
