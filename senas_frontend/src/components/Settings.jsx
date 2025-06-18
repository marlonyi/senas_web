// src/components/Settings.jsx
import React from 'react';

export default function Settings({ userId, makeAuthenticatedRequest, DJANGO_API_BASE_URL, setErrorMessage, userProfile, setUserProfile }) {
    return (
        <div className="p-4">
            <h3 className="text-2xl font-semibold text-gray-800 mb-4">Configuración (Implementación Pendiente)</h3>
            <p className="text-gray-600">Ajusta tus preferencias de la aplicación y perfil.</p>
            <p className="text-gray-500 text-sm mt-2">ID de Usuario: {userId}</p>
            {/* Contenido futuro para configuración */}
        </div>
    );
}
