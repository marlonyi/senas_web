// src/App.jsx
import React, { useState, useEffect, useCallback } from 'react';
import './index.css';

import WelcomeScreen from './components/WelcomeScreen.jsx';
import Login from './components/Login.jsx';
import Register from './components/Register.jsx';
import Home from './components/Home.jsx';
import Courses from './components/Courses.jsx';
import UserDetails from './components/UserDetails.jsx';
import UserProfile from './components/UserProfile.jsx';
import Tasks from './components/Tasks.jsx';
import Goals from './components/Goals.jsx';
import Habits from './components/Habits.jsx';
import Rewards from './components/Rewards.jsx';
import Friends from './components/Friends.jsx';
import Leaderboard from './components/Leaderboard.jsx';
import Settings from './components/Settings.jsx';

const DJANGO_API_BASE_URL = "http://127.0.0.1:8000";

export default function App() {
    const [currentPage, setCurrentPage] = useState('welcome');
    const [user, setUser] = useState(null);
    const [authToken, setAuthToken] = useState(localStorage.getItem('authToken'));
    const [refreshToken, setRefreshToken] = useState(localStorage.getItem('refreshToken'));
    const [errorMessage, setErrorMessage] = useState('');
    const [loadingApp, setLoadingApp] = useState(true);

    const fetchUserProfile = useCallback(async (token) => {
        try {
            const response = await fetch(`${DJANGO_API_BASE_URL}/api/usuarios/mi-perfil/`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`,
                },
            });

            if (!response.ok) {
                const errorData = await response.json();
                setErrorMessage(`Error al cargar perfil: ${errorData.detail || response.statusText}.`);
                return null;
            }

            const profileData = await response.json();
            return {
                id: profileData.id,
                email: profileData.email,
                username: profileData.username,
                first_name: profileData.first_name,
                last_name: profileData.last_name,
                avatar: profileData.avatar,
                level: profileData.level,
                experience_points: profileData.experience_points,
            };
        } catch (error) {
            setErrorMessage('Error de red al obtener el perfil.');
            return null;
        }
    }, []);

    const handleLogout = useCallback(async () => {
        if (authToken && refreshToken) {
            try {
                const response = await fetch(`${DJANGO_API_BASE_URL}/api/usuarios/logout/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${authToken}`,
                    },
                    body: JSON.stringify({ refresh: refreshToken }),
                });
                if (!response.ok) {
                    console.warn('Logout en el backend falló o no fue necesario:', await response.text());
                }
            } catch (error) {
                setErrorMessage('Error de red al intentar cerrar sesión.');
            }
        }

        setAuthToken(null);
        setRefreshToken(null);
        setUser(null);
        localStorage.removeItem('authToken');
        localStorage.removeItem('refreshToken');
        setCurrentPage('welcome');
        setErrorMessage('Has cerrado sesión exitosamente.');
    }, [authToken, refreshToken]);

    const handleLoginSuccess = useCallback(async (accessToken, newRefreshToken) => {
        setAuthToken(accessToken);
        setRefreshToken(newRefreshToken);
        localStorage.setItem('authToken', accessToken);
        localStorage.setItem('refreshToken', newRefreshToken);

        const userProfile = await fetchUserProfile(accessToken);
        if (userProfile) {
            setUser(userProfile);
            setErrorMessage('');
            setCurrentPage('home');
        } else {
            handleLogout();
            setErrorMessage('No se pudo cargar el perfil de usuario.');
        }
    }, [fetchUserProfile, handleLogout]);

    useEffect(() => {
        const initializeApp = async () => {
            const storedAuthToken = localStorage.getItem('authToken');
            const storedRefreshToken = localStorage.getItem('refreshToken');

            if (storedAuthToken && storedRefreshToken) {
                const userProfile = await fetchUserProfile(storedAuthToken);
                if (userProfile) {
                    setUser(userProfile);
                    setAuthToken(storedAuthToken);
                    setRefreshToken(storedRefreshToken);
                    setCurrentPage('home');
                } else {
                    try {
                        const refreshResponse = await fetch(`${DJANGO_API_BASE_URL}/api/token/refresh/`, {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ refresh: storedRefreshToken }),
                        });
                        const refreshData = await refreshResponse.json();
                        if (refreshResponse.ok) {
                            const newAccessToken = refreshData.access;
                            localStorage.setItem('authToken', newAccessToken);
                            setAuthToken(newAccessToken);
                            const refreshedUserProfile = await fetchUserProfile(newAccessToken);
                            if (refreshedUserProfile) {
                                setUser(refreshedUserProfile);
                                setCurrentPage('home');
                            } else {
                                handleLogout();
                            }
                        } else {
                            handleLogout();
                        }
                    } catch (error) {
                        handleLogout();
                    }
                }
            } else {
                setCurrentPage('welcome');
            }
            setLoadingApp(false);
        };

        initializeApp();
    }, [fetchUserProfile, handleLogout]);

    const renderPage = () => {
        switch (currentPage) {
            case 'welcome':
                return <WelcomeScreen setCurrentPage={setCurrentPage} />;
            case 'login':
                return <Login DJANGO_API_BASE_URL={DJANGO_API_BASE_URL} onLoginSuccess={handleLoginSuccess} setErrorMessage={setErrorMessage} setCurrentPage={setCurrentPage} />;
            case 'register':
                return <Register DJANGO_API_BASE_URL={DJANGO_API_BASE_URL} setCurrentPage={setCurrentPage} setErrorMessage={setErrorMessage} />;
            case 'home':
                if (user && authToken) {
                    return <Home user={user} authToken={authToken} DJANGO_API_BASE_URL={DJANGO_API_BASE_URL} setErrorMessage={setErrorMessage} setCurrentPage={setCurrentPage} onLogout={handleLogout} setUserProfile={setUser} />;
                } else {
                    setCurrentPage('login');
                    setErrorMessage('Por favor, inicia sesión para acceder.');
                    return null;
                }
            case 'courses':
                if (user && authToken) {
                    return <Courses DJANGO_API_BASE_URL={DJANGO_API_BASE_URL} authToken={authToken} userId={user.id} setCurrentPage={setCurrentPage} setErrorMessage={setErrorMessage} />;
                } else {
                    setCurrentPage('login');
                    setErrorMessage('Por favor, inicia sesión para acceder a los cursos.');
                    return null;
                }
            case 'perfil':
                return <UserDetails DJANGO_API_BASE_URL={DJANGO_API_BASE_URL} makeAuthenticatedRequest={(url, options = {}) => fetch(url, { ...options, headers: { ...(options.headers || {}), Authorization: `Bearer ${authToken}` } })} setErrorMessage={setErrorMessage} accessToken={authToken} />;
            default:
                return <WelcomeScreen setCurrentPage={setCurrentPage} />;
        }
    };

    if (loadingApp) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-gray-100">
                <div className="animate-spin rounded-full h-16 w-16 border-t-4 border-b-4 border-blue-500"></div>
                <p className="ml-4 text-xl text-gray-700">Cargando aplicación...</p>
            </div>
        );
    }

    return (
        <div className="font-sans">
            {errorMessage && (
                <div className="fixed top-4 left-1/2 -translate-x-1/2 bg-red-500 text-white p-4 rounded-lg shadow-xl z-50 animate-fade-in-down max-w-sm w-11/12 text-center">
                    <p className="font-semibold">{errorMessage}</p>
                    <button onClick={() => setErrorMessage('')} className="mt-2 text-white opacity-75 hover:opacity-100 transition-opacity">
                        Cerrar
                    </button>
                </div>
            )}
            {renderPage()}
        </div>
    );
}
