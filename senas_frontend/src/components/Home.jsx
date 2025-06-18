// src/components/Home.jsx
import React, { useState, useEffect, useCallback } from 'react';
import UserProfile from './UserProfile';
import Tasks from './Tasks';
import Goals from './Goals';
import Habits from './Habits';
import Rewards from './Rewards';
import Friends from './Friends';
import Leaderboard from './Leaderboard';
import Settings from './Settings';

export default function Home({ DJANGO_API_BASE_URL, setCurrentPage, setErrorMessage, accessToken, refreshToken, onLogout }) {
    const [currentPageContent, setCurrentPageContent] = useState('tasks');
    const [userProfile, setUserProfile] = useState(null);
    const [loadingProfile, setLoadingProfile] = useState(true);
    const [isRefreshingToken, setIsRefreshingToken] = useState(false);

    // Función para refrescar el token de acceso usando el token de refresco
    const refreshAccessToken = useCallback(async () => {
        if (isRefreshingToken) return false; // Evita múltiples intentos de refresco simultáneos

        setIsRefreshingToken(true);
        setErrorMessage(''); // Limpiar errores previos

        try {
            console.log('Intentando refrescar token con:', refreshToken);
            const response = await fetch(`${DJANGO_API_BASE_URL}/api/token/refresh/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ refresh: refreshToken }),
            });

            const data = await response.json();

            if (response.ok) {
                console.log('Token refrescado exitosamente:', data.access);
                // Actualiza el token de acceso en el localStorage y en el estado de App.jsx
                localStorage.setItem('accessToken', data.access);
                // Llama a una función en App.jsx para actualizar el accessToken si es necesario
                // (esto asume que App.jsx tiene una forma de actualizar su estado de accessToken)
                // Por simplicidad aquí, asumimos que App.jsx lo leerá del localStorage si cambia.
                // En una aplicación real, probablemente querrías propagar esto a través de un prop o contexto.
                // onLoginSuccess(data.access, refreshToken); // Esto volvería a guardar ambos tokens

                setIsRefreshingToken(false);
                return data.access; // Retorna el nuevo token de acceso
            } else {
                console.error('Error al refrescar token:', data);
                setErrorMessage('Sesión expirada. Por favor, inicia sesión de nuevo.');
                onLogout(); // Cierra la sesión si el refresco falla (ej. token de refresco inválido)
                setIsRefreshingToken(false);
                return null;
            }
        } catch (error) {
            console.error('Error de red al refrescar token:', error);
            setErrorMessage('Error de red al intentar refrescar la sesión.');
            onLogout();
            setIsRefreshingToken(false);
            return null;
        }
    }, [DJANGO_API_BASE_URL, refreshToken, onLogout, setErrorMessage, isRefreshingToken]);


    // Función genérica para realizar peticiones autenticadas
    const makeAuthenticatedRequest = useCallback(async (url, options = {}) => {
        let currentAccessToken = localStorage.getItem('accessToken');
        let response = await fetch(url, {
            ...options,
            headers: {
                ...options.headers,
                'Authorization': `Bearer ${currentAccessToken}`,
            },
        });

        // Si el token expiró y la respuesta es 401 (Unauthorized)
        if (response.status === 401) {
            console.log('Token expirado, intentando refrescar...');
            const newAccessToken = await refreshAccessToken();
            if (newAccessToken) {
                // Reintenta la petición con el nuevo token
                currentAccessToken = newAccessToken; // Actualiza el token para el reintento
                response = await fetch(url, {
                    ...options,
                    headers: {
                        ...options.headers,
                        'Authorization': `Bearer ${currentAccessToken}`,
                    },
                });
            } else {
                // Si no se pudo refrescar el token, la sesión ha expirado
                throw new Error('Sesión expirada. Por favor, inicia sesión de nuevo.');
            }
        }

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Error al realizar la petición autenticada.');
        }

        return response;
    }, [refreshAccessToken]);


    // Efecto para obtener el perfil del usuario al cargar la página o al cambiar accessToken/refreshToken
    useEffect(() => {
        const fetchUserProfile = async () => {
            if (!accessToken) {
                setLoadingProfile(false);
                setErrorMessage("No hay token de acceso. Por favor, inicia sesión.");
                setCurrentPage('login');
                return;
            }

            setLoadingProfile(true);
            setErrorMessage('');

            try {
                console.log('Intentando obtener perfil de usuario...');
                const response = await makeAuthenticatedRequest(`${DJANGO_API_BASE_URL}/api/usuarios/profile/`);
                const data = await response.json();
                console.log('Perfil de usuario obtenido:', data);
                setUserProfile(data);
            } catch (error) {
                console.error('Error al obtener el perfil del usuario:', error);
                setErrorMessage(error.message || 'Error al cargar el perfil del usuario.');
                if (error.message.includes('Sesión expirada')) {
                     onLogout(); // Forzar cierre de sesión si el refresco falló
                }
            } finally {
                setLoadingProfile(false);
            }
        };

        fetchUserProfile();
    }, [accessToken, DJANGO_API_BASE_URL, setErrorMessage, setCurrentPage, makeAuthenticatedRequest, onLogout]); // Dependencias para re-ejecutar el efecto


    const renderContent = () => {
        if (loadingProfile) {
            return (
                <div className="flex justify-center items-center h-full text-gray-700">
                    <svg className="animate-spin h-8 w-8 text-blue-500 mr-3" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Cargando perfil y datos...
                </div>
            );
        }

        if (!userProfile) {
            return (
                <div className="flex justify-center items-center h-full text-red-500">
                    No se pudo cargar el perfil del usuario.
                </div>
            );
        }

        switch (currentPageContent) {
            case 'tasks':
                return <Tasks userId={userProfile.id} makeAuthenticatedRequest={makeAuthenticatedRequest} DJANGO_API_BASE_URL={DJANGO_API_BASE_URL} setErrorMessage={setErrorMessage} />;
            case 'goals':
                return <Goals userId={userProfile.id} makeAuthenticatedRequest={makeAuthenticatedRequest} DJANGO_API_BASE_URL={DJANGO_API_BASE_URL} setErrorMessage={setErrorMessage} />;
            case 'habits':
                return <Habits userId={userProfile.id} makeAuthenticatedRequest={makeAuthenticatedRequest} DJANGO_API_BASE_URL={DJANGO_API_BASE_URL} setErrorMessage={setErrorMessage} />;
            case 'rewards':
                return <Rewards userId={userProfile.id} makeAuthenticatedRequest={makeAuthenticatedRequest} DJANGO_API_BASE_URL={DJANGO_API_BASE_URL} setErrorMessage={setErrorMessage} />;
            case 'friends':
                return <Friends userId={userProfile.id} makeAuthenticatedRequest={makeAuthenticatedRequest} DJANGO_API_BASE_URL={DJANGO_API_BASE_URL} setErrorMessage={setErrorMessage} />;
            case 'leaderboard':
                return <Leaderboard userId={userProfile.id} makeAuthenticatedRequest={makeAuthenticatedRequest} DJANGO_API_BASE_URL={DJANGO_API_BASE_URL} setErrorMessage={setErrorMessage} />;
            case 'settings':
                return <Settings userId={userProfile.id} makeAuthenticatedRequest={makeAuthenticatedRequest} DJANGO_API_BASE_URL={DJANGO_API_BASE_URL} setErrorMessage={setErrorMessage} userProfile={userProfile} setUserProfile={setUserProfile} />;
            default:
                return <Tasks userId={userProfile.id} makeAuthenticatedRequest={makeAuthenticatedRequest} DJANGO_API_BASE_URL={DJANGO_API_BASE_URL} setErrorMessage={setErrorMessage} />;
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

                {userProfile && (
                    <UserProfile
                        userProfile={userProfile}
                        onLogout={onLogout}
                        makeAuthenticatedRequest={makeAuthenticatedRequest}
                        DJANGO_API_BASE_URL={DJANGO_API_BASE_URL}
                        setErrorMessage={setErrorMessage}
                    />
                )}

                <nav className="flex-grow">
                    <ul className="space-y-3">
                        {['tasks', 'goals', 'habits', 'rewards', 'friends', 'leaderboard', 'settings'].map((item) => (
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
