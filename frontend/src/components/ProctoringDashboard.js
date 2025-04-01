import React, { useEffect, useState } from "react";
import { io } from "socket.io-client";
import "bootstrap/dist/css/bootstrap.min.css";  //  Import Bootstrap for styling

const SERVER_URL = process.env.REACT_APP_SERVER_URL || "http://localhost:5000"; //  Use environment variable for server
const socket = io(SERVER_URL);

const ProctoringDashboard = () => {
    const [alerts, setAlerts] = useState([]);
    const [logs, setLogs] = useState([]);

    //  Handle live socket alerts
    useEffect(() => {
        const handleAlert = (data) => {
            console.log("🚨 New Alert:", data);
            setAlerts((prev) => [data, ...prev]);  //  Show latest alert on top
            playAlertSound();  //  Play sound notification
        };

        socket.on("cheating_alert", handleAlert);

        return () => {
            socket.off("cheating_alert", handleAlert);
        };
    }, []);

    //  Fetch logs periodically
    useEffect(() => {
        const fetchLogs = async () => {
            try {
                const response = await fetch(`${SERVER_URL}/api/proctoring_logs`);
                if (!response.ok) {
                    throw new Error("Failed to fetch logs");
                }
                const data = await response.json();
                setLogs(data.reverse()); //  Show latest logs first
            } catch (error) {
                console.error("Error fetching logs:", error);
            }
        };

        fetchLogs();
        const interval = setInterval(fetchLogs, 5000); // Fetch logs every 5 seconds

        return () => clearInterval(interval);
    }, []);

    //  Play notification sound for new alerts
    const playAlertSound = () => {
        const audio = new Audio("/alert.mp3");  //  Ensure this file exists in `/public`
        audio.play();
    };

    return (
        <div className="container mt-4">
            <h1 className="text-center text-primary">AI Proctoring Dashboard</h1>

            {/*  Live Alerts Section */}
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

            {/*  Suspicious Activity Logs Section */}
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
