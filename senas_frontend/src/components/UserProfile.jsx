// src/components/UserProfile.jsx
import React, { useState } from 'react';

export default function UserProfile({ userProfile, onLogout, makeAuthenticatedRequest, DJANGO_API_BASE_URL, setErrorMessage, setUserProfile }) {
    const [isEditingAvatar, setIsEditingAvatar] = useState(false);
    const [selectedFile, setSelectedFile] = useState(null);
    const [previewUrl, setPreviewUrl] = useState(userProfile.avatar || null);
    const [uploading, setUploading] = useState(false);

    // Maneja la selección de un archivo de imagen
    const handleFileChange = (event) => {
        const file = event.target.files[0];
        if (file) {
            setSelectedFile(file);
            setPreviewUrl(URL.createObjectURL(file)); // Muestra una vista previa de la imagen
        } else {
            setSelectedFile(null);
            setPreviewUrl(userProfile.avatar || null);
        }
    };

    // Envía el nuevo avatar al backend de Django
    const handleAvatarUpload = async () => {
        if (!selectedFile) {
            setErrorMessage("Por favor, selecciona un archivo para subir.");
            return;
        }

        setUploading(true);
        setErrorMessage('');

        const formData = new FormData();
        formData.append('avatar', selectedFile);

        try {
            console.log('Intentando subir nuevo avatar...');
            const response = await makeAuthenticatedRequest(
                `${DJANGO_API_BASE_URL}/api/usuarios/mi-perfil/avatar/`,
                {
                    method: 'PUT', 
                    body: formData,
                    // No Content-Type header needed for FormData; browser sets it automatically
                }
            );

            const data = await response.json();
            if (response.ok) {
                console.log('Avatar actualizado exitosamente:', data);
                setUserProfile(prevProfile => ({ ...prevProfile, avatar: data.avatar }));
                setPreviewUrl(data.avatar); // Actualiza la URL de vista previa con la nueva URL del avatar
                setIsEditingAvatar(false); // Cierra el modo de edición
                setSelectedFile(null); // Limpia el archivo seleccionado
                setErrorMessage('');
            } else {
                console.error('Error al subir avatar:', data);
                setErrorMessage(data.avatar ? data.avatar[0] : (data.detail || 'Error al actualizar el avatar.'));
            }
        } catch (error) {
            console.error('Error de red al subir avatar:', error);
            setErrorMessage(error.message || 'Error de red al actualizar el avatar.');
        } finally {
            setUploading(false);
        }
    };

    return (
        <div className="flex flex-col items-center mb-8 p-4 bg-blue-800 rounded-lg shadow-inner">
            {/* Contenedor del Avatar */}
            <div className="relative mb-4 w-24 h-24 rounded-full overflow-hidden border-4 border-blue-300 shadow-xl group cursor-pointer"
                 onClick={() => setIsEditingAvatar(true)}>
                <img
                    src={previewUrl || `https://placehold.co/96x96/ADD8E6/FFFFFF?text=${userProfile.username ? userProfile.username.charAt(0).toUpperCase() : '?'}`}
                    alt="User Avatar"
                    className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-110"
                    onError={(e) => {
                        e.target.onerror = null; // Evita bucles infinitos
                        e.target.src = `https://placehold.co/96x96/ADD8E6/FFFFFF?text=${userProfile.username ? userProfile.username.charAt(0).toUpperCase() : '?'}`;
                    }}
                />
                <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                    <span className="text-white text-sm font-semibold">Editar</span>
                </div>
            </div>

            <h2 className="text-2xl font-bold text-white mb-1">{userProfile.username}</h2>
            <p className="text-blue-200 text-sm">Nivel: {userProfile.level} | XP: {userProfile.experience_points}</p>

            {/* Modal de edición de Avatar */}
            {isEditingAvatar && (
                <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
                    <div className="bg-white rounded-lg shadow-xl p-6 w-full max-w-md">
                        <h3 className="text-xl font-bold text-gray-800 mb-4">Actualizar Avatar</h3>
                        <div className="flex flex-col items-center mb-6">
                            <img
                                src={previewUrl || `https://placehold.co/128x128/ADD8E6/FFFFFF?text=${userProfile.username ? userProfile.username.charAt(0).toUpperCase() : '?'}`}
                                alt="Avatar Preview"
                                className="w-32 h-32 rounded-full object-cover mb-4 border-2 border-gray-300"
                            />
                            <input
                                type="file"
                                accept="image/*"
                                onChange={handleFileChange}
                                className="block w-full text-sm text-gray-500
                                           file:mr-4 file:py-2 file:px-4
                                           file:rounded-full file:border-0
                                           file:text-sm file:font-semibold
                                           file:bg-blue-50 file:text-blue-700
                                           hover:file:bg-blue-100"
                            />
                        </div>

                        <div className="flex justify-end space-x-3">
                            <button
                                onClick={() => {
                                    setIsEditingAvatar(false);
                                    setSelectedFile(null);
                                    setPreviewUrl(userProfile.avatar || null); // Restaura la URL original si cancela
                                }}
                                className="px-4 py-2 bg-gray-300 text-gray-800 rounded-lg hover:bg-gray-400 transition duration-150"
                            >
                                Cancelar
                            </button>
                            <button
                                onClick={handleAvatarUpload}
                                disabled={!selectedFile || uploading}
                                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition duration-150 flex items-center"
                            >
                                {uploading && (
                                    <svg className="animate-spin h-5 w-5 text-white mr-3" viewBox="0 0 24 24">
                                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                    </svg>
                                )}
                                {uploading ? 'Subiendo...' : 'Guardar Avatar'}
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
