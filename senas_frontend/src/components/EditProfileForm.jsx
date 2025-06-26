import React, { useState, useRef } from 'react';

export default function EditProfileForm({
  userProfile,
  makeAuthenticatedRequest,
  DJANGO_API_BASE_URL,
  setErrorMessage,
  setUserProfile
}) {
  const [formData, setFormData] = useState({
    username: userProfile.username || '',
    email: userProfile.email || '',
    first_name: userProfile.first_name || '',
    last_name: userProfile.last_name || '',
    avatar: userProfile.avatar || '',
  });
  const [successMessage, setSuccessMessage] = useState('');
  const [saving, setSaving] = useState(false);
  const fileInputRef = useRef();

  const handleChange = (e) => {
    setFormData(prev => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleAvatarUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const formDataUpload = new FormData();
    formDataUpload.append('avatar', file);

    try {
      const response = await makeAuthenticatedRequest(`${DJANGO_API_BASE_URL}/api/usuarios/mi-perfil/`, {
        method: 'PATCH',
        body: formDataUpload
      });

      const updatedUser = await response.json();
      setFormData(prev => ({ ...prev, avatar: updatedUser.avatar }));
      setUserProfile(updatedUser);
      setSuccessMessage('Avatar actualizado exitosamente.');
    } catch (error) {
      console.error('Error al subir avatar:', error);
      setErrorMessage('Error al subir el avatar. Asegúrate de que sea una imagen válida.');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setErrorMessage('');
    setSuccessMessage('');

    try {
      const response = await makeAuthenticatedRequest(`${DJANGO_API_BASE_URL}/api/usuarios/mi-perfil/`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      });

      const updatedUser = await response.json();
      setUserProfile(updatedUser);
      setSuccessMessage('Perfil actualizado exitosamente.');
    } catch (error) {
      console.error('Error al actualizar perfil:', error);
      setErrorMessage('Error al guardar los cambios. Verifica los campos.');
    }

    setSaving(false);
  };

  return (
    <form onSubmit={handleSubmit} className="max-w-xl mx-auto bg-white p-6 rounded-xl shadow-md space-y-5">
      <h2 className="text-2xl font-bold text-gray-800 mb-4">Editar Perfil</h2>

      {successMessage && (
        <div className="bg-green-100 text-green-800 p-3 rounded-lg">{successMessage}</div>
      )}
      {saving && (
        <div className="text-sm text-blue-500">Guardando cambios...</div>
      )}

      <div>
        <label className="block text-sm font-medium text-gray-700">Username</label>
        <input type="text" name="username" value={formData.username} onChange={handleChange}
          className="mt-1 w-full rounded-lg border-gray-300 shadow-sm focus:ring-blue-500 focus:border-blue-500" />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">Email</label>
        <input type="email" name="email" value={formData.email} onChange={handleChange}
          className="mt-1 w-full rounded-lg border-gray-300 shadow-sm focus:ring-blue-500 focus:border-blue-500" />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">Nombre</label>
        <input type="text" name="first_name" value={formData.first_name} onChange={handleChange}
          className="mt-1 w-full rounded-lg border-gray-300 shadow-sm focus:ring-blue-500 focus:border-blue-500" />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">Apellido</label>
        <input type="text" name="last_name" value={formData.last_name} onChange={handleChange}
          className="mt-1 w-full rounded-lg border-gray-300 shadow-sm focus:ring-blue-500 focus:border-blue-500" />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">Avatar (URL)</label>
        <input type="text" name="avatar" value={formData.avatar} onChange={handleChange}
          className="mt-1 w-full rounded-lg border-gray-300 shadow-sm focus:ring-blue-500 focus:border-blue-500" />
        {formData.avatar && (
          <img src={formData.avatar} alt="Avatar preview" className="mt-2 h-20 w-20 rounded-full object-cover shadow-md" />
        )}
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">Subir nuevo avatar</label>
        <input
          type="file"
          accept="image/*"
          ref={fileInputRef}
          onChange={handleAvatarUpload}
          className="mt-2 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:bg-blue-600 file:text-white hover:file:bg-blue-700"
        />
      </div>

      <div className="grid grid-cols-2 gap-4 mt-4">
        <div>
          <label className="block text-sm font-medium text-gray-500">Nivel</label>
          <p className="mt-1 text-lg font-semibold text-gray-800">{userProfile.level}</p>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-500">Puntos de Experiencia</label>
          <p className="mt-1 text-lg font-semibold text-gray-800">{userProfile.experience_points}</p>
        </div>
      </div>

      <button
        type="submit"
        disabled={saving}
        className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-lg transition duration-200"
      >
        Guardar Cambios
      </button>
    </form>
  );
}
