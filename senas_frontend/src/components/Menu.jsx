// src/components/Menu.jsx
import React from 'react';

export default function Menu({ setCurrentPage, onLogout, user }) {
    return (
        <div className="bg-blue-800 text-white h-full w-full md:w-64 flex flex-col p-4 shadow-lg">
            <h2 className="text-2xl font-bold mb-6 text-center">Mi Menú</h2>

            <nav className="flex flex-col space-y-4">
                <button
                    onClick={() => setCurrentPage('home')}
                    className="text-left px-4 py-2 rounded hover:bg-blue-700 transition"
                >
                    Inicio
                </button>

                <button
                    onClick={() => setCurrentPage('perfil')}
                    className="text-left px-4 py-2 rounded hover:bg-blue-700 transition"
                >
                    Mi Perfil
                </button>

                <button
                    onClick={() => setCurrentPage('courses')}
                    className="text-left px-4 py-2 rounded hover:bg-blue-700 transition"
                >
                    Cursos
                </button>

                <button
                    onClick={() => setCurrentPage('tareas')}
                    className="text-left px-4 py-2 rounded hover:bg-blue-700 transition"
                >
                    Tareas
                </button>

                <button
                    onClick={() => setCurrentPage('recompensas')}
                    className="text-left px-4 py-2 rounded hover:bg-blue-700 transition"
                >
                    Recompensas
                </button>

                <button
                    onClick={() => setCurrentPage('configuracion')}
                    className="text-left px-4 py-2 rounded hover:bg-blue-700 transition"
                >
                    Configuración
                </button>

                <div className="border-t border-blue-500 my-4"></div>

                <button
                    onClick={onLogout}
                    className="text-left px-4 py-2 bg-red-600 hover:bg-red-700 rounded transition"
                >
                    Cerrar sesión
                </button>
            </nav>

            {user && (
                <div className="mt-auto text-sm text-center text-blue-200 pt-4">
                    Sesion iniciada como: <br /><strong>{user.username}</strong>
                </div>
            )}
        </div>
    );
}
