// src/components/Login.jsx
import React, { useState } from 'react';

export default function Login({ DJANGO_API_BASE_URL, onLoginSuccess, setErrorMessage, setCurrentPage }) {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false); // Estado para mostrar indicador de carga

    const handleLogin = async (e) => {
        e.preventDefault(); // Previene el comportamiento por defecto del formulario (recargar la página)
        setLoading(true); // Activar el estado de carga
        setErrorMessage(''); // Limpiar cualquier mensaje de error previo

        try {
            // Realiza la petición POST a tu endpoint de login de Django
            const response = await fetch(`${DJANGO_API_BASE_URL}/api/token/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email, password }), // Envía email y contraseña
            });

            const data = await response.json();

            if (response.ok) {
                // Si la respuesta es exitosa (código 200), extrae los tokens
                const accessToken = data.access;
                const refreshToken = data.refresh;
                
                // Llama a la función de éxito que se pasa desde App.jsx
                // Esta función se encargará de guardar los tokens y obtener el perfil de usuario
                onLoginSuccess(accessToken, refreshToken);
                // No se necesita setCurrentPage aquí ya que onLoginSuccess lo maneja al obtener el perfil
            } else {
                // Si la respuesta no es exitosa, muestra el mensaje de error del backend
                // Los errores pueden estar en data.detail o en otros campos específicos de validación
                const errorMsg = data.detail || (data.email && data.email[0]) || (data.password && data.password[0]) || 'Error desconocido al iniciar sesión.';
                setErrorMessage(`Error de inicio de sesión: ${errorMsg}`);
                console.error('Error de Django en Login:', data);
            }
        } catch (error) {
            // Errores de red o de conexión
            console.error('Error de red al intentar iniciar sesión:', error);
            setErrorMessage('Error de red. Asegúrate de que el backend de Django esté funcionando y accesible.');
        } finally {
            setLoading(false); // Desactivar el estado de carga
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-100 p-4">
            <div className="bg-white p-8 rounded-lg shadow-xl w-full max-w-md">
                <h2 className="text-3xl font-bold text-center text-gray-800 mb-8">Iniciar Sesión</h2>
                <form onSubmit={handleLogin} className="space-y-6">
                    <div>
                        <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
                            Correo Electrónico
                        </label>
                        <input
                            type="email"
                            id="email"
                            className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 transition duration-150 ease-in-out"
                            placeholder="tu@ejemplo.com"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
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
                        disabled={loading} // Deshabilita el botón mientras se carga
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
