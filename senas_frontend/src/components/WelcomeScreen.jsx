// src/components/WelcomeScreen.jsx
import React from 'react';

export default function WelcomeScreen({ setCurrentPage }) {
    return (
        <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-400 to-purple-600 p-4">
            <div className="bg-white p-10 rounded-2xl shadow-2xl w-full max-w-lg text-center transform hover:scale-105 transition-transform duration-300 ease-in-out">
                <h1 className="text-5xl font-extrabold text-gray-900 mb-6 leading-tight">
                    ¡Bienvenido a <span className="text-purple-700">Señas App!</span>
                </h1>
                <p className="text-xl text-gray-700 mb-10 leading-relaxed">
                    Tu camino hacia la comunicación inclusiva empieza aquí. Aprende Lenguaje de Señas de forma interactiva y divertida.
                </p>
                <div className="space-y-4">
                    <button
                        onClick={() => setCurrentPage('login')}
                        className="w-full bg-blue-600 text-white py-3 px-6 rounded-lg shadow-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 text-xl font-bold transition duration-300 ease-in-out transform hover:scale-105"
                    >
                        Iniciar Sesión
                    </button>
                    <button
                        onClick={() => setCurrentPage('register')}
                        className="w-full bg-purple-600 text-white py-3 px-6 rounded-lg shadow-lg hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500 text-xl font-bold transition duration-300 ease-in-out transform hover:scale-105"
                    >
                        Registrarse
                    </button>
                </div>
            </div>
        </div>
    );
}
