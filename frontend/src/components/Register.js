import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

const SERVER_URL = process.env.REACT_APP_SERVER_URL || "http://localhost:5000";

const Register = () => {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [role, setRole] = useState("student");
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);

        // Validation
        if (!email || !password) {
            toast.error("Please fill in all fields.");
            setLoading(false);
            return;
        }
        if (!/\S+@\S+\.\S+/.test(email)) {
            toast.error("Invalid email format.");
            setLoading(false);
            return;
        }
        if (password.length < 6) {
            toast.error("Password must be at least 6 characters long.");
            setLoading(false);
            return;
        }

        try {
            const response = await fetch(`${SERVER_URL}/auth/register`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email, password, role }),
            });

            const data = await response.json();

            if (response.ok) {
                toast.success("🎉 Registration successful!");
                setEmail("");
                setPassword("");
                setRole("student");
                setTimeout(() => navigate("/login"), 2000);
            } else {
                toast.error(data.error || "Registration failed.");
            }
        } catch (err) {
            console.error("Registration error:", err);
            toast.error("Server error. Try again later.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex items-center justify-center min-h-screen bg-gray-100">
            <form
                onSubmit={handleSubmit}
                className="p-6 bg-white rounded-lg shadow-md w-full max-w-md"
                autoComplete="off"
            >
                <h2 className="text-2xl font-bold mb-4 text-center text-blue-600">Register</h2>

                <label className="text-sm font-medium text-gray-700">Email</label>
                <input
                    type="email"
                    placeholder="your@email.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full px-3 py-2 border rounded-md mb-3"
                    required
                    autoFocus
                />

                <label className="text-sm font-medium text-gray-700">Password</label>
                <input
                    type="password"
                    placeholder="••••••••"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full px-3 py-2 border rounded-md mb-3"
                    required
                />

                <label className="text-sm font-medium text-gray-700">Role</label>
                <select
                    value={role}
                    onChange={(e) => setRole(e.target.value)}
                    className="w-full px-3 py-2 border rounded-md mb-4"
                >
                    <option value="student">Student</option>
                    <option value="admin">Admin</option>
                </select>

                <button
                    type="submit"
                    className={`w-full py-2 rounded-md text-white flex items-center justify-center transition ${
                        loading ? "bg-blue-300" : "bg-blue-500 hover:bg-blue-600"
                    }`}
                    disabled={loading}
                >
                    {loading ? (
                        <>
                            <span className="animate-spin mr-2">🔄</span> Registering...
                        </>
                    ) : (
                        "Register"
                    )}
                </button>

                <p className="mt-4 text-center text-sm">
                    Already have an account?{" "}
                    <a href="/login" className="text-blue-500 hover:underline">
                        Login
                    </a>
                </p>
            </form>
        </div>
    );
};

export default Register;
