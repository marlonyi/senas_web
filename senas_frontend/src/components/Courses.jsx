// src/components/Courses.jsx

import React, { useState, useEffect } from 'react';
// Importa íconos si los necesitas, por ejemplo:
// import { ArrowLeft, Book } from 'lucide-react';

export default function Courses({ setCurrentPage, DJANGO_API_BASE_URL, authToken, userId, setErrorMessage }) {
    const [courses, setCourses] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchCourses = async () => {
            if (!authToken) {
                setErrorMessage('No autorizado. Por favor, inicia sesión de nuevo.');
                setCurrentPage('login');
                setLoading(false);
                return;
            }

            try {
                // Endpoint para obtener cursos (ajusta la URL según tu backend de Django)
                const response = await fetch(`${DJANGO_API_BASE_URL}/api/cursos/`, {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${authToken}`, // Usa Bearer token para JWT
                    },
                });

                const data = await response.json();

                if (response.ok) {
                    setCourses(data);
                } else {
                    setError(data.detail || 'Error al cargar los cursos.');
                    console.error('Error al cargar cursos del backend:', data);
                    setErrorMessage(data.detail || 'No se pudieron cargar los cursos. Inténtalo de nuevo.');
                }
            } catch (err) {
                console.error('Error durante la solicitud de cursos:', err);
                setError('Error de conexión o del servidor. Inténtalo de nuevo.');
                setErrorMessage('Error de conexión o del servidor al cargar cursos.');
            } finally {
                setLoading(false);
            }
        };

        fetchCourses();
    }, [DJANGO_API_BASE_URL, authToken, setCurrentPage, setErrorMessage]); // Dependencias del useEffect

    return (
        <div className="flex flex-col items-center min-h-screen bg-gradient-to-br from-green-50 to-blue-100 p-4">
            <div className="bg-white p-8 rounded-2xl shadow-xl w-full max-w-4xl border border-gray-200 transform hover:scale-105 transition-transform duration-300 ease-in-out mt-10 mb-10">
                <div className="flex justify-between items-center mb-8">
                    <h2 className="text-4xl font-extrabold text-gray-900">Nuestros Cursos</h2>
                    <button
                        onClick={() => setCurrentPage('home')}
                        className="flex items-center bg-gray-200 text-gray-800 py-2 px-5 rounded-lg shadow-md hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-400 text-lg font-semibold transition duration-300 ease-in-out transform hover:scale-105"
                    >
                        {/* <ArrowLeft className="mr-2 h-5 w-5" /> */}
                        Volver al Inicio
                    </button>
                </div>

                {loading && (
                    <div className="flex justify-center items-center h-48">
                        <div className="animate-spin rounded-full h-16 w-16 border-t-4 border-b-4 border-blue-500"></div>
                        <p className="ml-4 text-xl text-gray-700">Cargando cursos...</p>
                    </div>
                )}

                {error && (
                    <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-6" role="alert">
                        <strong className="font-bold">Error:</strong>
                        <span className="block sm:inline"> {error}</span>
                    </div>
                )}

                {!loading && !error && courses.length === 0 && (
                    <div className="text-center py-10">
                        <p className="text-xl text-gray-600">No hay cursos disponibles en este momento.</p>
                    </div>
                )}

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                    {courses.map(course => (
                        <div key={course.id} className="bg-white border border-gray-200 rounded-xl shadow-lg p-6 flex flex-col items-start hover:shadow-xl transition-shadow duration-300 ease-in-out transform hover:-translate-y-1">
                            {/* <Book className="text-blue-500 mb-4 h-10 w-10" /> */}
                            <h3 className="text-2xl font-bold text-gray-900 mb-2">{course.nombre}</h3>
                            <p className="text-gray-700 text-base mb-4 flex-grow">{course.descripcion}</p>
                            <span className="text-sm font-semibold text-blue-600 bg-blue-50 px-3 py-1 rounded-full">{course.categoria}</span>
                            <div className="mt-4 w-full flex justify-end">
                                <button
                                    onClick={() => alert(`Inscribirse en: ${course.nombre}`)}
                                    className="bg-blue-600 text-white py-2 px-5 rounded-lg shadow-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 text-md font-bold transition duration-300 ease-in-out"
                                >
                                    Ver Detalles
                                </button>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
