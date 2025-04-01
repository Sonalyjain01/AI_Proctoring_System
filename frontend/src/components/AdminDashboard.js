import React, { useEffect, useState, useContext } from "react";
import { AuthContext } from "./AuthContext";
import { toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

const SERVER_URL = process.env.REACT_APP_SERVER_URL || "http://localhost:5000";

const AdminDashboard = () => {
    const { auth } = useContext(AuthContext);

    // State hooks
    const [logs, setLogs] = useState([]);
    const [users, setUsers] = useState([]);
    const [statusMessage, setStatusMessage] = useState("");
    const [errorMessage, setErrorMessage] = useState("");

    // Redirect or deny access if not authenticated
    if (!auth || !auth.token) {
        return <div className="text-center text-red-500">Please login as Admin</div>;
    }

    // Fetch logs and users when component loads and every 5 seconds
    useEffect(() => {
        fetchLogs();
        fetchUsers();

        const interval = setInterval(() => {
            fetchLogs();
            fetchUsers();
        }, 5000);

        return () => clearInterval(interval);
    }, []);

    // Fetch logs from Flask backend
    const fetchLogs = async () => {
        try {
            const response = await fetch(`${SERVER_URL}/api/proctoring_logs`, {
                headers: {
                    Authorization: `Bearer ${auth.token}`,
                },
            });
            if (!response.ok) throw new Error(`Failed to fetch logs`);
            const data = await response.json();
            setLogs(data.reverse()); //  Show latest logs first
            setErrorMessage(""); // Clear previous errors
        } catch (error) {
            console.error("Error fetching logs:", error);
            setErrorMessage("Failed to load logs.");
        }
    };

    // Fetch users from Flask backend
    const fetchUsers = async () => {
        try {
            const response = await fetch(`${SERVER_URL}/api/users`, {
                headers: {
                    Authorization: `Bearer ${auth.token}`,
                },
            });
            if (!response.ok) throw new Error(`Failed to fetch users`);
            const data = await response.json();
            setUsers(data);
            setErrorMessage(""); // Clear previous errors
        } catch (error) {
            console.error("Error fetching users:", error);
            setErrorMessage("Failed to load users.");
        }
    };

    // Handle user unlock action
    const handleUnlockUser = async (userId) => {
        try {
            const response = await fetch(`${SERVER_URL}/api/unlock_user/${userId}`, {
                method: "POST",
                headers: {
                    Authorization: `Bearer ${auth.token}`,
                },
            });
            if (!response.ok) throw new Error(`Failed to unlock user`);

            const data = await response.json();
            setStatusMessage(data.message);
            fetchUsers(); // Refresh user list after unlocking
            toast.success("User unlocked successfully!"); //  Show success message
        } catch (error) {
            console.error("Error unlocking user:", error);
            setErrorMessage("Failed to unlock user.");
            toast.error("Failed to unlock user!"); //  Show error message
        }
    };

    return (
        <div className="p-6">
            <h1 className="text-3xl font-bold mb-6 text-center text-blue-600">Admin Dashboard</h1>

            {/*  Error Message */}
            {errorMessage && (
                <p className="mb-4 text-red-500 text-center">{errorMessage}</p>
            )}

            {/* Suspicious Activity Logs */}
            <div className="mb-6">
                <h2 className="text-xl font-semibold mb-3 text-gray-700">Suspicious Activity Logs</h2>
                <div className="border rounded p-3 bg-white shadow-md">
                    {logs.length > 0 ? (
                        <ul className="list-disc pl-4">
                            {logs.map((log, index) => (
                                <li key={index} className="text-gray-800">
                                    <strong>{log.event_type}</strong> - {log.details}
                                </li>
                            ))}
                        </ul>
                    ) : (
                        <p className="text-gray-500">No logs available</p>
                    )}
                </div>
            </div>

            {/*  User Management */}
            <div>
                <h2 className="text-xl font-semibold mb-3 text-gray-700">User Management</h2>
                <div className="border rounded p-3 bg-white shadow-md">
                    {users.length > 0 ? (
                        <ul className="list-none">
                            {users.map((user) => (
                                <li key={user.id} className="flex justify-between items-center border-b py-2">
                                    <span>
                                        {user.email} -{" "}
                                        {user.is_locked ? (
                                            <span className="text-red-500">Locked</span>
                                        ) : (
                                            <span className="text-green-500">Active</span>
                                        )}
                                    </span>
                                    {user.is_locked && (
                                        <button
                                            className="bg-blue-500 text-white px-3 py-1 rounded"
                                            onClick={() => handleUnlockUser(user.id)}
                                        >
                                            Unlock
                                        </button>
                                    )}
                                </li>
                            ))}
                        </ul>
                    ) : (
                        <p className="text-gray-500">No users available</p>
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
