import { createContext, useEffect, useState } from "react";
import jwtDecode from "jwt-decode";

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
    const [auth, setAuth] = useState(() => {
        const token = localStorage.getItem("token");
        const role = localStorage.getItem("role");
        const email = localStorage.getItem("email");

        if (token) {
            try {
                const decoded = jwtDecode(token);
                const expiry = decoded.exp * 1000;

                if (Date.now() > expiry) {
                    console.log("⚠️ Token expired. Clearing session.");
                    localStorage.clear();
                    return null;
                }

                return { token, role, email };
            } catch (error) {
                console.error("❌ Invalid token:", error);
                localStorage.clear();
                return null;
            }
        }
        return null;
    });

    // 🔐 Handle login
    const login = (token, role, email) => {
        localStorage.setItem("token", token);
        localStorage.setItem("role", role);
        localStorage.setItem("email", email);
        setAuth({ token, role, email });
    };

    // 🔒 Handle logout
    const logout = () => {
        localStorage.clear();
        setAuth(null);
    };

    // 🧠 Watch token expiration (on app load)
    useEffect(() => {
        const token = localStorage.getItem("token");

        if (token) {
            try {
                const decoded = jwtDecode(token);
                const expiry = decoded.exp * 1000;
                const timeRemaining = expiry - Date.now();

                if (timeRemaining <= 0) {
                    logout();
                } else {
                    // Optional: Auto-logout when token expires
                    const timeout = setTimeout(() => {
                        console.log("⏰ Session expired automatically.");
                        logout();
                    }, timeRemaining);

                    return () => clearTimeout(timeout);
                }
            } catch (error) {
                console.error("Error checking token:", error);
                logout();
            }
        }
    }, []);

    return (
        <AuthContext.Provider value={{ auth, login, logout }}>
            {children}
        </AuthContext.Provider>
    );
};
