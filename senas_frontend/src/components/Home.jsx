// src/components/Home.jsx
import React, { useState, useEffect, useCallback } from 'react';

// Importa los componentes de contenido del dashboard (asegúrate de que existan)
import UserProfile from './UserProfile.jsx';
import Tasks from './Tasks.jsx';
import Goals from './Goals.jsx';
import Habits from './Habits.jsx';
import Rewards from './Rewards.jsx';
import Friends from './Friends.jsx';
import Leaderboard from './Leaderboard.jsx';
import Settings from './Settings.jsx';

export default function Home({ user, authToken, DJANGO_API_BASE_URL, setErrorMessage, setCurrentPage, onLogout, setUserProfile }) {
    const [currentPageContent, setCurrentPageContent] = useState('tasks'); // Estado para la navegación interna del dashboard
    const [isRefreshingToken, setIsRefreshingToken] = useState(false); // Para evitar refrescos concurrentes

    // Función genérica para realizar peticiones autenticadas
    const makeAuthenticatedRequest = useCallback(async (url, options = {}) => {
        let currentAccessToken = authToken; // Usa el token del estado de App.jsx

        let response = await fetch(url, {
            ...options,
            headers: {
                ...options.headers,
                'Authorization': `Bearer ${currentAccessToken}`,
            },
        });

        // Si el token expiró y la respuesta es 401 (Unauthorized)
        if (response.status === 401) {
            if (isRefreshingToken) { // Si ya hay un proceso de refresco en marcha, espera o falla
                console.warn('Ya se está refrescando un token, evitando reintento concurrente.');
                throw new Error('Petición no autorizada. Token requiere refresco o re-login.');
            }

            console.log('Token expirado o inválido, intentando refrescar...');
            setIsRefreshingToken(true);
            setErrorMessage('Sesión a punto de expirar. Refrescando...');

            try {
                const refreshResponse = await fetch(`${DJANGO_API_BASE_URL}/api/token/refresh/`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ refresh: localStorage.getItem('refreshToken') }), // Usar el refresh token del localStorage
                });

                const refreshData = await refreshResponse.json();

                if (refreshResponse.ok) {
                    const newAccessToken = refreshData.access;
                    console.log('Token refrescado exitosamente.');
                    localStorage.setItem('authToken', newAccessToken);
                    // Actualizar el authToken en el estado de App.jsx
                    // Nota: En un contexto real con Redux/Context API, esto se propagaría automáticamente.
                    // Aquí, necesitamos que App.jsx reciba el nuevo token.
                    // Para simplificar, asumimos que App.jsx se re-renderizará con el nuevo token del localStorage
                    // o podrías pasar una función setAuthToken desde App.jsx
                    
                    currentAccessToken = newAccessToken; // Usa el nuevo token para el reintento
                    setErrorMessage('Sesión refrescada. Reintentando operación.');

                    // Reintenta la petición original con el nuevo token
                    response = await fetch(url, {
                        ...options,
                        headers: {
                            ...options.headers,
                            'Authorization': `Bearer ${currentAccessToken}`,
                        },
                    });
                } else {
                    console.error('Error al refrescar token:', refreshData);
                    setErrorMessage('Sesión expirada. Por favor, inicia sesión de nuevo.');
                    onLogout(); // Forzar cierre de sesión si el refresco falla
                    throw new Error('Fallo al refrescar token. Necesita re-login.');
                }
            } catch (refreshError) {
                console.error('Excepción durante el refresco del token:', refreshError);
                setErrorMessage('Error al refrescar la sesión. Por favor, inicia sesión de nuevo.');
                onLogout();
                throw refreshError; // Propaga el error para que la petición original falle
            } finally {
                setIsRefreshingToken(false);
            }
        }

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || `Error ${response.status}: ${response.statusText}`);
        }

        return response;
    }, [authToken, DJANGO_API_BASE_URL, localStorage, onLogout, setErrorMessage, isRefreshingToken]);


    // Función para renderizar el contenido de la página actual del dashboard
    const renderContent = () => {
        if (!user) { // Asegura que el objeto user esté disponible
            return (
                <div className="flex justify-center items-center h-full text-gray-700">
                    <p>Cargando datos de usuario...</p>
                </div>
            );
        }

        // Aquí pasamos makeAuthenticatedRequest a los subcomponentes para que puedan hacer llamadas a la API
        switch (currentPageContent) {
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
            case 'settings':
                return <Settings userId={user.id} makeAuthenticatedRequest={makeAuthenticatedRequest} DJANGO_API_BASE_URL={DJANGO_API_BASE_URL} setErrorMessage={setErrorMessage} userProfile={user} setUserProfile={setUserProfile} />;
            case 'courses': // Agregamos el caso para Courses
                return <Courses 
                            DJANGO_API_BASE_URL={DJANGO_API_BASE_URL} 
                            authToken={authToken} 
                            userId={user.id} 
                            setCurrentPage={setCurrentPage} 
                            setErrorMessage={setErrorMessage}
                        />;
            default:
                return <Tasks userId={user.id} makeAuthenticatedRequest={makeAuthenticatedRequest} DJANGO_API_BASE_URL={DJANGO_API_BASE_URL} setErrorMessage={setErrorMessage} />;
        }
    };

    return (
        <div className="min-h-screen flex flex-col lg:flex-row bg-gray-100 font-sans">
            {/* Sidebar de Navegación */}
            <aside className="w-full lg:w-64 bg-gradient-to-br from-blue-700 to-blue-900 text-white shadow-lg p-6 lg:p-4 flex flex-col rounded-r-xl">
                <div className="text-center mb-8">
                    <h1 className="text-4xl font-extrabold tracking-tight">LevelUp!</h1>
                    <p className="text-blue-200 text-lg mt-1">¡Gamifica tu vida!</p>
                </div>

                {/* Componente UserProfile */}
                {user && (
                    <UserProfile
                        userProfile={user} // Pasamos el objeto user completo
                        onLogout={onLogout}
                        makeAuthenticatedRequest={makeAuthenticatedRequest}
                        DJANGO_API_BASE_URL={DJANGO_API_BASE_URL}
                        setErrorMessage={setErrorMessage}
                        setUserProfile={setUserProfile} // Para que UserProfile pueda actualizar el user object en App.jsx
                    />
                )}

                <nav className="flex-grow">
                    <ul className="space-y-3">
                        {['tasks', 'goals', 'habits', 'rewards', 'friends', 'leaderboard', 'courses', 'settings'].map((item) => ( // Agregado 'courses' al menú
                            <li key={item}>
                                <button
                                    onClick={() => setCurrentPageContent(item)}
                                    className={`w-full text-left py-3 px-4 rounded-lg flex items-center transition duration-200 ease-in-out
                                        ${currentPageContent === item
                                            ? 'bg-blue-600 text-white shadow-md transform scale-105'
                                            : 'hover:bg-blue-700 hover:text-blue-100 text-blue-200'
                                        }`}
                                >
                                    {/* Aquí podrías usar iconos para cada elemento del menú */}
                                    <span className="capitalize text-lg font-medium">{item}</span>
                                </button>
                            </li>
                        ))}
                    </ul>
                </nav>

                <div className="mt-8">
                    <button
                        onClick={onLogout}
                        className="w-full bg-red-600 text-white py-3 px-4 rounded-lg flex items-center justify-center hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 focus:ring-offset-blue-800 transition duration-150 ease-in-out"
                    >
                        <span className="text-lg font-medium">Cerrar Sesión</span>
                    </button>
                </div>
            </aside>

            {/* Contenido Principal */}
            <main className="flex-1 p-6 lg:p-8 overflow-auto">
                <div className="bg-white rounded-xl shadow-lg p-6 h-full">
                    {renderContent()}
                </div>
            </main>
        </div>
    );
}
