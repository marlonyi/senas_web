// src/components/Login.jsx

import React, { useState } from 'react';

export default function Login({ DJANGO_API_BASE_URL, onLoginSuccess, setErrorMessage, setCurrentPage }) {
    // CAMBIO CLAVE: Usar 'username' en lugar de 'email' para el campo de login
    const [username, setUsername] = useState(''); 
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);

    const handleLogin = async (e) => {
        e.preventDefault(); 
        setLoading(true); 
        setErrorMessage(''); 

        try {
            const response = await fetch(`${DJANGO_API_BASE_URL}/api/token/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                // CAMBIO CLAVE: Enviar 'username' en lugar de 'email'
                body: JSON.stringify({ username, password }), 
            });

            const data = await response.json();

            if (response.ok) {
                const accessToken = data.access;
                const refreshToken = data.refresh;
                onLoginSuccess(accessToken, refreshToken);
            } else {
                const errorMsg = data.detail || (data.username && data.username[0]) || (data.password && data.password[0]) || 'Error desconocido al iniciar sesión.';
                setErrorMessage(`Error de inicio de sesión: ${errorMsg}`);
                console.error('Error de Django en Login:', data);
            }
        } catch (error) {
            console.error('Error de red al intentar iniciar sesión:', error);
            setErrorMessage('Error de red. Asegúrate de que el backend de Django esté funcionando y accesible.');
        } finally {
            setLoading(false); 
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-100 p-4">
            <div className="bg-white p-8 rounded-lg shadow-xl w-full max-w-md">
                <h2 className="text-3xl font-bold text-center text-gray-800 mb-8">Iniciar Sesión</h2>
                <form onSubmit={handleLogin} className="space-y-6">
                    <div>
                        <label htmlFor="username" className="block text-sm font-medium text-gray-700 mb-1">
                            Nombre de Usuario
                        </label>
                        <input
                            type="text" // Cambiado a 'text' para username
                            id="username"
                            className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 transition duration-150 ease-in-out"
                            placeholder="tu_nombre_de_usuario" // Placeholder ajustado
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            required
                        />
                    </div>
                    <div>
                        <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
                            Contraseña
                        </label>
                        <input
                            type="password"
                            id="password"
                            className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 transition duration-150 ease-in-out"
                            placeholder="••••••••"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                        />
                    </div>
                    <button
                        type="submit"
                        className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition duration-150 ease-in-out flex items-center justify-center"
                        disabled={loading} 
                    >
                        {loading ? (
                            <svg className="animate-spin h-5 w-5 text-white mr-3" viewBox="0 0 24 24">
                                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                            </svg>
                        ) : null}
                        {loading ? 'Iniciando Sesión...' : 'Iniciar Sesión'}
                    </button>
                </form>
                <div className="mt-6 text-center">
                    <p className="text-sm text-gray-600">
                        ¿No tienes una cuenta?{' '}
                        <button
                            onClick={() => setCurrentPage('register')}
                            className="text-blue-600 hover:text-blue-800 font-medium transition duration-150 ease-in-out"
                        >
                            Regístrate aquí
                        </button>
                    </p>
                </div>
            </div>
        </div>
    );
}
