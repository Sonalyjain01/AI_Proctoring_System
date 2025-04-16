import React, { useState, useContext, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { AuthContext } from "./AuthContext";
import { toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

const SERVER_URL = process.env.REACT_APP_SERVER_URL || "http://localhost:5000";

const Login = () => {
    const { login } = useContext(AuthContext);
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [errorMessage, setErrorMessage] = useState("");
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    // 🧹 Clear error on input
    useEffect(() => {
        if (email || password) setErrorMessage("");
    }, [email, password]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);

        // ⚠️ Validation
        if (!email || !password) {
            setErrorMessage("Please fill in all fields");
            setLoading(false);
            return;
        }
        if (!/\S+@\S+\.\S+/.test(email)) {
            setErrorMessage("Invalid email format");
            setLoading(false);
            return;
        }

        try {
            const response = await fetch(`${SERVER_URL}/auth/login`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email, password }),
            });

            const data = await response.json();

            if (response.ok) {
                login(data.access_token, data.role); // Save token to context/localStorage
                toast.success("Login successful!");

                // 🎯 Role-based navigation
                navigate(data.role === "admin" ? "/admin" : "/dashboard");
            } else {
                setErrorMessage(data.error || "Invalid credentials");
                toast.error(data.error || "Invalid credentials");
            }
        } catch (error) {
            setErrorMessage("Failed to connect to the server");
            toast.error("Failed to connect to the server");
            console.error("Login error:", error);
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
                <h2 className="text-2xl font-bold mb-4 text-center text-blue-600">Login</h2>

                {errorMessage && (
                    <p className="text-red-500 mb-3 text-center">{errorMessage}</p>
                )}

                <label className="block mb-2 text-sm font-medium text-gray-600">Email</label>
                <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="user@example.com"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md mb-4"
                    required
                />

                <label className="block mb-2 text-sm font-medium text-gray-600">Password</label>
                <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md mb-4"
                    required
                />

                <button
                    type="submit"
                    className={`w-full py-2 rounded-md text-white transition flex justify-center items-center ${
                        loading ? "bg-blue-300" : "bg-blue-500 hover:bg-blue-600"
                    }`}
                    disabled={loading}
                >
                    {loading ? (
                        <>
                            <span className="animate-spin mr-2">🔄</span> Logging in...
                        </>
                    ) : (
                        "Login"
                    )}
                </button>

                <p className="mt-4 text-center text-sm">
                    Don't have an account?{" "}
                    <a href="/register" className="text-blue-500 hover:underline">
                        Register
                    </a>
                </p>
            </form>
        </div>
    );
};

export default Login;
