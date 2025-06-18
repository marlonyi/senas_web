// senas_frontend/src/components/Register.jsx

import React, { useState } from 'react';

function Register({ setRenderPage }) { // Asegúrate de que setRenderPage se recibe como prop
    // Estado para almacenar los datos del formulario de registro
    const [formData, setFormData] = useState({
        username: '',
        email: '',
        password: '',
        password2: '', // Confirmación de contraseña
        first_name: '',
        last_name: ''
    });

    // Estado para manejar mensajes de error o éxito
    const [message, setMessage] = useState('');
    // Estado para controlar el estado de carga (mientras se envía la solicitud)
    const [loading, setLoading] = useState(false);

    // URL base de tu API de Django
    // ASEGÚRATE DE QUE ESTA URL ES CORRECTA PARA TU BACKEND
    const DJANGO_API_BASE_URL = "http://127.0.0.1:8000";

    // Maneja los cambios en los campos del formulario
    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    // Maneja el envío del formulario de registro
    const handleRegister = async (e) => {
        // MUY IMPORTANTE: Asegúrate de que esta línea es la primera en la función
        // para prevenir el envío por defecto del formulario.
        e.preventDefault(); 
        console.log("¡e.preventDefault() llamado!"); // Añade este log para confirmar que se ejecuta.

        setMessage(''); // Limpia mensajes anteriores
        setLoading(true); // Activa el estado de carga

        // Validaciones básicas del lado del cliente
        if (formData.password !== formData.password2) {
            setMessage('Las contraseñas no coinciden.');
            setLoading(false);
            return;
        }

        // Prepara los datos para enviar al backend
        const userData = {
            username: formData.username,
            email: formData.email,
            password: formData.password,
            // Asegúrate de que tu serializador de Django espera 'password2'
            password2: formData.password2, // Asegúrate de enviar password2 aquí
            first_name: formData.first_name,
            last_name: formData.last_name,
        };

        console.log("Enviando datos al backend:", JSON.stringify(userData, null, 2));

        try {
            // VERIFICA ESTA LÍNEA CUIDADOSAMENTE POR CUALQUIER ERROR DE SINTAXIS
            const response = await fetch(`${DJANGO_API_BASE_URL}/api/usuarios/register/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(userData), // Convierte el objeto JavaScript a una cadena JSON
            });

            if (response.ok) {
                const data = await response.json();
                console.log("Registro exitoso:", data);
                setMessage('Registro exitoso. ¡Ahora puedes iniciar sesión!');
                // Mueve setRenderPage AQUÍ, después de que la respuesta sea OK
                setRenderPage('login'); 
            } else {
                const errorData = await response.json();
                console.error("Error en el registro:", errorData);
                // Muestra un mensaje de error más específico del backend si está disponible
                setMessage(`Error al registrarse: ${errorData.detail || JSON.stringify(errorData)}`);
            }
        } catch (error) {
            console.error("Error de red al intentar registrarse:", error);
            setMessage(`Error al registrarse: Falló la conexión al servidor. (${error.message})`);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100 p-4">
            <div className="bg-white p-8 rounded-lg shadow-md w-full max-w-md">
                <h2 className="text-2xl font-bold text-center mb-6 text-gray-800">Registro</h2>
                {/* VERIFICA EL onSUBMIT DE ESTE FORMULARIO */}
                <form onSubmit={handleRegister} className="space-y-4"> 
                    <div>
                        <label htmlFor="username" className="block text-sm font-medium text-gray-700">Usuario</label>
                        <input
                            type="text"
                            id="username"
                            name="username"
                            value={formData.username}
                            onChange={handleChange}
                            required
                            className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                        />
                    </div>
                    <div>
                        <label htmlFor="email" className="block text-sm font-medium text-gray-700">Email</label>
                        <input
                            type="email"
                            id="email"
                            name="email"
                            value={formData.email}
                            onChange={handleChange}
                            required
                            className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                        />
                    </div>
                    <div>
                        <label htmlFor="first_name" className="block text-sm font-medium text-gray-700">Nombre</label>
                        <input
                            type="text"
                            id="first_name"
                            name="first_name"
                            value={formData.first_name}
                            onChange={handleChange}
                            className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                        />
                    </div>
                    <div>
                        <label htmlFor="last_name" className="block text-sm font-medium text-gray-700">Apellido</label>
                        <input
                            type="text"
                            id="last_name"
                            name="last_name"
                            value={formData.last_name}
                            onChange={handleChange}
                            className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                        />
                    </div>
                    <div>
                        <label htmlFor="password" className="block text-sm font-medium text-gray-700">Contraseña</label>
                        <input
                            type="password"
                            id="password"
                            name="password"
                            value={formData.password}
                            onChange={handleChange}
                            required
                            className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                        />
                    </div>
                    <div>
                        <label htmlFor="password2" className="block text-sm font-medium text-gray-700">Confirmar Contraseña</label>
                        <input
                            type="password"
                            id="password2"
                            name="password2"
                            value={formData.password2}
                            onChange={handleChange}
                            required
                            className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                        />
                    </div>
                    <button
                        type="submit"
                        disabled={loading} // Deshabilita el botón mientras se carga
                        className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
                    >
                        {loading ? 'Registrando...' : 'Registrarse'}
                    </button>
                </form>
                {message && (
                    <p className={`mt-4 text-center ${message.includes('Error') ? 'text-red-600' : 'text-green-600'}`}>
                        {message}
                    </p>
                )}
                <p className="mt-4 text-center text-sm text-gray-600">
                    ¿Ya tienes una cuenta?{' '}
                    <span
                        onClick={() => setRenderPage('login')}
                        className="font-medium text-blue-600 hover:text-blue-500 cursor-pointer"
                    >
                        Inicia Sesión aquí
                    </span>
                </p>
            </div>
        </div>
    );
}

export default Register;
