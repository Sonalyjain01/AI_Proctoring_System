import { createContext, useEffect, useState } from "react";
import jwtDecode from "jwt-decode"; //  Decode JWT token

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
                    console.log("Token expired. Logging out...");
                    localStorage.clear();
                    return null;
                }

                return { token, role, email };
            } catch (error) {
                console.error("Invalid token:", error);
                localStorage.clear();
                return null;
            }
        } else {
            return null;
        }
    });

    //  Save user data on login
    const login = (token, role, email) => {
        localStorage.setItem("token", token);
        localStorage.setItem("role", role);
        localStorage.setItem("email", email);
        setAuth({ token, role, email });
    };

    //  Clear storage on logout
    const logout = () => {
        localStorage.clear();
        setAuth(null);
    };

    //  Check token validity when app reloads
    useEffect(() => {
        const token = localStorage.getItem("token");
        if (token) {
            try {
                const decoded = jwtDecode(token);
                const expiry = decoded.exp * 1000;
                if (Date.now() > expiry) {
                    console.log("Session expired. Logging out...");
                    logout();
                }
            } catch (error) {
                console.error("Invalid token:", error);
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
