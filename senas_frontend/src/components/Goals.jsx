// src/components/Goals.jsx
import React from 'react';

export default function Goals({ userId, makeAuthenticatedRequest, DJANGO_API_BASE_URL, setErrorMessage }) {
    return (
        <div className="p-4">
            <h3 className="text-2xl font-semibold text-gray-800 mb-4">Metas de Aprendizaje (Implementación Pendiente)</h3>
            <p className="text-gray-600">Aquí podrás establecer y seguir tus metas de aprendizaje.</p>
            <p className="text-gray-500 text-sm mt-2">ID de Usuario: {userId}</p>
            {/* Contenido futuro para metas */}
        </div>
    );
}
