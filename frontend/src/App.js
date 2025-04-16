import React from "react";
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation } from "react-router-dom";
import { ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

import Login from "./components/Login";
import Register from "./components/Register";
import AdminDashboard from "./components/AdminDashboard";
import ProctoringDashboard from "./components/ProctoringDashboard";
import { AuthProvider, AuthContext } from "./components/AuthContext";

// 🔐 ProtectedRoute component with role check
const ProtectedRoute = ({ Component, roles }) => {
    const { auth } = React.useContext(AuthContext);
    const location = useLocation();

    return auth && roles.includes(auth.role) ? (
        <Component />
    ) : (
        <Navigate to="/login" state={{ from: location }} replace />
    );
};

const App = () => {
    return (
        <AuthProvider>
            <Router>
                <ToastContainer />
                <Routes>
                    <Route path="/login" element={<Login />} />
                    <Route path="/register" element={<Register />} />
                    <Route
                        path="/admin"
                        element={<ProtectedRoute Component={AdminDashboard} roles={["admin"]} />}
                    />
                    <Route
                        path="/dashboard"
                        element={<ProtectedRoute Component={ProctoringDashboard} roles={["admin", "student"]} />}
                    />
                    <Route path="*" element={<Navigate to="/login" replace />} />
                </Routes>
            </Router>
        </AuthProvider>
    );
};

export default App;
