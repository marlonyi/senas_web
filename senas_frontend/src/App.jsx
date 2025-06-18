// src/App.jsx
import React, { useState, useEffect, useCallback } from 'react';
import './index.css'; // Asegúrate de importar tu archivo CSS principal

// Importa tus componentes de página
import WelcomeScreen from './components/WelcomeScreen.jsx';
import Login from './components/Login.jsx';
import Register from './components/Register.jsx';
import Home from './components/Home.jsx';
import Courses from './components/Courses.jsx';

// Importa los componentes placeholder del dashboard
import UserProfile from './components/UserProfile.jsx';
import Tasks from './components/Tasks.jsx';
import Goals from './components/Goals.jsx';
import Habits from './components/Habits.jsx';
import Rewards from './components/Rewards.jsx';
import Friends from './components/Friends.jsx';
import Leaderboard from './components/Leaderboard.jsx';
import Settings from './components/Settings.jsx';


// URL base de tu backend Django
const DJANGO_API_BASE_URL = "	http://127.0.0.1:8000"; 

export default function App() {
    // Estados principales de la aplicación
    const [currentPage, setCurrentPage] = useState('welcome'); // Página actual que se muestra
    const [user, setUser] = useState(null); // Objeto de usuario completo (desde Django)
    const [authToken, setAuthToken] = useState(localStorage.getItem('authToken')); // Token de acceso JWT
    const [refreshToken, setRefreshToken] = useState(localStorage.getItem('refreshToken')); // Token de refresco JWT
    const [errorMessage, setErrorMessage] = useState(''); // Mensajes de error para mostrar al usuario
    const [loadingApp, setLoadingApp] = useState(true); // Estado de carga inicial de la aplicación

    // Función para obtener los detalles del perfil del usuario desde Django
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
                console.error('Error al obtener perfil de usuario:', errorData);
                setErrorMessage(`Error al cargar perfil: ${errorData.detail || response.statusText}.`);
                return null;
            }

            const profileData = await response.json();
            // Asegúrate de que los campos coincidan con tu serializer de Django (ej. id, email, username, first_name, last_name)
            return {
                id: profileData.id, 
                email: profileData.email,
                username: profileData.username,
                first_name: profileData.first_name,
                last_name: profileData.last_name,
                // Añade aquí otros campos de tu perfil si existen (ej. avatar, level, experience_points)
                avatar: profileData.avatar, 
                level: profileData.level,
                experience_points: profileData.experience_points,
            };
        } catch (error) {
            console.error('Error de conexión al obtener perfil:', error);
            setErrorMessage('Error de red al obtener el perfil. Revisa tu conexión con el backend.');
            return null;
        }
    }, [DJANGO_API_BASE_URL, setErrorMessage]);

    // Función para manejar el cierre de sesión
    const handleLogout = useCallback(async () => {
        if (authToken && refreshToken) {
            try {
                const response = await fetch(`${DJANGO_API_BASE_URL}/api/usuarios/logout/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${authToken}`, 
                    },
                    body: JSON.stringify({ refresh: refreshToken }), // Asegúrate de que tu endpoint de logout espera 'refresh'
                });
                if (!response.ok) {
                    console.warn('Logout en el backend falló o no fue necesario:', await response.text());
                } else {
                    console.log('Sesión cerrada en el backend.');
                }
            } catch (error) {
                console.error('Error al intentar cerrar sesión en el backend:', error);
                setErrorMessage('Error de red al intentar cerrar sesión.');
            }
        }

        // Limpiar el estado de autenticación y localStorage
        setAuthToken(null);
        setRefreshToken(null);
        setUser(null);
        localStorage.removeItem('authToken');
        localStorage.removeItem('refreshToken');
        setCurrentPage('welcome'); 
        setErrorMessage('Has cerrado sesión exitosamente.');
    }, [authToken, refreshToken, DJANGO_API_BASE_URL, setErrorMessage]);

    // Función que se llama desde Login.jsx al tener éxito la obtención inicial de tokens
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
            setErrorMessage('No se pudo cargar el perfil de usuario. Por favor, inicia sesión de nuevo.');
        }
    }, [fetchUserProfile, handleLogout, setErrorMessage]);

    // useEffect para cargar el estado de autenticación al inicio
    useEffect(() => {
        const initializeApp = async () => {
            const storedAuthToken = localStorage.getItem('authToken');
            const storedRefreshToken = localStorage.getItem('refreshToken');

            if (storedAuthToken && storedRefreshToken) {
                // Intentar validar el token y obtener el perfil
                const userProfile = await fetchUserProfile(storedAuthToken);
                if (userProfile) {
                    setUser(userProfile);
                    setAuthToken(storedAuthToken);
                    setRefreshToken(storedRefreshToken);
                    setCurrentPage('home');
                } else {
                    // Si el token no es válido o el perfil no se carga, intentar refrescar
                    console.log('Token existente inválido o perfil no cargado. Intentando refrescar.');
                    try {
                        const refreshResponse = await fetch(`${DJANGO_API_BASE_URL}/api/token/refresh/`, {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ refresh: storedRefreshToken }),
                        });
                        const refreshData = await refreshResponse.json();
                        if (refreshResponse.ok) {
                            console.log('Token refrescado exitosamente.');
                            const newAccessToken = refreshData.access;
                            localStorage.setItem('authToken', newAccessToken);
                            setAuthToken(newAccessToken);
                            const refreshedUserProfile = await fetchUserProfile(newAccessToken);
                            if (refreshedUserProfile) {
                                setUser(refreshedUserProfile);
                                setCurrentPage('home');
                            } else {
                                handleLogout(); // Si falla después del refresco, logout
                            }
                        } else {
                            console.error('Fallo al refrescar el token:', refreshData);
                            handleLogout(); // Si no se puede refrescar, logout
                        }
                    } catch (error) {
                        console.error('Error de red al refrescar el token:', error);
                        handleLogout(); // Error de red al refrescar, logout
                    }
                }
            } else {
                setCurrentPage('welcome'); // Si no hay tokens, ir a la pantalla de bienvenida
            }
            setLoadingApp(false); // La aplicación terminó de cargar su estado inicial
        };

        initializeApp();
    }, [fetchUserProfile, handleLogout]); // Dependencias para re-ejecutar el efecto si cambian

    // Renderizado condicional de componentes según el estado 'currentPage'
    const renderPage = () => {
        switch (currentPage) {
            case 'welcome':
                return <WelcomeScreen setCurrentPage={setCurrentPage} />;
            case 'login':
                return <Login 
                            DJANGO_API_BASE_URL={DJANGO_API_BASE_URL} 
                            onLoginSuccess={handleLoginSuccess} 
                            setErrorMessage={setErrorMessage} 
                            setCurrentPage={setCurrentPage}
                        />;
            case 'register':
                return <Register 
                            DJANGO_API_BASE_URL={DJANGO_API_BASE_URL} 
                            setCurrentPage={setCurrentPage} 
                            setErrorMessage={setErrorMessage} 
                        />;
            case 'home':
                if (user && authToken) {
                    return <Home 
                                user={user} 
                                authToken={authToken}
                                DJANGO_API_BASE_URL={DJANGO_API_BASE_URL}
                                setErrorMessage={setErrorMessage}
                                setCurrentPage={setCurrentPage} // Pasa setCurrentPage
                                onLogout={handleLogout} // Asegúrate de pasar onLogout
                                setUserProfile={setUser} // Para que UserProfile pueda actualizar el user object
                            />;
                } else {
                    // Si no hay usuario o token, redirigir al login
                    setCurrentPage('login');
                    setErrorMessage('Por favor, inicia sesión para acceder.');
                    return null;
                }
            case 'courses':
                if (user && authToken) {
                    return <Courses 
                                DJANGO_API_BASE_URL={DJANGO_API_BASE_URL} 
                                authToken={authToken} 
                                userId={user.id} 
                                setCurrentPage={setCurrentPage} 
                                setErrorMessage={setErrorMessage} 
                            />;
                } else {
                    setCurrentPage('login'); 
                    setErrorMessage('Por favor, inicia sesión para acceder a los cursos.');
                    return null;
                }
            // Agrega más casos para tus otras páginas si son rutas directas desde App.jsx
            // Por ejemplo, para los componentes del dashboard, Home.jsx ya los maneja internamente.
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
        <div className="font-sans"> {/* Aplica la fuente globalmente aquí */}
            {errorMessage && (
                <div className="fixed top-4 left-1/2 -translate-x-1/2 bg-red-500 text-white p-4 rounded-lg shadow-xl z-50 animate-fade-in-down max-w-sm w-11/12 text-center">
                    <p className="font-semibold">{errorMessage}</p>
                    <button
                        onClick={() => setErrorMessage('')}
                        className="mt-2 text-white opacity-75 hover:opacity-100 transition-opacity"
                    >
                        Cerrar
                    </button>
                </div>
            )}
            {renderPage()}
        </div>
    );
}
