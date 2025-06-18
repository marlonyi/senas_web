// src/App.jsx
import React, { useState, useEffect } from 'react';

// Importa tus componentes de página (SIN Firebase)
import Login from './components/Login.jsx';
import Register from './components/Register.jsx';
import Home from './components/Home.jsx';
import Courses from './components/Courses.jsx';
import WelcomeScreen from './components/WelcomeScreen.jsx'; // Asegúrate de tener este componente

// URL base de tu backend Django - APUNTA A TU SERVIDOR LOCAL DURANTE EL DESARROLLO
const DJANGO_API_BASE_URL = "http://127.0.0.1:8000"; 

export default function App() {
    // Estados principales de la aplicación
    const [currentPage, setCurrentPage] = useState('welcome'); // Página actual que se muestra
    const [userId, setUserId] = useState(null); // ID del usuario autenticado (desde Django)
    const [userEmail, setUserEmail] = useState(null); // Email del usuario autenticado (desde Django)
    const [authToken, setAuthToken] = useState(localStorage.getItem('authToken')); // Token de acceso JWT de Django
    const [refreshToken, setRefreshToken] = useState(localStorage.getItem('refreshToken')); // Token de refresco JWT de Django
    const [errorMessage, setErrorMessage] = useState(''); // Mensajes de error para mostrar al usuario
    
    // El estado de 'user' ahora almacenará los datos completos del perfil de Django
    const [user, setUser] = useState(null); 

    // Función para obtener los detalles del perfil del usuario desde Django (segundo paso del login)
    // Se llama después de obtener los tokens para conseguir el ID y Email del usuario.
    const fetchUserProfile = async (token) => {
        try {
            const response = await fetch(`${DJANGO_API_BASE_URL}/api/usuarios/mi-perfil/`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`, // Envía el token JWT en el encabezado Authorization
                },
            });

            if (!response.ok) {
                const errorData = await response.json();
                console.error('Error al obtener perfil de usuario:', errorData);
                setErrorMessage(`Error al cargar perfil: ${errorData.detail || response.statusText}. Por favor, vuelve a iniciar sesión.`);
                return null;
            }

            const profileData = await response.json();
            // Accede a los campos según la estructura que tu MiPerfilSerializer devuelve.
            // Asegúrate de que 'id', 'email', 'username', 'first_name', 'last_name' existan en la respuesta de tu backend.
            return {
                uid: profileData.id, // Usamos el ID de Django como 'uid' para mantener consistencia si venía de Firebase
                id: profileData.id,
                email: profileData.email,
                username: profileData.username,
                first_name: profileData.first_name,
                last_name: profileData.last_name,
                // Puedes añadir más campos del perfil aquí
            };
        } catch (error) {
            console.error('Error de conexión al obtener perfil:', error);
            setErrorMessage('Error de red al obtener el perfil. Revisa tu conexión con el backend.');
            return null;
        }
    };

    // Función para manejar el cierre de sesión
    const handleLogout = async () => {
        if (authToken && refreshToken) {
            try {
                const response = await fetch(`${DJANGO_API_BASE_URL}/api/usuarios/logout/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${authToken}`, // Autentica la petición de logout
                    },
                    body: JSON.stringify({ refresh_token: refreshToken }), // Envía el refresh token para invalidarlo
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
        setUserId(null);
        setUserEmail(null);
        setUser(null); // Limpiar el objeto de usuario completo
        localStorage.removeItem('authToken');
        localStorage.removeItem('refreshToken');
        localStorage.removeItem('userId');
        localStorage.removeItem('userEmail');
        setCurrentPage('welcome'); // Redirigir a la pantalla de bienvenida después del logout
    };

    // Función que se llama desde Login.jsx al tener éxito la obtención inicial de tokens
    const handleLoginSuccess = async (accessToken, newRefreshToken) => {
        setAuthToken(accessToken);
        setRefreshToken(newRefreshToken);
        localStorage.setItem('authToken', accessToken);
        localStorage.setItem('refreshToken', newRefreshToken);

        // Ahora, fetchUserProfile obtendrá todos los datos del perfil de Django
        const userProfile = await fetchUserProfile(accessToken);
        if (userProfile) {
            setUserId(userProfile.id);
            setUserEmail(userProfile.email);
            setUser(userProfile); // Almacena el objeto de perfil completo
            localStorage.setItem('userId', userProfile.id);
            localStorage.setItem('userEmail', userProfile.email);
            setErrorMessage(''); 
            setCurrentPage('home'); // Navegar a la página de inicio al completar el login y cargar perfil
        } else {
            // Si el perfil no se pudo obtener, forzar un cierre de sesión para evitar un estado inconsistente
            handleLogout(); 
        }
    };

    // Efecto que se ejecuta una vez al montar el componente para cargar estado desde localStorage
    useEffect(() => {
        const storedAuthToken = localStorage.getItem('authToken');
        const storedRefreshToken = localStorage.getItem('refreshToken');
        const storedUserId = localStorage.getItem('userId');
        const storedUserEmail = localStorage.getItem('userEmail');

        if (storedAuthToken && storedRefreshToken && storedUserId && storedUserEmail) {
            setAuthToken(storedAuthToken);
            setRefreshToken(storedRefreshToken);
            setUserId(storedUserId);
            setUserEmail(storedUserEmail);
            // Intentar recuperar el perfil completo si hay tokens, para asegurar el objeto 'user'
            const recoverUserProfile = async () => {
                const profile = await fetchUserProfile(storedAuthToken);
                if (profile) {
                    setUser(profile);
                    setCurrentPage('home'); // Ir a home si el perfil se recupera
                } else {
                    handleLogout(); // Si no se puede recuperar, cerrar sesión
                }
            };
            recoverUserProfile();
        } else {
            setCurrentPage('welcome'); // De lo contrario, ir a la pantalla de bienvenida
        }
    }, []); // El array de dependencias vacío asegura que este efecto se ejecute solo una vez al montar

    // Renderizado condicional de componentes según el estado 'currentPage'
    let pageComponent;
    switch (currentPage) {
        case 'welcome':
            pageComponent = <WelcomeScreen setCurrentPage={setCurrentPage} />;
            break;
        case 'login':
            pageComponent = <Login 
                                DJANGO_API_BASE_URL={DJANGO_API_BASE_URL} 
                                onLoginSuccess={handleLoginSuccess} 
                                setErrorMessage={setErrorMessage} 
                                // Ya no se pasan props de Firebase
                            />;
            break;
        case 'register':
            pageComponent = <Register 
                                DJANGO_API_BASE_URL={DJANGO_API_BASE_URL} 
                                setCurrentPage={setCurrentPage} 
                                setErrorMessage={setErrorMessage} 
                                // Ya no se pasan props de Firebase
                            />;
            break;
        case 'home':
            // Asegúrate que haya datos de usuario completos y un token para mostrar Home
            if (user && authToken) {
                return <Home 
                            user={user} // Pasar el objeto de usuario completo
                            setCurrentPage={setCurrentPage} 
                            handleLogout={handleLogout} 
                        />;
            } else {
                setCurrentPage('login'); // Si no hay datos, redirigir al Login
                setErrorMessage('Por favor, inicia sesión para acceder al inicio.');
                pageComponent = null; // No renderizar nada hasta la redirección
            }
            break;
        case 'courses':
            // Asegúrate que haya datos de usuario y un token para acceder a los cursos
            if (user && authToken) {
                return <Courses 
                            DJANGO_API_BASE_URL={DJANGO_API_BASE_URL} 
                            authToken={authToken} // Se sigue usando authToken para la petición
                            userId={user.id} // Pasar el ID del usuario desde el objeto 'user'
                            setCurrentPage={setCurrentPage} 
                            setErrorMessage={setErrorMessage}
                        />;
            } else {
                setCurrentPage('login'); 
                setErrorMessage('Por favor, inicia sesión para acceder a los cursos.');
                pageComponent = null;
            }
            break;
        default:
            pageComponent = <WelcomeScreen setCurrentPage={setCurrentPage} />;
            break;
    }

    return (
        <div className="app-container">
            {errorMessage && (
                <div className="absolute top-0 left-0 right-0 bg-red-500 text-white p-3 text-center text-lg z-50 animate-fade-in-down">
                    {errorMessage}
                </div>
            )}
            {pageComponent} 
        </div>
    );
}
