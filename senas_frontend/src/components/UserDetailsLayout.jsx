import React, { useEffect, useState } from 'react';

export default function UserDetailsLayout({ DJANGO_API_BASE_URL, makeAuthenticatedRequest, setErrorMessage, accessToken }) {
  const [perfil, setPerfil] = useState(null);
  const [formData, setFormData] = useState({});
  const [avatarPreview, setAvatarPreview] = useState(null);
  const [successMessage, setSuccessMessage] = useState('');

  useEffect(() => {
    async function fetchPerfil() {
      try {
        const response = await makeAuthenticatedRequest(`${DJANGO_API_BASE_URL}/api/usuarios/mi-perfil/`);
        const data = await response.json();

        setPerfil(data);
        setFormData({
          nombre: data.nombre || '',
          apellido: data.apellido || '',
          email: data.email || '',
          telefono: data.telefono || '',
          biografia: data.biografia || '',
          genero: data.genero || '',
          pais: data.pais || '',
          ciudad: data.ciudad || '',
          idioma_preferido: data.idioma_preferido || '',
          nivel_educativo: data.nivel_educativo || '',
          ocupacion: data.ocupacion || '',
        });
        setAvatarPreview(data.avatar);
      } catch (error) {
        console.error('Error al obtener perfil:', error);
        setErrorMessage('Error al obtener perfil');
      }
    }

    fetchPerfil();
  }, [DJANGO_API_BASE_URL, makeAuthenticatedRequest, setErrorMessage]);

  function handleInputChange(e) {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  }

  function handleAvatarChange(e) {
    const file = e.target.files[0];
    if (file) {
      setAvatarPreview(URL.createObjectURL(file));
      setFormData((prev) => ({ ...prev, avatar: file }));
    }
  }

  async function handleSubmit(e) {
    e.preventDefault();
    const data = new FormData();
    Object.entries(formData).forEach(([key, value]) => {
      if (value !== null && value !== undefined) {
        data.append(key, value);
      }
    });

    try {
      const response = await fetch(`${DJANGO_API_BASE_URL}/api/usuarios/mi-perfil/`, {
        method: 'PATCH',
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
        body: data,
      });

      if (!response.ok) {
        throw new Error('Error al guardar perfil');
      }

      const updated = await response.json();
      setPerfil(updated);
      setSuccessMessage('Perfil actualizado con éxito');
    } catch (error) {
      console.error('Error al guardar perfil:', error);
      setErrorMessage('Error al guardar perfil');
    }
  }

  if (!perfil) return <div className="text-gray-700">Cargando perfil...</div>;

  return (
    <div className="max-w-4xl mx-auto p-6 bg-white rounded-xl shadow-md">
      <h2 className="text-2xl font-bold mb-6">Editar Perfil</h2>

      {successMessage && <div className="mb-4 p-2 text-green-700 bg-green-100 rounded">{successMessage}</div>}

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-gray-600">Nombre</label>
            <input name="nombre" value={formData.nombre} onChange={handleInputChange} className="input" />
          </div>
          <div>
            <label className="block text-gray-600">Apellido</label>
            <input name="apellido" value={formData.apellido} onChange={handleInputChange} className="input" />
          </div>
          <div>
            <label className="block text-gray-600">Email</label>
            <input name="email" value={formData.email} onChange={handleInputChange} className="input" />
          </div>
          <div>
            <label className="block text-gray-600">Teléfono</label>
            <input name="telefono" value={formData.telefono} onChange={handleInputChange} className="input" />
          </div>
          <div>
            <label className="block text-gray-600">Género</label>
            <select name="genero" value={formData.genero} onChange={handleInputChange} className="input">
              <option value="">Selecciona</option>
              <option value="masculino">Masculino</option>
              <option value="femenino">Femenino</option>
              <option value="otro">Otro</option>
              <option value="no_decir">Prefiero no decir</option>
            </select>
          </div>
          <div>
            <label className="block text-gray-600">País</label>
            <input name="pais" value={formData.pais} onChange={handleInputChange} className="input" />
          </div>
          <div>
            <label className="block text-gray-600">Ciudad</label>
            <input name="ciudad" value={formData.ciudad} onChange={handleInputChange} className="input" />
          </div>
          <div>
            <label className="block text-gray-600">Idioma Preferido</label>
            <select name="idioma_preferido" value={formData.idioma_preferido} onChange={handleInputChange} className="input">
              <option value="">Selecciona</option>
              <option value="es-co">Español (Colombia)</option>
              <option value="en">English</option>
              <option value="es">Español (General)</option>
            </select>
          </div>
          <div>
            <label className="block text-gray-600">Nivel Educativo</label>
            <select name="nivel_educativo" value={formData.nivel_educativo} onChange={handleInputChange} className="input">
              <option value="">Selecciona</option>
              <option value="primaria">Primaria</option>
              <option value="secundaria">Secundaria</option>
              <option value="tecnico">Técnico</option>
              <option value="universitario">Universitario</option>
              <option value="posgrado">Posgrado</option>
              <option value="otro">Otro</option>
            </select>
          </div>
          <div>
            <label className="block text-gray-600">Ocupación</label>
            <input name="ocupacion" value={formData.ocupacion} onChange={handleInputChange} className="input" />
          </div>
        </div>

        <div>
          <label className="block text-gray-600">Biografía</label>
          <textarea name="biografia" value={formData.biografia} onChange={handleInputChange} className="input"></textarea>
        </div>

        <div className="flex items-center space-x-4">
          <div>
            <label className="block text-gray-600">Avatar</label>
            <input type="file" accept="image/*" onChange={handleAvatarChange} className="input" />
          </div>
          {avatarPreview && (
            <img src={avatarPreview} alt="Avatar preview" className="h-24 w-24 rounded-full object-cover border" />
          )}
        </div>

        <button type="submit" className="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700 transition">
          Guardar Cambios
        </button>
      </form>
    </div>
  );
}
