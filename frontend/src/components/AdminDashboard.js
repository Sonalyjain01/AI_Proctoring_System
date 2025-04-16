import React, { useEffect, useState, useContext } from "react";
import { AuthContext } from "./AuthContext";
import { toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

const SERVER_URL = process.env.REACT_APP_SERVER_URL || "http://localhost:5000";

const AdminDashboard = () => {
    const { auth } = useContext(AuthContext);
    const [logs, setLogs] = useState([]);
    const [users, setUsers] = useState([]);
    const [statusMessage, setStatusMessage] = useState("");
    const [errorMessage, setErrorMessage] = useState("");

    // 🔐 Access control
    if (!auth?.token || auth.role !== "admin") {
        return <div className="text-center text-red-600 mt-10">⛔ Access Denied. Please login as Admin.</div>;
    }

    // 🔁 Fetch logs & users every 5 seconds
    useEffect(() => {
        fetchLogs();
        fetchUsers();
        const interval = setInterval(() => {
            fetchLogs();
            fetchUsers();
        }, 5000);

        return () => clearInterval(interval);
    }, []);

    const fetchLogs = async () => {
        try {
            const res = await fetch(`${SERVER_URL}/api/proctoring_logs`, {
                headers: { Authorization: `Bearer ${auth.token}` },
            });
            if (!res.ok) throw new Error("Failed to fetch logs");
            const data = await res.json();
            setLogs(data.reverse());
            setErrorMessage("");
        } catch (err) {
            console.error(err);
            setErrorMessage("Failed to load logs.");
        }
    };

    const fetchUsers = async () => {
        try {
            const res = await fetch(`${SERVER_URL}/api/users`, {
                headers: { Authorization: `Bearer ${auth.token}` },
            });
            if (!res.ok) throw new Error("Failed to fetch users");
            const data = await res.json();
            setUsers(data.users || []);
            setErrorMessage("");
        } catch (err) {
            console.error(err);
            setErrorMessage("Failed to load users.");
        }
    };

    const handleUnlockUser = async (userId) => {
        try {
            const res = await fetch(`${SERVER_URL}/api/unlock_user/${userId}`, {
                method: "POST",
                headers: { Authorization: `Bearer ${auth.token}` },
            });
            if (!res.ok) throw new Error("Failed to unlock user");

            const data = await res.json();
            setStatusMessage(data.message);
            fetchUsers();
            toast.success("✅ User unlocked!");
        } catch (err) {
            console.error(err);
            setErrorMessage("Failed to unlock user.");
            toast.error("❌ Could not unlock user.");
        }
    };

    return (
        <div className="p-6 max-w-4xl mx-auto">
            <h1 className="text-3xl font-bold mb-6 text-center text-blue-600">👮 Admin Dashboard</h1>

            {errorMessage && (
                <div className="mb-4 text-red-500 text-center">{errorMessage}</div>
            )}

            {/* 🔍 Suspicious Activity Logs */}
            <div className="mb-6">
                <h2 className="text-xl font-semibold mb-2 text-gray-800">Suspicious Activity Logs</h2>
                <div className="bg-white rounded shadow p-4 border">
                    {logs.length > 0 ? (
                        <ul className="space-y-2">
                            {logs.map((log, index) => (
                                <li key={index} className="text-sm text-gray-700">
                                    <strong>{log.event_type}</strong>: {log.details}
                                </li>
                            ))}
                        </ul>
                    ) : (
                        <p className="text-gray-500">No logs available.</p>
                    )}
                </div>
            </div>

            {/* 👥 User Management */}
            <div>
                <h2 className="text-xl font-semibold mb-2 text-gray-800">User Management</h2>
                <div className="bg-white rounded shadow p-4 border">
                    {users.length > 0 ? (
                        <ul className="divide-y">
                            {users.map((user) => (
                                <li key={user.id} className="py-2 flex justify-between items-center text-sm">
                                    <span>
                                        <span className="font-medium">{user.email}</span>{" "}
                                        -{" "}
                                        {user.is_locked ? (
                                            <span className="text-red-500">Locked</span>
                                        ) : (
                                            <span className="text-green-500">Active</span>
                                        )}
                                    </span>
                                    {user.is_locked && (
                                        <button
                                            onClick={() => handleUnlockUser(user.id)}
                                            className="bg-blue-500 hover:bg-blue-600 text-white px-3 py-1 rounded text-sm"
                                        >
                                            Unlock
                                        </button>
                                    )}
                                </li>
                            ))}
                        </ul>
                    ) : (
                        <p className="text-gray-500">No users available.</p>
                    )}
                </div>
                {statusMessage && (
                    <p className="mt-3 text-green-500 text-center">{statusMessage}</p>
                )}
            </div>
        </div>
    );
};

export default AdminDashboard;
