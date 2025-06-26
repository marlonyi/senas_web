// src/components/Home.jsx
import React, { useState, useCallback } from 'react';

// Componentes del dashboard
import UserProfile from './UserProfile.jsx';
import Tasks from './Tasks.jsx';
import Goals from './Goals.jsx';
import Habits from './Habits.jsx';
import Rewards from './Rewards.jsx';
import Friends from './Friends.jsx';
import Leaderboard from './Leaderboard.jsx';
import Settings from './Settings.jsx';
import Courses from './Courses.jsx';
import UserDetailsLayout from './UserDetailsLayout.jsx';

export default function Home({
    user,
    authToken,
    DJANGO_API_BASE_URL,
    setErrorMessage,
    setCurrentPage,
    onLogout,
    setUserProfile
}) {
    const [currentPageContent, setCurrentPageContent] = useState('tasks');
    const [isRefreshingToken, setIsRefreshingToken] = useState(false);

    // Función reutilizable para peticiones autenticadas
    const makeAuthenticatedRequest = useCallback(async (url, options = {}) => {
        let currentAccessToken = authToken;

        let response = await fetch(url, {
            ...options,
            headers: {
                ...options.headers,
                'Authorization': `Bearer ${currentAccessToken}`,
            },
        });

        if (response.status === 401 && !isRefreshingToken) {
            console.log('Token expirado, intentando refrescar...');
            setIsRefreshingToken(true);
            setErrorMessage('Refrescando sesión...');

            try {
                const refreshResponse = await fetch(`${DJANGO_API_BASE_URL}/api/token/refresh/`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ refresh: localStorage.getItem('refreshToken') }),
                });

                const refreshData = await refreshResponse.json();

                if (refreshResponse.ok) {
                    const newAccessToken = refreshData.access;
                    localStorage.setItem('authToken', newAccessToken);
                    currentAccessToken = newAccessToken;
                    setErrorMessage('Sesión actualizada.');

                    response = await fetch(url, {
                        ...options,
                        headers: {
                            ...options.headers,
                            'Authorization': `Bearer ${currentAccessToken}`,
                        },
                    });
                } else {
                    console.error('Fallo al refrescar token:', refreshData);
                    setErrorMessage('Sesión expirada. Inicia sesión de nuevo.');
                    onLogout();
                    throw new Error('Error al refrescar sesión.');
                }
            } catch (error) {
                console.error('Excepción al refrescar token:', error);
                setErrorMessage('Error crítico al refrescar sesión.');
                onLogout();
                throw error;
            } finally {
                setIsRefreshingToken(false);
            }
        } else if (response.status === 401) {
            throw new Error('Token inválido. Intenta iniciar sesión nuevamente.');
        }

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || `Error ${response.status}`);
        }

        return response;
    }, [authToken, DJANGO_API_BASE_URL, isRefreshingToken, onLogout, setErrorMessage]);

    const renderContent = () => {
        if (!user) {
            return <div className="flex justify-center items-center h-full text-gray-700">Cargando datos...</div>;
        }

        switch (currentPageContent) {
            case 'perfil':
                return (
                    <UserDetailsLayout
                        DJANGO_API_BASE_URL={DJANGO_API_BASE_URL}
                        makeAuthenticatedRequest={makeAuthenticatedRequest}
                        setErrorMessage={setErrorMessage}
                        accessToken={authToken}
                    />
                );
            case 'tasks':
                return <Tasks userId={user.id} makeAuthenticatedRequest={makeAuthenticatedRequest} DJANGO_API_BASE_URL={DJANGO_API_BASE_URL} setErrorMessage={setErrorMessage} />;
            case 'goals':
                return <Goals userId={user.id} makeAuthenticatedRequest={makeAuthenticatedRequest} DJANGO_API_BASE_URL={DJANGO_API_BASE_URL} setErrorMessage={setErrorMessage} />;
            case 'habits':
                return <Habits userId={user.id} makeAuthenticatedRequest={makeAuthenticatedRequest} DJANGO_API_BASE_URL={DJANGO_API_BASE_URL} setErrorMessage={setErrorMessage} />;
            case 'rewards':
                return <Rewards userId={user.id} makeAuthenticatedRequest={makeAuthenticatedRequest} DJANGO_API_BASE_URL={DJANGO_API_BASE_URL} setErrorMessage={setErrorMessage} />;
            case 'friends':
                return <Friends userId={user.id} makeAuthenticatedRequest={makeAuthenticatedRequest} DJANGO_API_BASE_URL={DJANGO_API_BASE_URL} setErrorMessage={setErrorMessage} />;
            case 'leaderboard':
                return <Leaderboard userId={user.id} makeAuthenticatedRequest={makeAuthenticatedRequest} DJANGO_API_BASE_URL={DJANGO_API_BASE_URL} setErrorMessage={setErrorMessage} />;
            case 'courses':
                return <Courses DJANGO_API_BASE_URL={DJANGO_API_BASE_URL} authToken={authToken} userId={user.id} setCurrentPage={setCurrentPage} setErrorMessage={setErrorMessage} />;
            case 'settings':
                return <Settings userId={user.id} makeAuthenticatedRequest={makeAuthenticatedRequest} DJANGO_API_BASE_URL={DJANGO_API_BASE_URL} setErrorMessage={setErrorMessage} userProfile={user} setUserProfile={setUserProfile} />;
            default:
                return <Tasks userId={user.id} makeAuthenticatedRequest={makeAuthenticatedRequest} DJANGO_API_BASE_URL={DJANGO_API_BASE_URL} setErrorMessage={setErrorMessage} />;
        }
    };

    return (
        <div className="min-h-screen flex flex-col lg:flex-row bg-gray-100 font-sans">
            {/* Sidebar */}
            <aside className="w-full lg:w-64 bg-gradient-to-br from-blue-700 to-blue-900 text-white shadow-lg p-6 lg:p-4 flex flex-col rounded-r-xl">
                <div className="text-center mb-8">
                    <h1 className="text-4xl font-extrabold tracking-tight">LevelUp!</h1>
                    <p className="text-blue-200 text-lg mt-1">¡Gamifica tu vida!</p>
                </div>

                {user && (
                    <UserProfile
                        userProfile={user}
                        onLogout={onLogout}
                        makeAuthenticatedRequest={makeAuthenticatedRequest}
                        DJANGO_API_BASE_URL={DJANGO_API_BASE_URL}
                        setErrorMessage={setErrorMessage}
                        setUserProfile={setUserProfile}
                    />
                )}

                <nav className="flex-grow">
                    <ul className="space-y-3">
                        {[
                            'perfil',
                            'tasks',
                            'goals',
                            'habits',
                            'rewards',
                            'friends',
                            'leaderboard',
                            'courses',
                            'settings'
                        ].map((item) => (
                            <li key={item}>
                                <button
                                    onClick={() => setCurrentPageContent(item)}
                                    className={`w-full text-left py-3 px-4 rounded-lg flex items-center transition duration-200 ease-in-out
                                        ${currentPageContent === item
                                            ? 'bg-blue-600 text-white shadow-md transform scale-105'
                                            : 'hover:bg-blue-700 hover:text-blue-100 text-blue-200'
                                        }`}
                                >
                                    <span className="capitalize text-lg font-medium">{item}</span>
                                </button>
                            </li>
                        ))}
                    </ul>
                </nav>

                <div className="mt-8">
                    <button
                        onClick={onLogout}
                        className="w-full bg-red-600 text-white py-3 px-4 rounded-lg flex items-center justify-center hover:bg-red-700 transition duration-150"
                    >
                        <span className="text-lg font-medium">Cerrar Sesión</span>
                    </button>
                </div>
            </aside>

            {/* Contenido principal */}
            <main className="flex-1 p-6 lg:p-8 overflow-auto">
                <div className="bg-white rounded-xl shadow-lg p-6 h-full">
                    {renderContent()}
                </div>
            </main>
        </div>
    );
}
