// src/components/Register.jsx
import React, { useState } from 'react';

export default function Register({ DJANGO_API_BASE_URL, setCurrentPage, setErrorMessage }) {
    const [username, setUsername] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [loading, setLoading] = useState(false); // Estado para mostrar indicador de carga

    const handleRegister = async (e) => {
        e.preventDefault(); // Previene el comportamiento por defecto del formulario
        setLoading(true); // Activar el estado de carga
        setErrorMessage(''); // Limpiar cualquier mensaje de error previo

        if (password !== confirmPassword) {
            setErrorMessage('Las contraseñas no coinciden. Por favor, inténtalo de nuevo.');
            setLoading(false);
            return;
        }

        try {
            // Realiza la petición POST a tu endpoint de registro de Django
            const response = await fetch(`${DJANGO_API_BASE_URL}/api/usuarios/register/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    username: username, // Asegúrate de que Django espera 'username'
                    email: email, 
                    password: password,
                    // Si tu backend de registro requiere confirm_password, añádelo aquí
                    // confirm_password: confirmPassword,
                }),
            });

            const data = await response.json();

            if (response.ok) {
                // Si el registro es exitoso, puedes redirigir al usuario al login
                setErrorMessage('Registro exitoso. ¡Ahora puedes iniciar sesión!');
                setCurrentPage('login'); // Redirigir a la página de login
            } else {
                // Si hay errores, muestra los mensajes del backend
                // Los errores pueden venir en diferentes formatos, se intenta capturar los más comunes
                let errorDetails = 'Error desconocido al registrar. Revisa los datos.';
                if (data.email) {
                    errorDetails = `Email: ${data.email[0]}`;
                } else if (data.username) {
                    errorDetails = `Nombre de usuario: ${data.username[0]}`;
                } else if (data.password) {
                    errorDetails = `Contraseña: ${data.password[0]}`;
                } else if (data.detail) {
                    errorDetails = data.detail;
                }
                setErrorMessage(`Error de registro: ${errorDetails}`);
                console.error('Error de Django en Register:', data);
            }
        } catch (error) {
            // Errores de red o de conexión
            console.error('Error de red al intentar registrar:', error);
            setErrorMessage('Error de red. Asegúrate de que el backend de Django esté funcionando y accesible.');
        } finally {
            setLoading(false); // Desactivar el estado de carga
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-100 p-4">
            <div className="bg-white p-8 rounded-lg shadow-xl w-full max-w-md">
                <h2 className="text-3xl font-bold text-center text-gray-800 mb-8">Registrarse</h2>
                <form onSubmit={handleRegister} className="space-y-6">
                    <div>
                        <label htmlFor="username" className="block text-sm font-medium text-gray-700 mb-1">
                            Nombre de Usuario
                        </label>
                        <input
                            type="text"
                            id="username"
                            className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 transition duration-150 ease-in-out"
                            placeholder="tu_nombre_de_usuario"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            required
                        />
                    </div>
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
                    <div>
                        <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700 mb-1">
                            Confirmar Contraseña
                        </label>
                        <input
                            type="password"
                            id="confirmPassword"
                            className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 transition duration-150 ease-in-out"
                            placeholder="••••••••"
                            value={confirmPassword}
                            onChange={(e) => setConfirmPassword(e.target.value)}
                            required
                        />
                    </div>
                    <button
                        type="submit"
                        className="w-full bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 transition duration-150 ease-in-out flex items-center justify-center"
                        disabled={loading}
                    >
                        {loading ? (
                            <svg className="animate-spin h-5 w-5 text-white mr-3" viewBox="0 0 24 24">
                                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                            </svg>
                        ) : null}
                        {loading ? 'Registrando...' : 'Registrarse'}
                    </button>
                </form>
                <div className="mt-6 text-center">
                    <p className="text-sm text-gray-600">
                        ¿Ya tienes una cuenta?{' '}
                        <button
                            onClick={() => setCurrentPage('login')}
                            className="text-blue-600 hover:text-blue-800 font-medium transition duration-150 ease-in-out"
                        >
                            Inicia Sesión aquí
                        </button>
                    </p>
                </div>
            </div>
        </div>
    );
}
