import React, { useEffect, useState } from 'react';
import { useUser } from '../context/UserContext';


export default function UserDetails({ DJANGO_API_BASE_URL, makeAuthenticatedRequest, setErrorMessage, accessToken }) {
    const [formData, setFormData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [successMessage, setSuccessMessage] = useState('');
    const [localErrorMessage, setLocalErrorMessage] = useState('');
    const { setUserData } = useUser();

    useEffect(() => {
        const fetchProfile = async () => {
            try {
                const response = await makeAuthenticatedRequest(`${DJANGO_API_BASE_URL}/api/usuarios/mi-perfil/`);
                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.detail || 'Error al obtener perfil.');
                }
                const data = await response.json();
                setFormData(data);
                setUserData(data);
            } catch (error) {
                setLocalErrorMessage(error.message || 'Error inesperado al obtener perfil.');
            } finally {
                setLoading(false);
            }
        };

        fetchProfile();
    }, [DJANGO_API_BASE_URL, makeAuthenticatedRequest, setUserData]);

    useEffect(() => {
        if (successMessage) {
            const timeout = setTimeout(() => setSuccessMessage(''), 4000);
            return () => clearTimeout(timeout);
        }
    }, [successMessage]);

    useEffect(() => {
        if (localErrorMessage) {
            const timeout = setTimeout(() => setLocalErrorMessage(''), 4000);
            return () => clearTimeout(timeout);
        }
    }, [localErrorMessage]);

    const handleChange = (e) => {
        const { name, value } = e.target;
        if (name.startsWith('preferencias_accesibilidad.')) {
            const prefKey = name.split('.')[1];
            setFormData((prev) => ({
                ...prev,
                preferencias_accesibilidad: {
                    ...prev.preferencias_accesibilidad,
                    [prefKey]: value,
                },
            }));
        } else {
            setFormData((prev) => ({ ...prev, [name]: value }));
        }
    };

    const handleCheckbox = (e) => {
        const { name, checked } = e.target;
        const prefKey = name.split('.')[1];
        setFormData((prev) => ({
            ...prev,
            preferencias_accesibilidad: {
                ...prev.preferencias_accesibilidad,
                [prefKey]: checked,
            },
        }));
    };

    const handleAvatarUpload = async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        const formDataToSend = new FormData();
        formDataToSend.append('avatar', file);

        try {
            const response = await fetch(`${DJANGO_API_BASE_URL}/api/usuarios/mi-perfil/avatar/`, {
                method: 'PUT',
                headers: {
                    Authorization: `Bearer ${accessToken}`,
                },
                body: formDataToSend,
            });

            const data = await response.json();

            if (response.ok) {
                setFormData((prev) => ({ ...prev, avatar: data.avatar }));
                setUserData((prev) => ({ ...prev, avatar: data.avatar }));
                setSuccessMessage('Avatar actualizado correctamente.');
            } else {
                setLocalErrorMessage(data.detail || 'Error al actualizar avatar.');
            }
        } catch (error) {
            setLocalErrorMessage('Error de red al subir avatar.');
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setSaving(true);
        setLocalErrorMessage('');
        setSuccessMessage('');

        try {
            const dataToSend = { ...formData };
            const response = await fetch(`${DJANGO_API_BASE_URL}/api/usuarios/mi-perfil/`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${accessToken}`,
                },
                body: JSON.stringify(dataToSend),
            });

            const data = await response.json();
            if (!response.ok) {
                setLocalErrorMessage(data.detail || 'Error al actualizar perfil.');
            } else {
                setFormData(data);
                setUserData(data);
                setSuccessMessage('Perfil actualizado exitosamente.');
            }
        } catch (error) {
            setLocalErrorMessage('Error de red al actualizar perfil.');
        } finally {
            setSaving(false);
        }
    };

    if (loading) return <p className="text-center text-blue-600">Cargando perfil...</p>;
    if (!formData) return null;

    return (
        <form onSubmit={handleSubmit} className="max-w-2xl mx-auto p-6 bg-white rounded-lg shadow-md">
            <h2 className="text-2xl font-bold mb-6 text-blue-700">Mi Perfil</h2>

            {successMessage && (
                <div className="mb-4 p-3 bg-green-100 text-green-700 rounded fade-in-out">
                    {successMessage}
                </div>
            )}
            {localErrorMessage && (
                <div className="mb-4 p-3 bg-red-100 text-red-700 rounded fade-in-out">
                    {localErrorMessage}
                </div>
            )}

            <div className="mb-4">
                <label className="block font-medium mb-1">Avatar</label>
                <input type="file" onChange={handleAvatarUpload} className="input" />
                {formData.avatar && <img src={formData.avatar} alt="Avatar" className="mt-2 h-20 w-20 rounded-full" />}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                    <label className="block mb-1 font-medium">Nombre</label>
                    <input name="first_name" value={formData.first_name || ''} onChange={handleChange} className="input" />
                </div>
                <div>
                    <label className="block mb-1 font-medium">Apellido</label>
                    <input name="last_name" value={formData.last_name || ''} onChange={handleChange} className="input" />
                </div>
                <div>
                    <label className="block mb-1 font-medium">Correo Electrónico</label>
                    <input name="email" type="email" value={formData.email || ''} onChange={handleChange} className="input" />
                </div>
                <div>
                    <label className="block mb-1 font-medium">Teléfono</label>
                    <input name="telefono" value={formData.telefono || ''} onChange={handleChange} className="input" />
                </div>
                <div className="md:col-span-2">
                    <label className="block mb-1 font-medium">Biografía</label>
                    <textarea name="biografia" value={formData.biografia || ''} onChange={handleChange} className="input" rows={2} />
                </div>
                <div>
                    <label className="block mb-1 font-medium">Ciudad</label>
                    <input name="ciudad" value={formData.ciudad || ''} onChange={handleChange} className="input" />
                </div>
                <div>
                    <label className="block mb-1 font-medium">País</label>
                    <input name="pais" value={formData.pais || ''} onChange={handleChange} className="input" />
                </div>
                <div>
                    <label className="block mb-1 font-medium">Idioma Preferido</label>
                    <select name="idioma_preferido" value={formData.idioma_preferido || ''} onChange={handleChange} className="input">
                        <option value="es-co">Español (Colombia)</option>
                        <option value="es">Español (General)</option>
                        <option value="en">English</option>
                    </select>
                </div>
                <div>
                    <label className="block mb-1 font-medium">Nivel Educativo</label>
                    <select name="nivel_educativo" value={formData.nivel_educativo || ''} onChange={handleChange} className="input">
                        <option value="">Selecciona uno</option>
                        <option value="primaria">Primaria</option>
                        <option value="secundaria">Secundaria</option>
                        <option value="tecnico">Técnico</option>
                        <option value="universitario">Universitario</option>
                        <option value="posgrado">Posgrado</option>
                        <option value="otro">Otro</option>
                    </select>
                </div>
                <div>
                    <label className="block mb-1 font-medium">Ocupación</label>
                    <input name="ocupacion" value={formData.ocupacion || ''} onChange={handleChange} className="input" />
                </div>
            </div>

            <h3 className="text-xl font-semibold mt-6 mb-2 text-blue-600">Preferencias de Accesibilidad</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                    <label className="block mb-1 font-medium">Tamaño de Fuente</label>
                    <select name="preferencias_accesibilidad.tamano_fuente" value={formData.preferencias_accesibilidad?.tamano_fuente || ''} onChange={handleChange} className="input">
                        <option value="pequeño">Pequeño</option>
                        <option value="mediano">Mediano</option>
                        <option value="grande">Grande</option>
                    </select>
                </div>
                <div className="flex items-center space-x-2 mt-6">
                    <input
                        type="checkbox"
                        name="preferencias_accesibilidad.transcripciones_activas"
                        checked={formData.preferencias_accesibilidad?.transcripciones_activas || false}
                        onChange={handleCheckbox}
                        className="h-4 w-4 text-blue-600"
                    />
                    <label className="text-sm">Activar transcripciones</label>
                </div>
                <div className="flex items-center space-x-2">
                    <input
                        type="checkbox"
                        name="preferencias_accesibilidad.contraste_alto"
                        checked={formData.preferencias_accesibilidad?.contraste_alto || false}
                        onChange={handleCheckbox}
                        className="h-4 w-4 text-blue-600"
                    />
                    <label className="text-sm">Usar alto contraste</label>
                </div>
            </div>

            <div className="mt-6 text-right">
                <button
                    type="submit"
                    disabled={saving}
                    className="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
                >
                    {saving ? 'Guardando...' : 'Guardar Cambios'}
                </button>
            </div>
        </form>
    );
}
