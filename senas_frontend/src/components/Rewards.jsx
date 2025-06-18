// src/components/Rewards.jsx
import React from 'react';

export default function Rewards({ userId, makeAuthenticatedRequest, DJANGO_API_BASE_URL, setErrorMessage }) {
    return (
        <div className="p-4">
            <h3 className="text-2xl font-semibold text-gray-800 mb-4">Recompensas (Implementación Pendiente)</h3>
            <p className="text-gray-600">Aquí verás las recompensas que has ganado por tu progreso.</p>
            <p className="text-gray-500 text-sm mt-2">ID de Usuario: {userId}</p>
            {/* Contenido futuro para recompensas */}
        </div>
    );
}
